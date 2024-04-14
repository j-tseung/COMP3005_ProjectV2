
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class DBManager:
    @staticmethod
    @contextmanager
    def connection():
        conn = None
        try:
            conn = psycopg2.connect(
                dbname='COMP3005_ProjectV2',
                user='postgres',
                password='postgres',
                host='localhost',
                cursor_factory=RealDictCursor  # Allows fetching rows as dictionaries
            )
            yield conn
        except psycopg2.Error as e:
            print(f"Database connection failed: {e}")
        finally:
            if conn and not conn.closed:  # Check for whether the connection is closed
                conn.close()
                
                
