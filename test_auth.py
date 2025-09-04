#!/usr/bin/env python3
"""
Simple test script to check authentication endpoints
"""

import requests
import json

def test_auth_endpoints():
    base_url = "http://localhost:5000"
    
    print("Testing authentication endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test rate limit status endpoint
    try:
        response = requests.get(f"{base_url}/api/auth/rate-limit-status")
        print(f"Rate limit endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Rate limit endpoint error: {e}")
    
    # Test signup endpoint
    try:
        data = {
            "email": "test@example.com",
            "password": "TestPass123",
            "confirm_password": "TestPass123"
        }
        response = requests.post(f"{base_url}/api/auth/signup", json=data)
        print(f"Signup endpoint: {response.status_code}")
        if response.status_code in [200, 201, 400, 409]:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Signup endpoint error: {e}")

if __name__ == "__main__":
    test_auth_endpoints()
