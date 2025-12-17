from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)
def get_db_connection():
    """Connect to the MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ecommerce_system',
            user='ecommerce_user',
            password='secure_password'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "customer-service"})
@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT customer_id, name, email FROM customers WHERE customer_id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()
        
        if customer:
            return jsonify(dict(customer))
        else:
            return jsonify({"error": "Customer not found"}), 404
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
if __name__ == '__main__':
    app.run(port=5004, debug=True)