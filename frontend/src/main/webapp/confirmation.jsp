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
        <header>
            <h1>Order Confirmed!</h1>
        </header>

        <div class="form-card" style="text-align: center;">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🎉</div>
            <h2 style="color: #10b981; margin-bottom: 1rem;">Thank you for your purchase!</h2>
            <p>Your order (ID: <%= request.getParameter("orderId") %>) has been successfully placed.</p>
            <p style="font-size: 1.25rem; font-weight: 700; margin: 1.5rem 0;">
                Total Amount: $<%= request.getParameter("totalAmount") %>
            </p>
            
            <% 
                String points = request.getParameter("pointsEarned");
                if (points != null && !points.equals("0")) { 
            %>
                <div style="background: #ecfdf5; color: #065f46; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                    <strong>You earned <%= points %> Loyalty Points!</strong>
                </div>
            <% } %>

            <a href="index.jsp" class="btn">Continue Shopping</a>
        </div>
    </div>
</body>
</html>
