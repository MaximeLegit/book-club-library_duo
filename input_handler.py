from database import update_db, add_loan

def get_book_via_id(clean_book_list, user_input):
    for id, title, authors, year in clean_book_list:
        if id == user_input:
            return {"id" : id, "title" : title, "year" : year, "authors" : authors}
    return None

def select_book_from_api(clean_book_list):
    print("\nWould you like to book any of the displayed books? If yes, please specify ID, if not, please type 'N'\n")
    user_input = input().strip()
    
    if user_input.isdigit():

        # Obtain the book based on ID
        loaned_book = get_book_via_id(clean_book_list, int(user_input))
        if loaned_book is None:
            print("No book with that ID.")
            return

        # refine to use as args
        if loaned_book["year"] == "N/A":
            update_db(loaned_book["title"], author_names = loaned_book["authors"])
        else:
            update_db(loaned_book["title"], loaned_book["year"], loaned_book["authors"])

        # Proceed to adding loan information for the book into the database.
        add_loan(loaned_book)

    else:
        print("For now, no book.")
        return