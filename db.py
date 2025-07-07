# db.py
import sqlite3
import os

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, "mcp_ecommerce.db")

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
