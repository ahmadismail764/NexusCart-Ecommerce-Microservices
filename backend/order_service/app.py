from flask import Flask, request, jsonify
import mysql.connector
import requests
from mysql.connector import Error
app = Flask(__name__)
INVENTORY_SERVICE_CHECK_URL = "http://localhost:5002/api/inventory/check_batch"
INVENTORY_SERVICE_UPDATE_URL = "http://localhost:5002/api/inventory/update_stock"
CUSTOMER_SERVICE_URL = "http://localhost:5004/api/customers"
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
        
    # 1. Check Inventory
    try:
        inv_response = requests.post(INVENTORY_SERVICE_CHECK_URL, json={"products": products})
        if inv_response.status_code != 200:
             return jsonify({"error": "Inventory check failed"}), 500
        
        inv_data = inv_response.json()
        if not inv_data.get('all_available'):
            return jsonify({"error": "Some items are out of stock", "details": inv_data.get('items')}), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Inventory Service unreachable: {e}"}), 503

    # 2. Calculate Price
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
        
        # 3. Update Stock
        try:
             requests.post(INVENTORY_SERVICE_UPDATE_URL, json={"products": products})
        except Exception as e:
             print(f"Warning: Failed to update stock: {e}")
             # In a real system, you might rollback or have a compensation transaction
             
        # 4. Update Loyalty Points (1 point per $10)
        try:
            points = int(total_amount / 10)
            if points > 0:
                requests.post(f"{CUSTOMER_SERVICE_URL}/{customer_id}/points", json={"points": points})
        except Exception as e:
             print(f"Warning: Failed to update loyalty points: {e}")

        # 5. Send Notification
        try:
             requests.post("http://localhost:5005/api/notifications/send", json={"order_id": order_id})
        except Exception as e:
             print(f"Warning: Failed to trigger notification service: {e}")
        
        return jsonify({
            "message": "Order created successfully", 
            "order_id": order_id,
            "total_amount": total_amount,
            "points_earned": int(total_amount / 10),
            "status": "CONFIRMED"
        }), 201
    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Database transaction failed"}), 500
    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Database transaction failed"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
@app.route('/api/orders/customer/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch orders
        cursor.execute("SELECT order_id, total_amount, status, CAST(order_date AS CHAR) as order_date FROM orders WHERE customer_id = %s ORDER BY order_date DESC", (customer_id,))
        orders = cursor.fetchall()
        
        results = []
        for order in orders:
            o_data = dict(order)
            # Optional: fetch items for each order if needed, but summary is usually enough for history list
            results.append(o_data)
            
        return jsonify(results)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(port=5001, debug=True)