<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="com.ecommerce.frontend.ApiClient" %>
<%@ page import="java.util.List" %>
<%@ page import="java.util.Map" %>
<html>
  <head>
    <title>E-Commerce Home</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

</head>
  <body>
    <div class="container">
        <header>
            <h1>E-Commerce Store</h1>
            <nav style="margin-top: 1rem;">
                <a href="index.jsp" class="nav-link active">Home</a>
                <a href="cart.jsp" class="nav-link">Cart</a>
                <a href="profile.jsp" class="nav-link">Profile</a>
            </nav>
            <h2>Discover our premium products</h2>
        </header>

        <div class="product-grid">
            <%
                ApiClient client = new ApiClient();
                java.util.List<Map<String, Object>> products = client.getProducts();
                
                if (products.isEmpty()) {
            %>
                <p>No products available at the moment.</p>
            <%
                } else {
                    for (Map<String, Object> product : products) {
            %>
            <div class="product-card">
                <div>
                    <h3 class="product-title"><%= product.get("name") %></h3>
                    <div class="product-price">$<%= String.format("%.2f", product.get("price")) %></div>
                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">Stock: <%= product.get("stock") %></p>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center; margin-top: 1rem;">
                    <label for="qty-<%= product.get("id") %>" style="font-weight: 600; margin: 0;">Qty:</label>
                    <input type="number" id="qty-<%= product.get("id") %>" value="1" min="1" max="<%= product.get("stock") %>" 
                           style="width: 60px; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px;">
                </div>
                <button onclick='addToCart(<%= product.get("id") %>, "<%= product.get("name").toString().replace("'", "\\'") %>", <%= product.get("price") %>, <%= product.get("stock") %>)' class="btn" style="margin-top: 0.5rem;">Add to Cart</button>
            </div>
            <%
                    }
                }
            %>
        </div>
    </div>
    
    <div id="toast" class="toast">Item added to cart!</div>

    <script>
        function addToCart(id, name, price, stock) {
            console.log("Adding to cart:", id, name, price, stock);
            const qtyInput = document.getElementById('qty-' + id);
            if (!qtyInput) {
                console.error("Quantity input not found for id:", id);
                return;
            }
            const quantity = parseInt(qtyInput.value);
            
            if (isNaN(quantity) || quantity < 1) {
                alert("Please enter a valid quantity (minimum 1)");
                return;
            }
            
            const cart = JSON.parse(localStorage.getItem('cart') || '[]');
            const existing = cart.find(item => item.id === id);
            
            if (existing) {
                if (existing.quantity + quantity > stock) {
                    alert('Cannot add more items than available in stock! You already have ' + existing.quantity + ' in cart.');
                    return;
                }
                existing.quantity += quantity;
            } else {
                if (quantity > stock) {
                    alert('Cannot add more items than available in stock!');
                    return;
                }
                cart.push({
                    id: id,
                    name: name,
                    price: price,
                    quantity: quantity
                });
            }
            
            localStorage.setItem('cart', JSON.stringify(cart));
            showToast(name, quantity);
            qtyInput.value = 1; // Reset to 1
        }

        function showToast(productName, qty) {
            console.log("Showing toast for:", productName);
            const toast = document.getElementById('toast');
            if (toast) {
                console.log('Toast found!');
                toast.textContent = qty + 'x ' + productName + ' added to cart!';
                toast.className = "toast show";
                setTimeout(function(){ toast.className = toast.className.replace("show", ""); }, 2500);
            } else {
                console.error("Toast element not found!");
            }
        }
    </script>
  </body>
</html>
