from flask import Flask, request, jsonify
import requests
from mysql.connector import Error

# Import utils directly (since they are in the same backend folder)
from utils import get_db_connection, close_db_connection

app = Flask(__name__)

# Service URLs
INVENTORY_SERVICE_BATCH_URL = "http://localhost:5002/api/inventory/check_batch"

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "pricing-service"})

@app.route('/api/pricing/calculate', methods=['POST'])
def calculate_price():
    data = request.get_json()
    products = data.get('products', [])
    
    # Basic Validation
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
        
        # 1. BATCH CALL: Fetch all product prices at once from Inventory
        # We send the list of products to the inventory service to check availability and get base prices
        inventory_payload = {"products": products}
        
        try:
            # Note: Port 5002 for Inventory Service
            inv_response = requests.post(
                INVENTORY_SERVICE_BATCH_URL, 
                json=inventory_payload
            )
            
            if inv_response.status_code != 200:
                 raise Exception("Failed to fetch batch inventory data")
            
            inv_data = inv_response.json()
            inventory_items = inv_data.get('items', [])
            
            # Create a Map for O(1) lookup: product_id -> price 
            price_map = {item['product_id']: item['price'] for item in inventory_items if 'price' in item}
            
        except Exception as e:
            return jsonify({"error": f"Inventory Service Error: {str(e)}"}), 500

        # 2. Get Tax Rate (Single DB call)
        cursor.execute("SELECT tax_rate FROM tax_rates WHERE region = 'US'")
        tax_record = cursor.fetchone()
        tax_rate = float(tax_record['tax_rate']) if tax_record else 0.0 # type: ignore
        
        # 3. Process Logic locally using the price map
        for item in products:
            p_id = item['product_id']
            qty = item['quantity']
            
            if p_id not in price_map:
                return jsonify({"error": f"Product {p_id} not found in Inventory"}), 404
            
            base_price = price_map[p_id]
            
            # Get discount rules for this specific product
            cursor.execute("SELECT discount_percentage, min_quantity FROM pricing_rules WHERE product_id = %s", (p_id,))
            rules = cursor.fetchall()
            
            discount_percent = 0.0
            for rule in rules:
                if qty >= rule['min_quantity']: # type: ignore
                    if float(rule['discount_percentage']) > discount_percent: # type: ignore
                        discount_percent = float(rule['discount_percentage']) # type: ignore
            
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
        close_db_connection(conn, cursor)

if __name__ == '__main__':
    app.run(port=5003, debug=True)