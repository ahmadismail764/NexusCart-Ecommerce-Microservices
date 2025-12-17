from flask import Flask, request, jsonify
import mysql.connector
import requests
from mysql.connector import Error
app = Flask(__name__)
ORDER_SERVICE_URL = "http://localhost:5001/api/orders/create"
PRICING_SERVICE_URL = "http://localhost:5003/api/pricing/calculate"
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
    return jsonify({"status": "alive", "service": "order-service"})
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT order_id, customer_id, total_amount, status FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
            
        cursor.execute("SELECT product_id, quantity, price_at_purchase FROM order_items WHERE order_id = %s", (order_id,))
        items = cursor.fetchall()
        
        order_data = dict(order)
        order_data['items'] = [dict(item) for item in items]
        
        return jsonify(order_data)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
@app.route('/api/orders/create', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_id = data.get('customer_id')
    products = data.get('products', [])
    
    if not customer_id or not products:
        return jsonify({"error": "Missing customer_id or products"}), 400
    for p in products:
        if 'product_id' not in p or 'quantity' not in p:
             return jsonify({"error": "Invalid product data"}), 400
        if int(p['quantity']) <= 0:
             return jsonify({"error": "Quantity must be positive"}), 400
    try:
        pricing_response = requests.post(
            PRICING_SERVICE_URL,
            json={"products": products}
        )
        if pricing_response.status_code != 200:
            return jsonify({"error": "Failed to calculate price"}), 400
            
        pricing_data = pricing_response.json()
        total_amount = pricing_data['total_amount']
        itemized_items = pricing_data['items']
        
    except Exception as e:
        return jsonify({"error": f"Pricing Service Error: {str(e)}"}), 500
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        conn.start_transaction()
        order_query = "INSERT INTO orders (customer_id, total_amount, status) VALUES (%s, %s, 'CONFIRMED')"
        cursor.execute(order_query, (customer_id, total_amount))
        order_id = cursor.lastrowid
        item_query = "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)"
        
        for item in itemized_items:
            effective_unit_price = item['final_price'] / item['quantity']
            
            cursor.execute(item_query, (
                order_id, 
                item['product_id'], 
                item['quantity'], 
                effective_unit_price
            ))
        conn.commit()
        
        try:
             requests.post("http://localhost:5005/api/notifications/send", json={"order_id": order_id})
        except Exception as e:
             print(f"Warning: Failed to trigger notification service: {e}")
        
        return jsonify({
            "message": "Order created successfully", 
            "order_id": order_id,
            "total_amount": total_amount,
            "status": "CONFIRMED"
        }), 201
    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Database transaction failed"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
if __name__ == '__main__':
    app.run(port=5001, debug=True)