import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL')

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
    
    def execute_query(self, query, params=None):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_insert(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return cur.rowcount

# For reference, already created table in the database
def create_tables():
    db = PostgresDB()
    db.execute_query("""
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        device VARCHAR(255),
        event_type VARCHAR(255),
        event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        event_location VARCHAR(255),
        time_to_stop INTEGER
    )
    """)