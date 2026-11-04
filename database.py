import sqlite3
from seed import insert_values

DB_PATH = "library.db"

# PUBLIC FUNCTIONS
def get_books_in_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select * from books")
    result = cursor.fetchall()
    conn.close()
    return result


def get_book(book_title, book_year : int | None = None):

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("select book_id from books where title = ? AND year is ?", (book_title, book_year))
        row = cursor.fetchone()
        return row[0]

    finally:
        conn.close()


def get_most_borrowed_books():
    """Return books with their loan count, most borrowed first."""

    # Connect to database
    conn = _get_connection()

    try:
        # Lets rows be read by column name, so we can use the names as dict key
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get book id, book title, and amount of times borrowed
        cursor.execute("""
SELECT COUNT(loans.book_id) AS times_loaned, books.book_id, title
FROM books
JOIN loans
ON books.book_id = loans.book_id
GROUP BY books.book_id
ORDER BY times_loaned DESC, title
LIMIT 5
""")
        rows = cursor.fetchall()

        # Converts all rows to dicts and returns them in a list
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_loans():
    """Return all loans as dicts with book title and member name"""

    # Connect to database
    conn = _get_connection()

    try:
        # Lets rows be read by column name, so we can use the names as dict key
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get loan, book title and member name
        cursor.execute("""
SELECT loan_id, title, first_name, last_name, loan_date, due_date, return_date
FROM loans
JOIN books
ON books.book_id = loans.book_id
JOIN members
ON members.member_id = loans.member_id""")
        rows = cursor.fetchall()

        # Converts all rows to dicts and returns them in a list
        return [dict(row) for row in rows]
    finally:
        conn.close()


def add_loan(loaned_book):

    conn = _get_connection()

    try:
        cursor = conn.cursor()

        member_id = _get_random_member()
        book_id = get_book(loaned_book["title"], loaned_book["year"])
        parameters = (member_id, book_id)

        cursor.execute("INSERT INTO loans (member_id, book_id) VALUES (?, ?)", (parameters))
        conn.commit()
        member = _get_member_name(book_id, member_id)
        print(f"The member {member[0]} {member[1]}, ID: {member_id} has loaned a book {loaned_book["title"]} with book ID {book_id}\
 The returned date for the book is:...\n")

    finally:
        conn.close()


def update_db(title: str, year: int | None = None, author_names: list[str] | None = None):
    """Add a book, with its authors, skipping anything that already exists."""
    book_id = _add_book(title, year)

    # If the book has authors

    if author_names is not None:
        for name in author_names:
            author_id = _add_author(name)
            _add_book_author(book_id, author_id)


def clear_data():
    """Rebuild the tables from schema.sql, without data."""

    # Rebuilds tables
    _rebuild_tables()


def reset_db():
    """Rebuild the tables from schema.sql and insert the seed data."""

    # Rebuilds tables
    _rebuild_tables()

    # Fill tables with seed data
    insert_values()


# PRIVATE FUNCTIONS
def _get_connection():
    """Open a connection to the database with foreign keys enabled."""

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def _get_random_member():
    try:
        conn = _get_connection()
        random_member_id = conn.execute("select member_id from members order by random() limit 1").fetchone()
    finally:
        conn.close()
    return random_member_id[0]


def _get_member_name(book_id, member_id):
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("select first_name, last_name from members "\
                       "join loans on members.member_id = loans.member_id "\
                       "where loans.book_id = ? AND members.member_id = ?", (book_id, member_id))
        return cursor.fetchone()
    finally:
        conn.close()


def _add_book(title, year):
    """Return the book_id for a book, add it first if it's new."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Checks if book already exists
        cursor.execute("SELECT book_id FROM books WHERE title = ? AND year IS ?", (title, year))
        row = cursor.fetchone()

        # If book exists
        if row is not None:

            # Return the id of the existing book
            return row[0]

        # Adds book to database
        cursor.execute("INSERT INTO books (title, year) VALUES (?, ?)", (title, year))
        conn.commit()

        # Returns the id of the new book
        return cursor.lastrowid
    finally:
        conn.close()


def _add_author(name):
    """Return the author_id for an author, add them first if they're new."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Checks if author already exists
        cursor.execute("SELECT author_id FROM authors WHERE name = ?", (name,))
        row = cursor.fetchone()

        # If author exists
        if row is not None:

            # Return the id of the existing author
            return row[0]

        # Adds author to database
        cursor.execute("INSERT INTO authors (name) VALUES (?)", (name,))
        conn.commit()

        # Returns the id of the new author
        return cursor.lastrowid
    finally:
        conn.close()


def _add_book_author(book_id, author_id):
    """Link a book to an author, if they aren't linked already."""

    # Checks if ids are null
    if book_id is None or author_id is None:
        raise ValueError("book_id and author_id are required")

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Adds book_author to database
        cursor.execute("INSERT OR IGNORE INTO book_authors (book_id, author_id) VALUES (?, ?)", (book_id, author_id))

        conn.commit()
    finally:
        conn.close()


def _rebuild_tables():
    """Drop and recreate all tables by running schema.sql."""

    # Connect to database
    conn = _get_connection()

    try:
        # Reads schema.sql to create tables.
        with open("schema.sql", encoding="utf-8") as file:
            conn.executescript(file.read())

    finally:
        conn.close()