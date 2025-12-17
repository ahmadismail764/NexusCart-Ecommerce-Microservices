<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Order Confirmation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background-color: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; }
        h1 { color: #28a745; margin-bottom: 20px; }
        p { font-size: 18px; color: #333; margin: 10px 0; }
        .order-id { font-weight: bold; font-size: 24px; color: #333; }
        .total { font-size: 20px; color: #555; margin-top: 20px; }
        .btn { display: inline-block; margin-top: 30px; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; transition: background-color 0.3s; }
        .btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Order Confirmed!</h1>
        <p>Thank you for your purchase.</p>
        <p>Your Order ID is: <div class="order-id"><%= request.getParameter("orderId") %></div></p>
        <p class="total">Total Amount: $<%= request.getParameter("totalAmount") %></p>
        <p>A confirmation email has been sent to you.</p>
        <a href="index.jsp" class="btn">Continue Shopping</a>
    </div>
</body>
</html>
