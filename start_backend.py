import subprocess
import time
import sys
import os
services = [
    {"name": "Order Service", "path": "backend/order_service/app.py", "port": 5001},
    {"name": "Inventory Service", "path": "backend/inventory_service/app.py", "port": 5002},
    {"name": "Pricing Service", "path": "backend/pricing_service/app.py", "port": 5003},
    {"name": "Customer Service", "path": "backend/customer_service/app.py", "port": 5004},
    {"name": "Notification Service", "path": "backend/notification_service/app.py", "port": 5005},
]
processes = []
try:
    print("Starting Microservices...")
    base_dir = os.getcwd()
    
    for service in services:
        print(f"Starting {service['name']} on port {service['port']}...")
        cmd = [sys.executable, service['path']]  # python from the curr. env
        p = subprocess.Popen(cmd, cwd=base_dir)
        processes.append(p)
        time.sleep(1)
    print("All services started. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping services...")
    for p in processes:
        p.terminate()
    print("Stopped.")