from flask import Flask, jsonify, request
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
            customer_list.append(dict(c))
            
        return jsonify(customer_list)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

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
            conn.close()

@app.route('/api/customers/<int:customer_id>/points', methods=['POST'])
def update_points(customer_id):
    data = request.get_json()
    points = data.get('points', 0)
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        # Update points
        cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s", (points, customer_id))
        conn.commit()
        return jsonify({"message": "Loyalty points updated"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to update points"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT customer_id, name, email, loyalty_points FROM customers WHERE customer_id = %s"
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