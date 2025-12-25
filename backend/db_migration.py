
import mysql.connector
from mysql.connector import Error

def migrate():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ecommerce_system',
            user='ecommerce_user',
            password='secure_password'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            try:
                # Check if column exists
                cursor.execute("SHOW COLUMNS FROM customers LIKE 'loyalty_points'")
                result = cursor.fetchone()
                if not result:
                    print("Adding loyalty_points column...")
                    cursor.execute("ALTER TABLE customers ADD COLUMN loyalty_points INT DEFAULT 0")
                    connection.commit()
                    print("Column added successfully.")
                else:
                    print("Column loyalty_points already exists.")
            except Error as e:
                print(f"Error during migration: {e}")
            finally:
                cursor.close()
                connection.close()
    except Error as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    migrate()
