<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Place Order</title>
</head>
<body>
    <h1>Place Your Order</h1>
    <form action="order" method="post">
        <label for="customerId">Customer ID:</label>
        <input type="text" id="customerId" name="customerId" required><br><br>

        <label for="productId">Product ID:</label>
        <input type="text" id="productId" name="productId" value="<%= request.getParameter("productId") != null ? request.getParameter("productId") : "" %>" required><br><br>

        <label for="quantity">Quantity:</label>
        <input type="number" id="quantity" name="quantity" min="1" value="1" required><br><br>

        <input type="submit" value="Submit Order">
    </form>
</body>
</html>
