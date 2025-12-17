package com.ecommerce.frontend;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.math.BigDecimal;
@WebServlet(name = "OrderServlet", urlPatterns = {"/order"})
public class OrderServlet extends HttpServlet {
    private static final String ORDER_SERVICE_URL = "http://localhost:5001/api/orders/create";
    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
        String customerId = req.getParameter("customerId");
        String productId = req.getParameter("productId");
        String quantity = req.getParameter("quantity");
        // Create JSON object structure:
        // {
        //   "customer_id": 1,
        //   "products": [{"product_id": 1, "quantity": 2}],
        //   "total_amount": 0.00
        // }
        
        JSONObject orderJson = new JSONObject();
        orderJson.put("customer_id", Integer.parseInt(customerId));
        
        JSONObject productItem = new JSONObject();
        productItem.put("product_id", Integer.parseInt(productId));
        productItem.put("quantity", Integer.parseInt(quantity));
        
        JSONArray productsArray = new JSONArray();
        productsArray.put(productItem);
        
        orderJson.put("products", productsArray);
        orderJson.put("total_amount", new BigDecimal("0.00"));
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(ORDER_SERVICE_URL))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(orderJson.toString()))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            resp.setContentType("text/html");
            resp.getWriter().println("<h1>Order Status</h1>");
            resp.getWriter().println("<p>Backend Response: " + response.body() + "</p>");
            resp.getWriter().println("<a href='index.jsp'>Back to Home</a>");
            JSONObject jsonResponse = new JSONObject(response.body());
            
            if (response.statusCode() == 201) {
                int orderId = jsonResponse.getInt("order_id");
                double totalAmount = jsonResponse.getDouble("total_amount");
                
                resp.sendRedirect("confirmation.jsp?orderId=" + orderId + "&totalAmount=" + totalAmount);
            } else {
                resp.setContentType("text/html");
                resp.getWriter().println("<h1>Error Creating Order</h1>");
                 resp.getWriter().println("<p>" + jsonResponse.optString("error", "Unknown error") + "</p>");
                resp.getWriter().println("<a href='index.jsp'>Back to Home</a>");
            }
        } catch (Exception e) {
            resp.getWriter().println("<h1>Error</h1>");
            resp.getWriter().println("<p>" + e.getMessage() + "</p>");
            e.printStackTrace();
        }
    }
}
