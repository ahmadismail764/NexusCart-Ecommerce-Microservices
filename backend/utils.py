import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.config'))

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_db_connection(connection, cursor=None):
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Generic function to execute database queries"""
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = None
    result = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            result = {'lastrowid': cursor.lastrowid, 'rowcount': cursor.rowcount}
        elif fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            # For updates/inserts without commit (part of transaction) or just execution
            result = True 
            
    except Error as e:
        print(f"Database Error: {e}")
        return None
    finally:
        # Only close if we are not in a transaction that needs manual handling?
        # For simplicity in this helper, we close. 
        # If you need transactions across multiple calls, you wouldn't use this helper for individual steps.
        close_db_connection(conn, cursor)
        
    return result