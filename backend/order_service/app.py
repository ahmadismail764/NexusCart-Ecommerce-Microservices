from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "order-service"})

@app.route('/api/orders/create', methods=['POST'])
def create_order():
    data = request.get_json()
    print(f"Received Order: {data}")
    # Logic to save order would go here
    return jsonify({"message": "Order received successfully", "order": data}), 201

if __name__ == '__main__':
    app.run(port=5001, debug=True)
