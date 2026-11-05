from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database

app = FastAPI()

# Home.
@app.get("/")
def home():
    return {"message" : "WelcomE to our LibrarY."}


# Display all available books from db
@app.get("/books")
def get_books():
    return database.get_books()


# Find specific book.
@app.get("/books/{book_id}")
def get_book(book_id: int):
    books = get_books()
    for book in books:
        if book[0] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Requested book not found.")


# See all loans in db.
@app.get("/loans")
def get_loans():
    return database.get_loans()


# See all overdue loans in db.
@app.get("/overdue_loans")
def get_overdue_loans():
    #return get__overdue_loans()
    pass


# Get loan statistics in db, which book was read the most.
@app.get("/most_borrowed_books")
def get_most_borrowed_books():
    return database.get_most_borrowed_books()


# Pydantic requirement.
class Book(BaseModel):
    title : str
    year : int
    author_names : list[str]

class BookUpdate(BaseModel):
    title : str | None = None
    year : int | None = None


# Add a book.
@app.post("/books", status_code=201)
def add_book(book: Book):

    # Call update DB via the given format to add a book.
    database.update_db(book.title, book.year, book.author_names)
    return book


# Update a book based on the entered ID.
@app.put("/books/{book_id}")
def update_a_book(book_id : int, book_update: BookUpdate):

    if database.update_book(book_id, book_update.title, book_update.year):
        return {"message" : "Book updated"}
    else:
        return {"message" : "The ID you have entered is not an existing one."}


# Purge a book.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id : int):
    selected_book = get_book(book_id)
    # database.delete_book(selected_book)