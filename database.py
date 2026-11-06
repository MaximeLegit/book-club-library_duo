import sqlite3
from seed import insert_values
from datetime import date

DB_PATH = "library.db"

# PUBLIC FUNCTIONS
def get_books():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select * from books")
    result = cursor.fetchall()
    conn.close()
    return result


def get_book(book_title, book_year : int | None = None):
    """Return a book as a dict, or None if it doesn't exist."""

    # Connect to database
    conn = _get_connection()
    try:

        # Lets rows be read by column name, so we can use the names as dict key
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get book whose title and year match the function arguments
        cursor.execute("select * from books where title = ? AND year is ?", (book_title, book_year))
        row = cursor.fetchone()

        if row is None:
            return None

        # Converts row to dict and returns it
        return dict(row)
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


def book_has_open_loan(book_id):
    """Return True if the book has an open loan, else False."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Get open loan count for book that matches id input
        cursor.execute("""
SELECT COUNT(*)
FROM loans
WHERE book_id = ? AND return_date IS NULL
""",
(book_id,))

        # Returns True if open loan was found, else False
        if cursor.fetchone()[0] > 0:
            return True
        else:
            return False
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


def get_overdue_loans():
    """Return all overdue loans as dicts with book title and member name"""

    # Connect to database
    conn = _get_connection()

    try:
        # Lets rows be read by column name, so we can use the names as dict key
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get overdue loan, book title and member
        cursor.execute("""
SELECT loan_id, title, first_name, last_name, loan_date, due_date, return_date
FROM loans
JOIN books
ON books.book_id = loans.book_id
JOIN members
ON members.member_id = loans.member_id
WHERE return_date IS NULL AND due_date < DATE('now')
""")
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
        book_id = get_book(loaned_book["title"], loaned_book["year"])["book_id"]
        parameters = (member_id, book_id)

        cursor.execute("INSERT INTO loans (member_id, book_id) VALUES (?, ?)", (parameters))
        conn.commit()
        member = _get_member_name(book_id, member_id)
        print(f"The member {member[0]} {member[1]}, ID: {member_id} has loaned a book {loaned_book["title"]} with book ID {book_id}\
 The returned date for the book is:...\n")

    finally:
        conn.close()


def delete_loan(loan_id):
    """Delete a loan, return True if it was deleted, else False."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor =  conn.cursor()

        # Deletes loan that has the same id as input
        cursor.execute("""
DELETE
FROM loans
WHERE loan_id = ?
""",
(loan_id,))
        conn.commit()

        # Returns True if loan was found and deleted, else False
        if cursor.rowcount == 1:
            return True
        else:
            return False
    finally:
        conn.close()


def delete_returned_loans(book_id):
    """Delete a book's returned loan(s), return True if it was deleted."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Deletes a loan that has the same book id as input
        cursor.execute("""
DELETE
FROM
loans
WHERE book_id = ? AND return_date NOT NULL
""",
(book_id,))
        conn.commit()

        # Returns True if loan was found and deleted, else False
        if cursor.rowcount > 0:
            return True
        else:
            return False

    finally:
        conn.close()


def delete_author(author_id):
    """Delete an author, return True if they were deleted, else False."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Deletes author that has the same id as input
        cursor.execute("""
DELETE
FROM
authors
WHERE author_id = ?
""",
(author_id,))
        conn.commit()

        # Returns True if author was found and deleted, else False
        if cursor.rowcount > 0:
            return True
        else:
            return False

    # If author is still linked to a book and the foreign key blocks the delete
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def update_book(book_id, title=None, year=None):
    """Update a book's title or year, return True if success, else False"""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

    # Update a book's title or year
        cursor.execute("""
    UPDATE books
    SET title = COALESCE(?, title), year = COALESCE(?, year)
    WHERE book_id = ?
    """,
    (title, year, book_id))
        conn.commit()

        # Returns True if book was updated, else False
        if cursor.rowcount == 1:
            return True
        else:
            return False
    finally:
        conn.close()


def delete_book_author(book_id):
    """Delete book_author(s), return True if any was deleted, else False."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Deletes book_author that has the same book id as input
        cursor.execute("""
DELETE
FROM book_authors
WHERE book_id = ?
""",
(book_id,))
        conn.commit()

        # Returns True if book_author was found, else False
        if cursor.rowcount > 0:
            return True
        else:
            return False
    finally:
        conn.close()


def delete_book(book_id):  # author links must be deleted first
    """Delete a book, return True if it was deleted, else False."""

    # Connect to database
    conn = _get_connection()

    try:
        cursor = conn.cursor()

        # Deletes a book that has the same id as input
        cursor.execute("""
DELETE
FROM
books
WHERE book_id = ?
""",
(book_id,))
        conn.commit()

        # Returns True if book was found and deleted, else False
        if cursor.rowcount > 0:
            return True
        else:
            return False

    # If book still had loans or linked to a author and the foreign key blocks the delete
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def delete_book_and_links(book_id):
    """Delete a book and its links, return True if deleted, else False"""

    # If book has no active loan
    if not book_has_open_loan(book_id):
        delete_returned_loans(book_id)
        delete_book_author(book_id)

        # Returns True if book was deleted, else False
        return delete_book(book_id)


def update_db(title: str, year: int | None = None, author_names: list[str] | None = None):
    """Add a book, with its authors, skipping anything that already exists."""
    book_id = _add_book(title, year)

    # If the book has authors

    if author_names is not None:
        for name in author_names:
            author_id = _add_author(name)
            _add_book_author(book_id, author_id)


def return_book(book_id):

    conn = _get_connection()
    try:
        result = conn.execute(
        """
        SELECT loans.loan_id FROM books
        LEFT JOIN loans ON loans.book_id = books.book_id
        AND loans.return_date IS NULL
        WHERE books.book_id = ?
        """,
        (book_id,),
        ).fetchone()

        # if we send sketchy id, return false.
        if result is None:
            return False

        # get the loan id to use it later on.
        loan_id = result[0]

        # no open loan and already returned, send back false.
        if loan_id is None:
            return False

        # base cse: open loan found, update db, send back true.
        conn.execute(
            "UPDATE loans SET return_date = date('now') WHERE loan_id = ? AND return_date IS NULL",
            (loan_id,)
        )
        conn.commit()
        return True
    finally:
        conn.close()


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