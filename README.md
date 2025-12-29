# Nexus Cart 🛒

**NexusCart** is a robust, modular e-commerce backend built using **Service-Oriented Architecture (SOA)**. It decouples core business logic into five autonomous microservices, enabling scalable inventory management, dynamic pricing calculations, and real-time order processing.

---

## 🏗️ Architecture

The system is composed of 5 distinct RESTful microservices that communicate via HTTP JSON payloads:

1. **Order Service (`5001`):** Orchestrates the buying process, transactions, and history.
2. **Inventory Service (`5002`):** Handles stock levels, batch availability checks, and atomic updates.
3. **Pricing Service (`5003`):** Dynamic price calculation engine with support for tax rules and bulk discounts.
4. **Customer Service (`5004`):** Manages user profiles and loyalty point accumulation.
5. **Notification Service (`5005`):** Asynchronous email simulation and activity logging.

---

## 📊 Database Schema

The system uses a unified MySQL database (`ecommerce_system`) to maintain relational integrity while allowing services to manage their specific domains.

![Database ER Diagram](database/Database-ERDiagram.png)

---

## 🚀 Setup & Installation

### Prerequisites

The project requires **Python 3.8+** and **MySQL Server 8.0**. **Postman** is recommended for API testing.

### Database Configuration

The system uses a MySQL database named `ecommerce_system`. The schema and initial data are provided in `database/schema.sql`, which can be imported to initialize the database environment.

```bash
mysql -u root -p ecommerce_system < database/schema.sql
```

### Environment Configuration

Python dependencies can be installed in a virtual environment using the following commands:

```bash
py -m venv .venv
.venv\Scripts\activate
pip install flask mysql-connector-python requests
```

### Service Deployment

The microservices are designed to run concurrently. Each service can be started using the Python interpreter:

```bash
python backend/order_service.py
python backend/inventory_service.py
python backend/pricing_service.py
python backend/customer_service.py
python backend/notif_service.py
```

---

## 🧪 API Testing

A **Postman Collection** (`test_suite.postman_collection.json`) is provided to facilitate endpoint testing and validation.

The collection covers primary business workflows:

- **Shopping Flow:** End-to-end simulation from inventory browsing and price calculation to order creation.
- **Loyalty System:** Validation of loyalty point updates within customer profiles post-purchase.
- **Order History:** Retrieval and verification of past order records for specific customers.

---

## 📂 Project Structure

```text
NexusCart/
├── backend/
│   ├── customer_service.py   # Port 5004
│   ├── inventory_service.py  # Port 5002
│   ├── order_service.py      # Port 5001
│   ├── pricing_service.py    # Port 5003
│   ├── notif_service.py      # Port 5005
│   └── utils.py              # DB Connection Logic
├── database/
│   ├── Database-ERDiagram.png
│   ├── schema.dbml
│   └── schema.sql
├── frontend/
│   ├── src/
│   ├── target/
│   └── pom.xml
├── test-suite.postman_collection.json # Postman Tests
├── requirements.txt
└── README.md
```
