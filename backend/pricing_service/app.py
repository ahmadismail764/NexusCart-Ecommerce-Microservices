from flask import Flask, request, jsonify
import mysql.connector
import requests
from mysql.connector import Error

app = Flask(__name__)

INVENTORY_SERVICE_URL = "http://localhost:5002/api/inventory/check"

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
    return jsonify({"status": "alive", "service": "pricing-service"})

@app.route('/api/pricing/calculate', methods=['POST'])
def calculate_price():
    data = request.get_json()
    products = data.get('products', [])
    
    for p in products:
        if 'product_id' not in p or 'quantity' not in p:
             return jsonify({"error": "Invalid product data"}), 400
        if int(p['quantity']) <= 0:
             return jsonify({"error": "Quantity must be positive"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
        
    total_amount = 0.0
    itemized_list = []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT tax_rate FROM tax_rates WHERE region = 'US'")
        tax_record = cursor.fetchone()
        tax_rate = float(tax_record['tax_rate']) if tax_record else 0.0
        
        for item in products:
            p_id = item['product_id']
            qty = item['quantity']
            
            try:
                response = requests.get(f"{INVENTORY_SERVICE_URL}/{p_id}")
                if response.status_code != 200:
                    raise Exception(f"Product {p_id} not found in Inventory")
                
                inv_data = response.json()
                base_price = inv_data['price']
            except Exception as e:
                return jsonify({"error": str(e)}), 400

            cursor.execute("SELECT discount_percentage, min_quantity FROM pricing_rules WHERE product_id = %s", (p_id,))
            rules = cursor.fetchall()
            
            discount_percent = 0.0
            for rule in rules:
                if qty >= rule['min_quantity']: 
                    if float(rule['discount_percentage']) > discount_percent: 
                        discount_percent = float(rule['discount_percentage']) 
            
            gross_price = base_price * qty
            discount_amount = gross_price * (discount_percent / 100.0)
            price_after_discount = gross_price - discount_amount
            tax_amount = price_after_discount * tax_rate
            final_line_price = price_after_discount + tax_amount
            
            total_amount += final_line_price
            
            itemized_list.append({
                "product_id": p_id,
                "quantity": qty,
                "base_price": base_price,
                "discount_percent": discount_percent,
                "tax_rate": tax_rate,
                "final_price": round(final_line_price, 2)
            })
            
        return jsonify({
            "total_amount": round(total_amount, 2),
            "currency": "USD",
            "items": itemized_list
        })

    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    app.run(port=5003, debug=True)
