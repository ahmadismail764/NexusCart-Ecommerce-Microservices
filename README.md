# 🚀 SOA Project Canvas: E-Commerce Order Management System

**Goal:** Build a distributed microservices system with a Java Server Pages Frontend and 5 Python Backends.

---

## 1️⃣ PART 1: The Architecture Blueprint

This is what we are building. Everyone needs to agree on these ports.

### 🏗️ System Architecture

- **API Gateway (Frontend):** A Java JSP application running on Tomcat. It acts as the "face" of the system.
- **Microservices (Backend):** 5 independent Python Flask apps handling business logic.
- **Data Layer:** MySQL Database accessed by specific services only.

### 🔌 Port Configuration (Do not change these!)

| Service Name         | Port | Technology        | Responsibility                      |
| -------------------- | ---- | ----------------- | ----------------------------------- |
| Frontend App         | 8080 | Java JSP (Tomcat) | UI, Forms, API Gateway              |
| Order Service        | 5001 | Python Flask      | Order ID creation, Input Validation |
| Inventory Service    | 5002 | Python Flask      | Stock checking, DB updates          |
| Pricing Service      | 5003 | Python Flask      | Tax & Discount calculations         |
| Customer Service     | 5004 | Python Flask      | Profile & Order History             |
| Notification Service | 5005 | Python Flask      | Email Simulation (Orchestration)    |

### 💾 Database Config

- **DB Name:** `ecommerce_system`
- **User:** `ecommerce_user` / `secure_password` (or `root` for local dev)
- **Tables:** `inventory`, `customers`, `pricing_rules`, `tax_rates`, `notification_log`

---

## 2️⃣ PART 2: The Launchpad (Nov 22 – Dec 1)

**Focus:** Connectivity. Get the systems talking before writing complex logic.

### 📅 Phase 0: The "Hello World" Weekend (Nov 22 - 24)

**Goal:** Prove Java can talk to Python.

- [ ] **Team Java:** Install Apache Tomcat 10+.
- [ ] **Team Java:** Create a Servlet that makes an HTTP GET request to `http://localhost:5001/api/test`.
- [x] **Team Python:** Set up Virtual Env & Flask.
- [ ] **Team Python:** Create a simple route `/api/test` on Port 5001 that returns `{"status": "alive"}`.
- [ ] **Integration Test:** Run both. Access the JSP page. Does it show the JSON from Python?

### 📅 Phase 1: The "Tracer Bullet" (Nov 25 - Dec 1)

**Goal:** One complete feature flow (Create Order).

- [ ] **Frontend:** Create `index.jsp` (Hardcoded product list for now).
- [ ] **Frontend:** Create `order.jsp` (HTML Form for Customer ID, Product ID, Qty).
- [ ] **Backend (Order Service):** Create `POST /api/orders/create`. Accept JSON, print it to console, return success.
- [ ] **Backend (Inventory Service):** Create `GET /api/inventory/check/{id}`. Return hardcoded stock true.
- [ ] **The Wiring:** Java Servlet takes Form Data -> POSTs to Order Service.

---

## 3️⃣ PART 3: The Heavy Lifting (Dec 2 – Dec 15)

**Focus:** Logic, Database, and Orchestration.

### 📅 Phase 2: Real Data (Dec 2 - Dec 8)

**Goal:** Connect to MySQL and implement Pricing/Customer logic.

- [ ] **Database:** Run the SQL scripts to create tables and insert dummy data.
- [ ] **Inventory Service:** Connect to MySQL. Implement "Check Stock" and "Update Stock" (SQL UPDATE).
- [ ] **Pricing Service:** Connect to MySQL. Fetch base price from Inventory Service (HTTP Call), then calculate tax/discount.
- [ ] **Customer Service:** Connect to MySQL. Fetch profile data.

### 📅 Phase 3: "Web of Chaos" (Dec 9 - Dec 15)

**Goal:** The Notification Service (Orchestration) and Final Polish.

- [ ] **Notification Service:** This is the hardest one.
  - Receive Order ID.
  - Call Customer Service (get email).
  - Call Inventory Service (get product names).
  - "Send" Email (Print to console).
  - Log to DB.
- [ ] **Frontend:** Finish `confirmation.jsp`. Display the final Order Summary.
- [ ] **Error Handling:** gracefully handle if a Python service is offline (try/catch in Java).

---

## 4️⃣ PART 4: The Knowledge Base (Learning Links)

Curated resources to help you build this FAST.

### 🟢 For the Python/Flask Crew (Backend)

**Microservices "Hello World":**

- 🔗 [GeeksForGeeks: Building Microservices in Flask](https://www.geeksforgeeks.org/)
- **Why:** Copy-paste code for running apps on different ports.

**Flask REST API Crash Course:**

- 🔗 [YouTube: Tech With Tim Flask API](https://www.youtube.com/)
- **Tip:** Watch the first 20 mins. Ignore the advanced database stuff for now.

**Connecting to MySQL:**

- 🔗 [HevoData: Flask MySQL Connection](https://hevodata.com/)
- **Library:** Use `mysql-connector-python`.

**Calling Other Services (Python to Python):**

- 🔗 [Python Requests Library Guide](https://requests.readthedocs.io/)
- **Why:** You need this for the Notification Service to talk to the others.

### 🔴 For the Java/JSP Crew (Frontend)

**Servlets for Beginners:**

- 🔗 [Baeldung: Intro to Servlets](https://www.baeldung.com/)
- **Focus:** Understand `doGet` and `doPost`.

**Calling REST APIs from Java (CRITICAL):**

- 🔗 [ZetCode: Java Servlet REST Client](https://zetcode.com/)
- **Why:** This is the exact code (`HttpClient`) you need to talk to the Python backend.

**Tomcat 10 Setup:**

- 🔗 [Apache Tomcat 10 Setup Guide](https://tomcat.apache.org/)
- **Crucial:** Use `import jakarta.servlet...` instead of `javax.servlet...`.

---

## ⚡ Quick Tips

- **JSON is King:** Ensure Java sends JSON keys exactly how Python expects them (e.g., `product_id` vs `productId`).
- **Kill Ports:** If your code crashes, the port might stay open.
  - **Windows:** `netstat -ano | findstr :5001` -> `taskkill /PID <pid> /F`
  - **Mac/Linux:** `lsof -i :5001` -> `kill -9 <pid>`
