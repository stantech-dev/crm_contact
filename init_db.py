# init_db.py
from crm import create_table

if __name__ == "__main__":
    create_table()
    print("Database initialized — dealbook.db is ready with an empty 'dealbook' table.")