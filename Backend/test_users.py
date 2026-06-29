import urllib.request
import urllib.error
import json
import time

def test_endpoint(method, path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = json.dumps(data).encode() if data else None
    try:
        req = urllib.request.Request(
            f"http://localhost:8000{path}",
            data=req_data,
            headers=headers,
            method=method
        )
        response = urllib.request.urlopen(req)
        body = response.read().decode()
        result = json.loads(body) if body else {}
        return result, response.status
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            return json.loads(body) if body else {}, e.code
        except:
            return None, e.code

def get_token():
    data = json.dumps({"email": "test@example.com", "password": "TestPassword123!"}).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    return json.loads(urllib.request.urlopen(req).read().decode())['token']['access_token']

print("=" * 80)
print("USERS MODULE - COMPREHENSIVE ENDPOINT TEST")
print("=" * 80)

token = get_token()
print("[OK] Authenticated\n")

timestamp = int(time.time())

# Test create user (already tested, just verify)
result, status = test_endpoint("POST", "/api/v1/users", {
    "email": f"newuser{timestamp}@example.com",
    "password": "TestPass123!",
    "first_name": "New",
    "last_name": "User",
    "organization_id": "org123"
}, token)
user_id = result.get('id') if status == 201 else None

# Users endpoints
tests = [
    ("POST", "/api/v1/users", 
     {"email": f"another{timestamp}@example.com", "password": "Pass123!", "first_name": "Another", "last_name": "User", "organization_id": "org456"},
     "1. Create user"),
    ("GET", "/api/v1/users", None, "2. List users"),
    ("GET", f"/api/v1/users/{user_id}", None, "3. Get user by ID" if user_id else "GET user (no ID)"),
    ("PUT", f"/api/v1/users/{user_id}", 
     {"first_name": "Updated", "last_name": "User", "is_active": True} if user_id else None,
     "4. Update user" if user_id else "PUT (no ID)"),
    ("DELETE", f"/api/v1/users/{user_id}", None, "5. Delete user" if user_id else "DEL (no ID)"),
]

passed = 0
failed = 0

for method, path, data, name in tests:
    if not path or (method in ["GET", "PUT", "DELETE"] and not user_id):
        print(f"[SKIP] {name:50} (no ID)")
        continue
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201, 204]
    print(f"[{'PASS' if ok else 'FAIL'}] {name:50} {status}")
    if ok:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
total = passed + failed
if total > 0:
    print(f"RESULTS: {passed}/{total} PASSED ({(passed/total*100):.0f}%)")
else:
    print("No tests run")
print("=" * 80)
