from database import reset_db
from menu_handler import main_loop_user_input

if __name__ == "__main__":
    
    reset_db()

    main_loop_user_input()