from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "inventory-service"})

@app.route('/api/inventory/check/<int:product_id>', methods=['GET'])
def check_inventory(product_id):
    # Hardcoded response for Phase 1
    print(f"Checking inventory for Product ID: {product_id}")
    return jsonify({"product_id": product_id, "available": True, "stock": 100})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
