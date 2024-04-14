"""
The DBManager class is responsible for handling all database connections and transactions 
within the fitness club management system. It provides a static method to establish and manage database connections using a context 
manager, ensuring that resources are properly managed and connections are safely closed.

Key Functionalities:
- connection(): A context manager that creates and yields a PostgreSQL connection. It ensures the connection is closed after use, and handles any exceptions during the connection lifecycle. This method improves reliability and ease of database operations throughout the system.
"""

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
                
                
