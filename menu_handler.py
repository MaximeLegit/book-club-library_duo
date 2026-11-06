import sys
from api_handler import ApiHandler
from database import get_books, return_book

def print_local_books():
    print(f"{"ID":<3} {"Title":<25} {"Published Year":<5}")
    books = get_books()
    for book in books:
        year = book[2] if book[2] is not None else "N/A"
        print(f"{book[0]:<3} {book[1]:<25} {year:<5}")


def view_book_details(book):
    """View the selected book."""
    # Show this book's title, published year, authors, and whether it is currently on loan.
    pass


def borrow_book(book):
    """Borrow the selected book."""
    # Ask which member is borrowing, then save a new loan with a loan date and a due date.
    pass


def return_selected_book(book):
    if return_book(book[0]):
        print(f"\nBook {book[1]} has been returned.")
    else:
        print(f"\nBook {book[1]} is not on loan, it has been returned already.")


def edit_book(book):
    """Edit the selected book."""
    # Update this book's title, published year, or linked authors.
    pass


def remove_book(book):
    """Remove the selected book."""
    # Delete this book and its author links when it has no open loan.
    pass


def main_loop_welcome_msg():
    print("\n\nWelcome to our digital library. Please choose if you wish to traverse our local or online library." \
    "\nType 1 to traverse Local Library" \
    "\nType 2 to traverse Online Library" \
    "\nOR type quit to quit")


def main_loop_user_input():
    # This is the function to handle main user loop choices.
    print_out = True
    while True:
        if print_out:
            main_loop_welcome_msg()
        
        choice = input().lower()
        if choice == "1":
            print_out = True
            print("Here are the contents of our local library:\n")
            print_local_books()

            # Next function call will move the user to handle choices for our internal library.
            print("\nIf you wish to select any of the displayed books, please type in the book's ID:")
            handle_local_books_choices()
        elif choice == "2":
            # Next function will move the user to handle choices for our online library.
            print_out = True
            api_obj = ApiHandler()
            api_obj.search_books_in_open_library()
        elif choice == "quit":
            sys.exit()
        else:
            print("Unrecognized input. Please type in a number 1 OR 2 OR quit.")
            print_out = False
            continue


def handle_local_books_choices():
    """Offer every action available for one book from the local library list."""

    # get all books from our local database
    local_library_books = get_books()
    while True:

        choice = input().lower()
        if not choice.isdigit():
            print("Unrecognized input. Please type in an ID from the displayed books above.")
            continue

        book_id = int(choice)
        selected = None
        for book in local_library_books:
            if book[0] == book_id:
                selected = book
                break
 
        if selected is None:
            print("\nNo book with requested ID. Please type again:\n")
            continue

        # These options are the actions on a book that is already displayed.

        id, title, year = selected
        year = "N/A" if year is None else year

        print(f"\nSelected: {id} {title} ({year})")
        print("What would you like to do?\n")
        print("1. View details")
        print("2. Borrow")
        print("3. Return")
        print("4. Edit")
        print("5. Remove")
        print("6. Back")

        action = input().strip()

        # Each number calls one placeholder. The sentence is the text under that function's name  (_doc_ attribute).
        if action == "1":
            print(f"\nView details: {view_book_details.__doc__}")
            view_book_details(selected)
        elif action == "2":
            print(f"\nBorrow: {borrow_book.__doc__}")
            borrow_book(selected)
        elif action == "3":
            return_selected_book(selected)
            break
        elif action == "4":
            print(f"\nEdit: {edit_book.__doc__}")
            edit_book(selected)
        elif action == "5":
            print(f"\nRemove: {remove_book.__doc__}")
            remove_book(selected)
        elif action == "6":
            break
        else:
            print("\nPlease choose one of the options above.")
