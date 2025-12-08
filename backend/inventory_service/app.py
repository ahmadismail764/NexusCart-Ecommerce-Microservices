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
    return jsonify({"status": "alive", "service": "inventory-service"})

@app.route('/api/inventory/check/<int:product_id>', methods=['GET'])
def check_inventory(product_id):
    print(f"Checking inventory for Product ID: {product_id}")
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT product_id, quantity_available, unit_price FROM inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        
        if product:
            return jsonify({
                "product_id": product['product_id'],
                "available": product['quantity_available'] > 0,
                "stock": product['quantity_available'],
                "price": float(product['unit_price'])
            })
        else:
            return jsonify({"error": "Product not found"}), 404
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
