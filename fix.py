"""Test the database after fixes

Provides a fallback lightweight HTTP client if the 'requests' package
is not installed, preventing import errors.
"""

try:
    import requests  # type: ignore
except ImportError:  # Fallback implementation using urllib
    import urllib.request
    import urllib.error
    import json as _json

    class _Resp:
        def __init__(self, status, data):
            self.status_code = status
            self.text = data
            self.content = data.encode()
        def json(self):
            try:
                return _json.loads(self.text)
            except Exception:
                return None

    class requests:  # Minimal shim
        @staticmethod
        def post(url, json=None):
            data = _json.dumps(json or {}).encode()
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req) as r:
                    body = r.read().decode()
                    return _Resp(r.getcode(), body)
            except urllib.error.HTTPError as e:
                body = e.read().decode()
                return _Resp(e.code, body)
            except Exception as e:
                return _Resp(0, str(e))

        @staticmethod
        def get(url):
            req = urllib.request.Request(url, method="GET")
            try:
                with urllib.request.urlopen(req) as r:
                    body = r.read().decode()
                    return _Resp(r.getcode(), body)
            except urllib.error.HTTPError as e:
                body = e.read().decode()
                return _Resp(e.code, body)
            except Exception as e:
                return _Resp(0, str(e))

import json

BASE_URL = "http://127.0.0.1:5000"

def test_all_endpoints():
    print("🧪 Testing all endpoints after database fix...")
    
    # Test data
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "password123",
        "phone": "+1234567890",
        "address": "123 Test Street"
    }
    
    mechanic_data = {
        "first_name": "Test",
        "last_name": "Mechanic",
        "email": "mechanic@example.com", 
        "password": "mechanic123",
        "specialization": "General Repairs",
        "years_experience": 3,
        "hourly_rate": 40.0
    }
    
    try:
        # Test customer registration
        print("1. Testing customer registration...")
        response = requests.post(f"{BASE_URL}/customers/register", json=customer_data)
        print(f"   Status: {response.status_code}")
        
        # Test mechanic registration  
        print("2. Testing mechanic registration...")
        response = requests.post(f"{BASE_URL}/mechanics/register", json=mechanic_data)
        print(f"   Status: {response.status_code}")
        
        # Test health endpoint
        print("3. Testing health endpoint...")
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_all_endpoints()