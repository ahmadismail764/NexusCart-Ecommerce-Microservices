from flask import Flask, jsonify
from flask import Flask, jsonify, request
import requests
import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_db_connection, close_db_connection

app = Flask(__name__)
ORDER_SERVICE_URL = "http://localhost:5001/api/orders"
CUSTOMER_SERVICE_URL = "http://localhost:5004/api/customers"
INVENTORY_SERVICE_URL = "http://localhost:5002/api/inventory/check"
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "notification-service"})
@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    data = request.get_json()
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400
        
    print(f"Processing notification for Order ID: {order_id}")
    try:
        order_resp = requests.get(f"{ORDER_SERVICE_URL}/{order_id}")
        if order_resp.status_code != 200:
            return jsonify({"error": "Failed to fetch order details"}), 400
        order_data = order_resp.json()
        customer_id = order_data['customer_id']
        items = order_data['items']
    except Exception as e:
        return jsonify({"error": f"Order Service Error: {e}"}), 500
    try:
        cust_resp = requests.get(f"{CUSTOMER_SERVICE_URL}/{customer_id}")
        if cust_resp.status_code != 200:
             return jsonify({"error": "Failed to fetch customer details"}), 400
        customer_data = cust_resp.json()
        email = customer_data['email']
        name = customer_data['name']
    except Exception as e:
        return jsonify({"error": f"Customer Service Error: {e}"}), 500
    product_names = []
    try:
        for item in items:
            p_id = item['product_id']
            inv_resp = requests.get(f"{INVENTORY_SERVICE_URL}/{p_id}")
            if inv_resp.status_code == 200:
                p_data = inv_resp.json()
                product_names.append(p_data.get('product_name', f"Product {p_id}"))
            else:
                product_names.append(f"Product {p_id}")
    except Exception as e:
        print(f"Warning: Failed to fetch product names: {e}")
    email_body = f"Hello {name},\n\nYour order #{order_id} has been confirmed!\n"
    email_body += f"Total Amount: ${order_data['total_amount']}\n"
    email_body += "Items:\n"
    for pname in product_names:
        email_body += f"- {pname}\n"
    
    print("---------------------------------------------------")
    print(f"SENDING EMAIL TO: {email}")
    print(email_body)
    print("---------------------------------------------------")
    conn = get_db_connection()
    if conn:
        cursor = None
        try:
            cursor = conn.cursor()
            query = "INSERT INTO notification_log (order_id, customer_id, notification_type, message) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (order_id, customer_id, "EMAIL", email_body))
            conn.commit()
        except Error as e:
            print(f"Error logging notification: {e}")
        finally:
            close_db_connection(conn, cursor)
    return jsonify({"status": "sent", "email": email}), 200
if __name__ == '__main__':
    app.run(port=5005, debug=True)
