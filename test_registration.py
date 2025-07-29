#!/usr/bin/env python3
"""
Test script to demonstrate user registration functionality.
This script shows how the registration endpoint behaves with different scenarios.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your API URL
HEADERS = {"Content-Type": "application/json"}

def test_user_registration():
    """Test user registration scenarios."""
    
    print("🧪 Testing User Registration Functionality")
    print("=" * 50)
    
    # Test data
    test_users = [
        {"name": "Alice Johnson", "email": "alice.test@example.com"},
        {"name": "Bob Smith", "email": "bob.test@example.com"},
        {"name": "Alice Updated", "email": "alice.test@example.com"},  # Same email, different name
    ]
    
    # Test 1: Register a new user
    print("\n1️⃣ Testing new user registration:")
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            headers=HEADERS,
            json=test_users[0]
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"👤 Name: {data['user']['name']}")
            print(f"🆕 Created: {data['created']}")
            print(f"💬 Message: {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API. Make sure the server is running.")
        return
    
    # Test 2: Register another new user
    print("\n2️⃣ Testing second user registration:")
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            headers=HEADERS,
            json=test_users[1]
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"👤 Name: {data['user']['name']}")
            print(f"🆕 Created: {data['created']}")
            print(f"💬 Message: {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Try to register existing user with different name
    print("\n3️⃣ Testing existing user registration with name update:")
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            headers=HEADERS,
            json=test_users[2]  # Same email as first user, different name
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"👤 Name: {data['user']['name']}")
            print(f"🆕 Created: {data['created']}")
            print(f"💬 Message: {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Try to register the same user again (no changes)
    print("\n4️⃣ Testing duplicate registration (no changes):")
    try:
        response = requests.post(
            f"{BASE_URL}/users/register",
            headers=HEADERS,
            json=test_users[2]  # Same as previous
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Email: {data['user']['email']}")
            print(f"👤 Name: {data['user']['name']}")
            print(f"🆕 Created: {data['created']}")
            print(f"💬 Message: {data['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: List all users to see the results
    print("\n5️⃣ Listing all users:")
    try:
        response = requests.get(f"{BASE_URL}/users")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users:")
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user['name']} ({user['email']}) - ID: {user['id']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 User registration testing completed!")
    print("\n💡 Key Features Demonstrated:")
    print("   • New user creation")
    print("   • Existing user detection") 
    print("   • Name updates for existing users")
    print("   • Duplicate registration handling")

def test_health_endpoints():
    """Test health endpoints."""
    print("\n🏥 Testing Health Endpoints")
    print("-" * 30)
    
    try:
        # Test basic health
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Note: Database health check might fail without proper Snowflake credentials
        print("ℹ️  Database health check skipped (requires Snowflake credentials)")
        
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Starting API tests at {datetime.now()}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test health first
    test_health_endpoints()
    
    # Test user registration
    test_user_registration()
    
    print(f"\n✨ Tests completed at {datetime.now()}")
    print("\n📚 To start the API server locally, run:")
    print("   python run_dev.py")
    print("\n📖 API documentation available at:")
    print(f"   {BASE_URL}/docs")
