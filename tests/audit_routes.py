import requests
import time
import sys
import os

# Wait for server to start
print("Waiting for server to start...")
time.sleep(3)

BASE_URL = "http://localhost:5000"

def check_route(path, method="GET", expected_status=200):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"Unknown method {method}")
            return False

        if response.status_code == expected_status:
            print(f"[PASS] {method} {path} - {response.status_code}")
            return True
        else:
            print(f"[FAIL] {method} {path} - Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {method} {path} - Exception: {e}")
        return False

def audit():
    success = True

    # 1. Static Assets & Pages
    success &= check_route("/")
    success &= check_route("/static/css/style.css")
    success &= check_route("/static/js/app.js")

    # 2. API Endpoints
    success &= check_route("/api/videos")
    success &= check_route("/api/jobs")
    success &= check_route("/api/stats")

    # 3. Test 404
    success &= check_route("/api/nonexistent", expected_status=404)

    # 4. Check Cleanup (POST)
    # Cleanup might return 200 or 500 depending on permissions, but should likely work.
    success &= check_route("/api/cleanup", method="POST")

    if success:
        print("\nAll checks passed!")
        sys.exit(0)
    else:
        print("\nSome checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    audit()
