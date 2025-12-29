from flask import Flask, jsonify, request
import requests
from mysql.connector import Error
from utils import get_db_connection, close_db_connection

app = Flask(__name__)

# Service URLs
ORDER_SERVICE_URL = "http://localhost:5001/api/orders"
CUSTOMER_SERVICE_URL = "http://localhost:5004/api/customers"
# Uses the Single-Item check endpoint (GET) we kept for compatibility
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
    
    # 1. Get Order Details (to find customer_id and items)
    try:
        order_resp = requests.get(f"{ORDER_SERVICE_URL}/{order_id}")
        if order_resp.status_code != 200:
            return jsonify({"error": "Failed to fetch order details"}), 400
        order_data = order_resp.json()
        customer_id = order_data['customer_id']
        items = order_data['items']
    except Exception as e:
        return jsonify({"error": f"Order Service Error: {e}"}), 500

    # 2. Get Customer Details (to find email and name)
    try:
        cust_resp = requests.get(f"{CUSTOMER_SERVICE_URL}/{customer_id}")
        if cust_resp.status_code != 200:
             return jsonify({"error": "Failed to fetch customer details"}), 400
        customer_data = cust_resp.json()
        email = customer_data['email']
        name = customer_data['name']
    except Exception as e:
        return jsonify({"error": f"Customer Service Error: {e}"}), 500

    # 3. Get Product Names (to make the email look nice)
    product_names = []
    try:
        for item in items:
            p_id = item['product_id']
            # Calls the GET /check/<id> endpoint
            inv_resp = requests.get(f"{INVENTORY_SERVICE_URL}/{p_id}")
            if inv_resp.status_code == 200:
                p_data = inv_resp.json()
                product_names.append(p_data.get('product_name', f"Product {p_id}"))
            else:
                product_names.append(f"Product {p_id}")
    except Exception as e:
        print(f"Warning: Failed to fetch product names: {e}")

    # 4. Construct Message
    email_body = f"Hello {name},\n\nYour order #{order_id} has been confirmed!\n"
    email_body += f"Total Amount: ${order_data['total_amount']}\n"
    email_body += "Items:\n"
    for pname in product_names:
        email_body += f"- {pname}\n"
    
    # 5. Simulate Sending (Print to Console)
    print("---------------------------------------------------")
    print(f"SENDING EMAIL TO: {email}")
    print(email_body)
    print("---------------------------------------------------")
    
    # 6. Log to Database
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