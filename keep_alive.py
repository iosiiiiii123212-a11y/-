#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keep-Alive Script for Render
Pings the server every 10 minutes to prevent it from sleeping
"""

import requests
import time
import os
from datetime import datetime

# Get the server URL from environment or use default
SERVER_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')

def ping_server():
    """Ping the server to keep it alive"""
    try:
        response = requests.get(f'{SERVER_URL}/health', timeout=10)
        if response.status_code == 200:
            print(f"✅ [{datetime.now()}] Server is alive!")
            return True
        else:
            print(f"⚠️  [{datetime.now()}] Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ [{datetime.now()}] Failed to ping server: {e}")
        return False

def main():
    """Main loop - ping every 10 minutes"""
    print("🚀 Keep-Alive script started!")
    print(f"📡 Pinging: {SERVER_URL}")
    print("⏰ Interval: 10 minutes")
    print("-" * 50)
    
    while True:
        ping_server()
        # Sleep for 10 minutes (600 seconds)
        time.sleep(600)

if __name__ == '__main__':
    main()
