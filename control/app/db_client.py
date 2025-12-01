import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from flask import current_app

def get_db_url():
    # Try to get from current_app config first, then os.getenv
    try:
        return current_app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv("DATABASE_URL")
    except RuntimeError:
        # If outside application context
        return os.getenv("DATABASE_URL")

@contextmanager
def get_db_connection():
    db_url = get_db_url()
    if not db_url:
        raise ValueError("DATABASE_URL is not set")

    conn = None
    try:
        conn = psycopg2.connect(db_url)
        conn.cursor_factory = RealDictCursor
        yield conn
    except psycopg2.Error as e:
        print(f"PostgreSQL connection error: {e}")
        if conn:
            conn.close()
        raise e
    finally:
        if conn:
            conn.close()
