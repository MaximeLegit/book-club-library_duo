import requests
from input_handler import select_book_from_api


class ApiHandler():

    url = "https://openlibrary.org/search.json"


    def open_lib_welcome_msg(self):
        print("\nHi! Welcome to our fantastic online library. Please type your search keyword(s) to display top 10 available books:\n")


    def make_clean_book_list(self, books):

        # Traverse raw data to extract bookId, title, authors and year and return it.
        print(f"{"ID":<3} {"Title":<65} {"Author(s)":<60} {"Published Year":<5}")
        clean_book_list = []
        book_id = 1
        for book in books["docs"]:
            authors = book.get("author_name", ["Unknown Author"])
            year = book.get("first_publish_year", "N/A")
            clean_book_list.append((book_id, book["title"], authors, year))
            print(f"{book_id:<3} {book['title']:<65} {", ".join(authors):<60} {year:<5}")
            book_id += 1
        return clean_book_list


    def search_books_in_open_library(self):

        self.open_lib_welcome_msg()
        while True:
            try:
                # api call. Get data based on input from open library.
                search_string = input().strip().lower()
                if search_string != "":
                    headers = {"User-Agent": "OpenLibraryStudentProject"}
                    search_parameters = {"q" : search_string, "limit" : 10}
                    open_library_books = requests.get(self.url, headers=headers, params=search_parameters, timeout=7).json()

                    if len(open_library_books["docs"]) == 0:
                        print("Your input gave 0 results, please provide another keyword\n")
                        continue
                    
                    # strip required data from the api call.
                    clean_book_list = self.make_clean_book_list(open_library_books)
                    if select_book_from_api(clean_book_list):
                        break
                    self.open_lib_welcome_msg()
                else:
                    print("\nYour input is an empty string, please provide a proper keyword.")
            except requests.exceptions.Timeout:
                print("Timed out. Please try again.")
