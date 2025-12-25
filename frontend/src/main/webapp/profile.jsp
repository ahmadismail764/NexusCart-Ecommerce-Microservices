<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="com.ecommerce.frontend.ApiClient" %>
<%@ page import="java.util.Map" %>
<%@ page import="java.util.List" %>
<%
    String customerIdParam = request.getParameter("customerId");
    Map<String, Object> customer = null;
    List<Map<String, Object>> orders = null;
    ApiClient client = new ApiClient();
    
    // Default to first customer if not specified (for demo purposes) or show selection
    // Ideally we should have a login, but for this simple app, we can select customer to view profile
    
    // Get list of all customers for the dropdown selector
    List<Map<String, Object>> allCustomers = client.getCustomers();
    
    if (customerIdParam != null && !customerIdParam.isEmpty()) {
        int cId = Integer.parseInt(customerIdParam);
        customer = client.getCustomer(cId);
        orders = client.getCustomerOrders(cId);
    }
%>
<html>
<head>
    <title>My Profile</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>My Profile</h1>
            <nav style="margin-top: 1rem;">
                <a href="index.jsp" class="nav-link">Home</a>
                <a href="cart.jsp" class="nav-link">Cart</a>
                <a href="profile.jsp" class="nav-link active">Profile</a>
            </nav>
        </header>

        <div class="form-card" style="max-width: 800px; margin-bottom: 2rem;">
            <h2>Select Customer Profile</h2>
            <form action="profile.jsp" method="get" style="display: flex; gap: 1rem; align-items: center;">
                 <select name="customerId" onchange="this.form.submit()" style="flex: 1; padding: 0.5rem; border-radius: 6px; border: 1px solid #e2e8f0;">
                    <option value="" disabled selected>-- Select View --</option>
                    <% for(Map<String, Object> c : allCustomers) { %>
                        <option value="<%= c.get("id") %>" <%= (customerIdParam != null && c.get("id").toString().equals(customerIdParam)) ? "selected" : "" %>>
                            <%= c.get("name") %>
                        </option>
                    <% } %>
                 </select>
                 <button type="submit" class="btn" style="padding: 0.5rem 1rem;">View</button>
            </form>
        </div>

        <% if (customer != null) { %>
            <div class="row" style="display: flex; gap: 2rem; flex-wrap: wrap;">
                <!-- Customer Details Card -->
                <div class="card" style="flex: 1; min-width: 300px; background: white; padding: 2rem; border-radius: 12px; box-shadow: var(--shadow);">
                    <h2>Customer Details</h2>
                    <div class="detail-row">
                        <strong>Name:</strong> <span><%= customer.get("name") %></span>
                    </div>
                    <div class="detail-row">
                        <strong>Email:</strong> <span><%= customer.get("email") %></span>
                    </div>
                    <div class="detail-row" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">
                        <strong>Loyalty Points:</strong> 
                        <span style="color: var(--primary-color); font-weight: 800; font-size: 1.5rem;"><%= customer.get("loyalty_points") %></span>
                    </div>
                </div>

                <!-- Order History -->
                <!-- Order History -->
                <div class="card" style="flex: 2; min-width: 300px;">
                    <h2>Order History</h2>
                    <% if (orders != null && !orders.isEmpty()) { %>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>Date-Time</th>
                                        <th>Status</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <% for(Map<String, Object> order : orders) { %>
                                        <tr>
                                            <td>#<%= order.get("order_id") %></td>
                                            <td style="color: var(--text-secondary); font-size: 0.9em;">
                                                <%= order.get("order_date") != null ? order.get("order_date").toString().replace("T", " ").substring(0, 16) : "N/A" %>
                                            </td>
                                            <td>
                                                <span class="status-badge status-<%= order.get("status").toString().toLowerCase() %>">
                                                    <%= order.get("status") %>
                                                </span>
                                            </td>
                                            <td style="font-weight: 600;">$<%= String.format("%.2f", order.get("total_amount")) %></td>
                                        </tr>
                                    <% } %>
                                </tbody>
                            </table>
                        </div>
                    <% } else { %>
                        <p style="color: var(--text-secondary); font-style: italic; margin-top: 1rem;">No orders found for this customer.</p>
                    <% } %>
                </div>
            </div>
        <% } %>
    </div>
</body>
</html>
