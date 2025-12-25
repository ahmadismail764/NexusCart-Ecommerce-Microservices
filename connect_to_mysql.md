# 🔌 Connecting Python Flask to MySQL

This guide explains how to connect your Python microservices to the MySQL database for Phase 2.

## 1. Prerequisites

Ensure you have the MySQL connector library installed in your virtual environment.

```bash
pip install mysql-connector-python
```

## 2. Database User Configuration

It is highly recommended (and required by the assignment) to use a specific user for the application rather than `root`.

**Run this SQL in MySQL Workbench:**

```sql
-- Create the user
CREATE USER IF NOT EXISTS 'ecommerce_user'@'localhost' IDENTIFIED BY 'secure_password';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ecommerce_system.* TO 'ecommerce_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;
```

## 3. Python Connection Code Pattern

Use this pattern in your Flask services (e.g., `inventory_service/app.py`).

### A. Import the library

```python
import mysql.connector
from mysql.connector import Error
```

### B. Create a Database Connection Function

Add this helper function to your `app.py` to handle connections cleanly.

```python
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='ecommerce_system',
            user='ecommerce_user',      # Use the user you created
            password='secure_password'  # Use the password you set
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
```

### C. Using the Connection in a Route

Here is an example of how to use it in an API endpoint (e.g., checking inventory).

```python
@app.route('/api/inventory/check/<int:product_id>', methods=['GET'])
def check_inventory(product_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True) # dictionary=True returns results as JSON-friendly dicts

    try:
        query = "SELECT * FROM inventory WHERE product_id = %s"
        cursor.execute(query, (product_id,))
        product = cursor.fetchone()

        if product:
            return jsonify({
                "product_id": product['product_id'],
                "available": product['quantity_available'] > 0,
                "stock": product['quantity_available'],
                "price": float(product['unit_price']) # Convert Decimal to float for JSON
            })
        else:
            return jsonify({"error": "Product not found"}), 404

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
```

## 4. Checklist for Each Service

- [ ] **Inventory Service:** Needs to Read (`SELECT`) and Update (`UPDATE`) stock.
- [ ] **Pricing Service:** Needs to Read (`SELECT`) tax rates and pricing rules.
- [ ] **Order Service:** Needs to Insert (`INSERT`) into `orders` and `order_items`.
