from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "alive", "service": "notification-service"})

if __name__ == '__main__':
    app.run(port=5005, debug=True)
