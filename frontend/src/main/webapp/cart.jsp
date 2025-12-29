<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ page import="com.ecommerce.frontend.ApiClient" %>
<%@ page import="java.util.Map" %>
<%@ page import="java.util.List" %>
<html>
<head>
    <title>Shopping Cart</title>
    <link rel="stylesheet" href="css/styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header>
            <h1>Your Cart</h1>
            <nav style="margin-top: 1rem;">
                <a href="index.jsp" class="nav-link">Home</a>
                <a href="cart.jsp" class="nav-link active">Cart</a>
                <a href="profile.jsp" class="nav-link">Profile</a>
            </nav>
        </header>

        <div id="cart-container">
            <div id="empty-cart-msg" style="display: none; text-align: center; padding: 3rem;">
                <h2>Your cart is empty</h2>
                <a href="index.jsp" class="btn">Start Shopping</a>
            </div>

            <div id="cart-content" style="display: none;">
                <div class="cart-items" style="background: white; border-radius: 12px; padding: 2rem; box-shadow: var(--shadow); margin-bottom: 2rem;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="text-align: left; border-bottom: 2px solid #eee;">
                                <th style="padding: 1rem;">Product</th>
                                <th style="padding: 1rem;">Price</th>
                                <th style="padding: 1rem;">Quantity</th>
                                <th style="padding: 1rem;">Total</th>
                                <th style="padding: 1rem;">Action</th>
                            </tr>
                        </thead>
                        <tbody id="cart-table-body">
                            <!-- Items injection -->
                        </tbody>
                    </table>
                    <div style="text-align: right; margin-top: 2rem; font-size: 1.5rem; font-weight: 700;">
                        Total: $<span id="cart-total-display">0.00</span>
                    </div>
                </div>

                <div class="form-card">
                    <h2>Checkout</h2>
                    <form action="order" method="post" id="checkout-form">
                        <input type="hidden" name="cartData" id="cartDataInput">
                        
                        <div class="form-group">
                            <label for="customerId">Select Customer:</label>
                            <select id="customerId" name="customerId" required class="form-control">
                                <option value="" disabled selected>-- Select a Customer --</option>
                                <%
                                    ApiClient client = new ApiClient();
                                    List<Map<String, Object>> customers = client.getCustomers();
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

                        <button type="submit" class="btn btn-block">Confirm Order</button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script>
        function loadCart() {
            const cartStr = localStorage.getItem('cart');
            const cart = cartStr ? JSON.parse(cartStr) : [];
            
            const emptyMsg = document.getElementById('empty-cart-msg');
            const content = document.getElementById('cart-content');
            const tbody = document.getElementById('cart-table-body');
            const totalDisplay = document.getElementById('cart-total-display');

            if (cart.length === 0) {
                emptyMsg.style.display = 'block';
                content.style.display = 'none';
                return;
            }

            emptyMsg.style.display = 'none';
            content.style.display = 'block';
            tbody.innerHTML = '';
            
            let total = 0;

            cart.forEach((item, index) => {
                const itemPrice = parseFloat(item.price);
                const itemQty = parseInt(item.quantity);
                const itemTotal = itemPrice * itemQty;
                total += itemTotal;
                console.log(item.name);
                console.log(itemPrice);
                console.log(itemQty);
                console.log(itemTotal);
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid #f0f0f0';
                tr.innerHTML = 
                    '<td style="padding: 1rem;">' + (item.name || 'N/A') + '</td>' +
                    '<td style="padding: 1rem;">$' + itemPrice.toFixed(2) + '</td>' +
                    '<td style="padding: 1rem;">' +
                        '<input type="number" min="1" value="' + itemQty + '" ' +
                               'onchange="updateQuantity(' + index + ', this.value)" ' +
                               'style="width: 70px; padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px;">' +
                    '</td>' +
                    '<td style="padding: 1rem; font-weight: 600;">$' + itemTotal.toFixed(2) + '</td>' +
                    '<td style="padding: 1rem;">' +
                        '<button onclick="removeItem(' + index + ')" class="btn" style="background-color: #dc2626; padding: 0.5rem 1rem; font-size: 0.875rem;">Remove</button>' +
                    '</td>';
                tbody.appendChild(tr);
            });

            totalDisplay.textContent = total.toFixed(2);
        }

        function updateQuantity(index, newQty) {
            const qty = parseInt(newQty);
            if (qty < 1) return;
            
            const cart = JSON.parse(localStorage.getItem('cart'));
            cart[index].quantity = qty;
            localStorage.setItem('cart', JSON.stringify(cart));
            loadCart();
        }

        function removeItem(index) {
            const cart = JSON.parse(localStorage.getItem('cart'));
            cart.splice(index, 1);
            localStorage.setItem('cart', JSON.stringify(cart));
            loadCart();
        }

        document.getElementById('checkout-form').onsubmit = function(e) {
            const cart = JSON.parse(localStorage.getItem('cart') || '[]');
            if (cart.length === 0) {
                e.preventDefault();
                alert('Your cart is empty');
                return;
            }
            
            const backendItems = cart.map(item => ({
                product_id: item.id,
                quantity: item.quantity
            }));
            
            document.getElementById('cartDataInput').value = JSON.stringify(backendItems);
            
            localStorage.removeItem('cart');
        };

        window.onload = loadCart;
    </script>
</body>
</html>
