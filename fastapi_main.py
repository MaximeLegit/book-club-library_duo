from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database, os, subprocess, sys, sqlite3

app = FastAPI()


# Function to run fastapi concurrently with main.
def start_api():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    kwargs = {}
    # Windows based check.
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    # Linux based check.
    else:
        kwargs["stdout"] = open(os.path.join(dir_path, "api.log"), "w")
        kwargs["stderr"] = subprocess.STDOUT
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return subprocess.Popen(
        [sys.executable, "-m", "fastapi", "run", "fastapi_main.py"],
        cwd=dir_path,
        **kwargs
    )


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


class BookPatch(BaseModel):
    title : str | None = None
    year  : int | None = None


class BookUpdate(BaseModel):
    title : str
    year  : int


# Add a book.
@app.post("/books", status_code=201)
def add_book(book: Book):

    # Call update DB via the given format to add a book.
    database.update_db(book.title, book.year, book.author_names)
    return book


# Update a book based on the entered ID.
@app.put("/books/{book_id}")
def update_a_book(book_id : int, book_update: BookUpdate):
    try:
        if database.update_book(book_id, book_update.title, book_update.year):
            return {"message" : "Book updated"}
        else:
            raise HTTPException(status_code=404, detail="The ID you have entered is not valid.")
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="You must enter valid 'title' and 'year' values.")


# Purge a book.
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id : int):
    book_to_delete = get_book(book_id)
    try:
        if database.delete_book(book_id):
            return {"message" : f"Book {book_to_delete} has been deleted."}
        else:
            raise HTTPException(status_code=404, detail="WITHIN IF: Book cannot be deleted, it has existing loans, or something.")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="EXCEPTION: Book cannot be deleted, it has existing loans, or something..")


# Update a book based on the entered ID, all fields are a must
@app.patch("/books/{book_id}")
def patch_book(book_id : int, book_patch : BookPatch):
    try:
        if database.update_book(book_id, book_patch.title, book_patch.year):
            return {"message" : "Book updated"}
        else:
            # cater for non existing ID.
            raise HTTPException(status_code=404, detail="The ID you have entered is not valid.")
        
    except sqlite3.IntegrityError:
        # on error, trying to ONLY put one of the required values, continue, do not crash.
        raise HTTPException(status_code=400, detail="You have entered values that cannot be parsed. Please try again.")
