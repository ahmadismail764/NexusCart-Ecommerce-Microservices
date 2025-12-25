package com.ecommerce.frontend;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ApiClient {
    private static final String INVENTORY_SERVICE_URL = "http://localhost:5002/api";
    private static final String CUSTOMER_SERVICE_URL = "http://localhost:5004/api";

    public List<Map<String, Object>> getCustomers() {
        List<Map<String, Object>> customers = new ArrayList<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(CUSTOMER_SERVICE_URL + "/customers"))
                    .GET()
                    .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONArray jsonArray = new JSONArray(response.body());
                for (int i = 0; i < jsonArray.length(); i++) {
                    JSONObject obj = jsonArray.getJSONObject(i);
                    Map<String, Object> customer = new HashMap<>();
                    customer.put("id", obj.getInt("customer_id"));
                    customer.put("name", obj.getString("name"));
                    customer.put("email", obj.getString("email"));
                     // Some endpoints might not return loyalty_points in list view, but let's check
                    if (obj.has("loyalty_points")) {
                         customer.put("loyalty_points", obj.getInt("loyalty_points"));
                    }
                    customers.add(customer);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return customers;
    }

    public Map<String, Object> getCustomer(int id) {
        Map<String, Object> customer = new HashMap<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(CUSTOMER_SERVICE_URL + "/customers/" + id))
                    .GET()
                    .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject obj = new JSONObject(response.body());
                customer.put("id", obj.getInt("customer_id"));
                customer.put("name", obj.getString("name"));
                customer.put("email", obj.getString("email"));
                customer.put("loyalty_points", obj.optInt("loyalty_points", 0));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return customer;
    }

    public List<Map<String, Object>> getCustomerOrders(int customerId) {
        List<Map<String, Object>> orders = new ArrayList<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:5001/api/orders/customer/" + customerId))
                    .GET()
                    .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONArray jsonArray = new JSONArray(response.body());
                for (int i = 0; i < jsonArray.length(); i++) {
                    JSONObject obj = jsonArray.getJSONObject(i);
                    Map<String, Object> order = new HashMap<>();
                    order.put("order_id", obj.getInt("order_id"));
                    order.put("total_amount", obj.getDouble("total_amount"));
                    order.put("status", obj.getString("status"));
                    if (obj.has("order_date")) {
                        order.put("order_date", obj.getString("order_date")); 
                    } else if (obj.has("created_at")) {
                         order.put("order_date", obj.getString("created_at"));
                    }
                    orders.add(order);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return orders;
    }

    public List<Map<String, Object>> getProducts() {
        List<Map<String, Object>> products = new ArrayList<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(INVENTORY_SERVICE_URL + "/inventory/products"))
                    .GET()
                    .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONArray jsonArray = new JSONArray(response.body());
                for (int i = 0; i < jsonArray.length(); i++) {
                    JSONObject obj = jsonArray.getJSONObject(i);
                    Map<String, Object> product = new HashMap<>();
                    product.put("id", obj.getInt("product_id"));
                    product.put("name", obj.getString("product_name"));
                    product.put("price", obj.getDouble("price"));
                    product.put("stock", obj.getInt("stock"));
                    products.add(product);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return products;
    }

    public Map<String, Object> getProduct(String productId) {
        Map<String, Object> product = new HashMap<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(INVENTORY_SERVICE_URL + "/inventory/check/" + productId))
                    .GET()
                    .build();
            
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject obj = new JSONObject(response.body());
                product.put("id", obj.getInt("product_id"));
                product.put("name", obj.getString("product_name"));
                product.put("price", obj.getDouble("price"));
                product.put("stock", obj.getInt("stock"));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return product;
    }
}
