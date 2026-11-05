from database import reset_db
from menu_handler import main_loop_user_input
from fastapi_main import start_api

if __name__ == "__main__":
    
    reset_db()

    api_process = start_api()
    try:
        main_loop_user_input()
    finally:
        api_process.terminate()