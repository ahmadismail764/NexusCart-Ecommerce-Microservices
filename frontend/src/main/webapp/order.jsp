<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="com.ecommerce.frontend.ApiClient" %>
<%@ page import="java.util.Map" %>
<%
    String productId = request.getParameter("productId");
    Map<String, Object> product = null;
    if (productId != null && !productId.isEmpty()) {
        ApiClient client = new ApiClient();
        product = client.getProduct(productId);
    }
%>
<html>
<head>
    <title>Place Order</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>Complete Your Order</h1>
        </header>

        <div class="form-card">
            <form action="order" method="post">
                <% if (product != null && !product.isEmpty()) { %>
                    <h2 style="margin-top: 0;">You are ordering: <%= product.get("name") %></h2>
                    <p class="product-price" style="margin-bottom: 2rem;">Price: $<%= String.format("%.2f", product.get("price")) %></p>
                    <input type="hidden" name="productId" value="<%= productId %>">
                <% } else { %>
                    <div class="form-group">
                        <label for="productId">Product ID:</label>
                        <input type="text" id="productId" name="productId" value="<%= productId != null ? productId : "" %>" required>
                    </div>
                <% } %>

                <div class="form-group">
                    <label for="customerId">Select Customer:</label>
                    <select id="customerId" name="customerId" required style="width: 100%; padding: 0.75rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 1rem; background-color: white;">
                        <option value="" disabled selected>-- Select a Customer --</option>
                        <%
                            ApiClient clientForCustomers = new ApiClient();
                            java.util.List<Map<String, Object>> customers = clientForCustomers.getCustomers();
                            if (customers != null) {
                                for (Map<String, Object> c : customers) {
                        %>
                                    <option value="<%= c.get("id") %>"><%= c.get("name") %> (<%= c.get("email") %>)</option>
                        <%
                                }
                            }
                        %>
                    </select>
                </div>

                <div class="form-group">
                    <label for="quantity">Quantity:</label>
                    <input type="number" id="quantity" name="quantity" min="1" value="1" <% if (product != null) { %> max="<%= product.get("stock") %>" <% } %> required>
                </div>

                <input type="submit" value="Confirm Order" class="btn btn-block">
                
                <a href="index.jsp" class="back-link">← Back to Products</a>
            </form>
        </div>
    </div>
</body>
</html>
