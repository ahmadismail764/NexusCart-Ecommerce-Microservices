from flask import Flask, jsonify, request
import mysql.connector
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
    return jsonify({"status": "alive", "service": "inventory-service"})
@app.route('/api/inventory/products', methods=['GET'])
def get_products():
    """Get all products from inventory"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT product_id, product_name, quantity_available, unit_price FROM inventory"
        cursor.execute(query)
        products = cursor.fetchall()
        
        product_list = []
        for p in products:
            product_list.append({
                "product_id": p['product_id'],
                "product_name": p['product_name'],
                "stock": p['quantity_available'],
                "price": float(p['unit_price'])
            })
            
        return jsonify(product_list)
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/inventory/check_batch', methods=['POST'])
def check_inventory_batch():
    """Check stock for multiple products"""
    data = request.get_json()
    products = data.get('products', [])
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        results = []
        all_available = True
        
        for p in products:
            product_id = p.get('product_id')
            req_qty = p.get('quantity')
            
            cursor.execute("SELECT product_id, product_name, quantity_available, unit_price FROM inventory WHERE product_id = %s", (product_id,))
            item = cursor.fetchone()
            
            if item:
                is_avail = item['quantity_available'] >= req_qty
                if not is_avail:
                    all_available = False
                results.append({
                    "product_id": item['product_id'],
                    "available": is_avail,
                    "current_stock": item['quantity_available'],
                    "requested": req_qty,
                    "price": float(item['unit_price'])
                })
            else:
                all_available = False
                results.append({
                    "product_id": product_id,
                    "error": "Product not found",
                    "available": False
                })
                
        return jsonify({"items": results, "all_available": all_available})
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/inventory/update_stock', methods=['POST'])
def update_stock():
    """Update stock after order"""
    data = request.get_json()
    products = data.get('products', [])
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()
        conn.start_transaction()
        
        for p in products:
            product_id = p.get('product_id')
            qty = p.get('quantity')
            # Simply deduct, assuming check was done before
            cursor.execute("UPDATE inventory SET quantity_available = quantity_available - %s WHERE product_id = %s", (qty, product_id))
            
        conn.commit()
        return jsonify({"message": "Stock updated successfully"}), 200
        
    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Stock update failed"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/inventory/check/<int:product_id>', methods=['GET'])
def check_inventory(product_id):
    # Backward compatibility if needed, or simply keep it
    print(f"Checking inventory for Product ID: {product_id}")
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT product_id, product_name, quantity_available, unit_price FROM inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()
        
        if product:
            product_data = dict(product)
            return jsonify({
                "product_id": product_data['product_id'],
                "product_name": product_data['product_name'],
                "available": product_data['quantity_available'] > 0,
                "stock": product_data['quantity_available'],
                "price": float(product_data['unit_price'])
            })
        else:
            return jsonify({"error": "Product not found"}), 404
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
if __name__ == '__main__':
    app.run(port=5002, debug=True)