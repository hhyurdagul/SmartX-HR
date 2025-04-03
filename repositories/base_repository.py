import sqlite3
from contextlib import contextmanager

DATABASE_NAME = "smartx_db.db" # Consider moving to a config file later

@contextmanager
def get_db_connection():
    """Provides a database connection using a context manager."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row # Access columns by name
        yield conn
    finally:
        if conn:
            conn.close()

# You could also define a BaseRepository class here if you want common methods,
# but for now, the connection manager might suffice.