# NexusCart Microservices - Code Review & Action Items

## 🌟 What Went Well (Strengths to Maintain)

- **Logical Domain Boundaries:** Excellent separation of concerns across Order, Customer, Inventory, Pricing, and Notification services.
- **Resilience to Non-Critical Failures:** Great use of `try/except` blocks in `order_service.py` when calling the Notification and Loyalty services, ensuring the main checkout flow isn't blocked by secondary service failures.
- **SQL Injection Prevention:** Consistent use of parameterized queries (`%s`) across all database operations.

---

## 🚨 Critical Architectural Fixes (High Priority)

### 1. Fix the Shared Database Anti-Pattern (Distributed Monolith)

- **Issue:** All microservices are reading from and writing to a single, shared `ecommerce_system` database (`schema.sql`). This tightly couples the services together.
- **Action Item:** Move towards a "Database-per-Service" architecture. Split the database so Inventory, Orders, Customers, etc., each have their own isolated database. If a service needs external data, it must fetch it via an API call, not a DB join.

### 2. Replace Synchronous HTTP Coupling with Event-Driven Architecture

- **Issue:** `order_service.py` relies on blocking, synchronous HTTP `requests.get()` calls to multiple other services to complete a single transaction. If one service is slow or down, the whole checkout process fails or stalls.
- **Action Item:** Introduce a Message Broker (like RabbitMQ, Kafka, or Redis Pub/Sub). For example, when an order is created, publish an `OrderCreated` event. The Notification and Customer (loyalty) services can listen to this event and process their tasks asynchronously in the background.

### 3. Implement Distributed Transactions (Saga Pattern)

- **Issue:** In `create_order()`, the order is committed to the database _before_ stock is updated via HTTP. If the Inventory service fails to update the stock, the system enters an inconsistent state (order confirmed, but stock not reserved).
- **Action Item:** Implement a Saga Pattern or Two-Phase Commit. If a downstream service (like Inventory) fails after the order is created, the Order Service must send a compensating transaction (e.g., an API call to cancel the order) to roll back the changes.

---

## 🤔 Refactoring Opportunities (Technical Debt)

### 1. Fix the N+1 Query Problem

- **Issue:** In `pricing_service.py`, a database query is executed inside a `for item in products:` loop to fetch discount rules. Processing a cart with 50 items results in 50 separate database calls.
- **Action Item:** Fetch all applicable pricing rules in a single query _before_ the loop using a SQL `IN` clause (e.g., `SELECT * FROM pricing_rules WHERE product_id IN (...)`), load them into memory, and perform the lookups from the dictionary.

### 2. Utilize the Dead Code in `utils.py`

- **Issue:** You wrote a robust `execute_query()` helper function in `utils.py` that handles connections, cursors, and cleanup gracefully, but none of the route handlers actually use it. They all repeat the same boilerplate code.
- **Action Item:** Refactor your endpoints to call `execute_query()` instead of manually managing `get_db_connection()`, `try/except/finally`, and `close_db_connection()` everywhere.

### 3. Remove Hardcoded Infrastructure URLs

- **Issue:** Service URLs (e.g., `http://localhost:5004/api/customers`) are hardcoded at the top of your Python files. This will break when deployed to Docker or a cloud provider.
- **Action Item:** Use the `python-dotenv` package (which you already installed) to load these URLs dynamically from environment variables using `os.getenv()`.
