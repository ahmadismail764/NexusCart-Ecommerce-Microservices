from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_db_connection, close_db_connection

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "customer-service"})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT customer_id, name, email FROM customers"
        cursor.execute(query)
        customers = cursor.fetchall()
        
        customer_list = []
        for c in customers:
            customer_list.append(dict(c)) # type: ignore
            
        return jsonify(customer_list)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    
    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO customers (name, email) VALUES (%s, %s)"
        cursor.execute(query, (name, email))
        conn.commit()
        
        customer_id = cursor.lastrowid
        return jsonify({"message": "Customer created", "customer_id": customer_id}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to create customer"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            close_db_connection(conn, customer_id)


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT customer_id, name, email, loyalty_points FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        
        if customer:
            return jsonify(dict(customer)) # type: ignore
        else:
            return jsonify({"error": "Customer not found"}), 404
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        close_db_connection(conn, cursor)

@app.route('/api/customers/<int:customer_id>/points', methods=['POST'])
def update_loyalty(customer_id):
    data = request.get_json()
    points = data.get('points', 0)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s", (points, customer_id))
        conn.commit()
        return jsonify({"message": "Loyalty points updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        close_db_connection(conn, cursor)

if __name__ == '__main__':
    app.run(port=5004, debug=True)