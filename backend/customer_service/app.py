from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "customer-service"})

if __name__ == '__main__':
    app.run(port=5004, debug=True)
