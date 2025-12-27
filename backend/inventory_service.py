from flask import Flask, jsonify, request
from mysql.connector import Error
from utils import get_db_connection, close_db_connection

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "inventory-service"})

@app.route('/api/inventory/products', methods=['GET'])
def get_products(): 
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT product_id, product_name, quantity_available, unit_price FROM inventory WHERE quantity_available > 0"
        cursor.execute(query)
        products = cursor.fetchall()
        
        product_list = []
        for prod in products:
            product_list.append({
                "product_id": prod['product_id'], # type: ignore
                "product_name": prod['product_name'], # type: ignore
                "stock": prod['quantity_available'], # type: ignore
                "price": float(prod['unit_price']) # type: ignore
            })
            
        return jsonify(product_list)
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        close_db_connection(conn, cursor)

@app.route('/api/inventory/check_batch', methods=['POST'])
def check_inventory_batch():
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
                is_avail = item['quantity_available'] >= req_qty # type: ignore
                if not is_avail:
                    all_available = False
                results.append({
                    "product_id": item['product_id'], # type: ignore
                    "available": is_avail, 
                    "current_stock": item['quantity_available'], # type: ignore
                    "requested": req_qty, 
                    "price": float(item['unit_price']) # type: ignore
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
        close_db_connection(conn, cursor)

@app.route('/api/inventory/update_stock', methods=['PUT'])
def update_stock():
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
            cursor.execute("UPDATE inventory SET quantity_available = quantity_available - %s WHERE product_id = %s", (qty, product_id))
            
        conn.commit()
        return jsonify({"message": "Stock updated successfully"}), 200
        
    except Error as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Stock update failed"}), 500
    finally:
        close_db_connection(conn, cursor)


@app.route('/api/inventory/check', methods=['POST'])
def check_inventory(product_id):
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
            product_data = dict(product) # type: ignore
            return jsonify({
                "product_id": product_data['product_id'], # type: ignore
                "product_name": product_data['product_name'], # type: ignore
                "available": product_data['quantity_available'] > 0, # type: ignore
                "stock": product_data['quantity_available'], # type: ignore
                "price": float(product_data['unit_price']) # type: ignore
            })
        else:
            return jsonify({"error": "Product not found"}), 404
            
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database query failed"}), 500
        
    finally:
        close_db_connection(conn, cursor)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
