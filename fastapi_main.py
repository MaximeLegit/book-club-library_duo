from fastapi import FastAPI, HTTPException
from database import get_books_in_db


app = FastAPI()

# home
@app.get("/")
def home():
    return {"message" : "WelcomE to our LibrarY."}


# Display all available books from db
@app.get("/books")
def get_books():
    return get_books_in_db()


def find_book(id: int):
    books = get_books()
    for book in books:
        if book[0] == id:
            return book
    raise HTTPException(status_code=404, detail="Requested book not found.")


# find specific book
@app.get("/books/{book_id}")
def get_book(book_id: int):
    return (find_book(book_id))


# see all loans in db
@app.get("/loans")
def get_loans():
    #return get_loans()
    pass


# see all overdue loans in db
@app.get("/overdue_loans")
def get_overdue_loans():
    #return get_loans()
    pass


# get loan statistics in db, which book was read the most
@app.get("/most_borrowed_books")
def get_most_borrowed_books():
    #return get_loans()
    pass