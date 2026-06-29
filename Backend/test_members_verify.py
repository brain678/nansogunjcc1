import urllib.request
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
        return json.loads(body) if body else {}, response.status
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
print("MEMBERS MODULE - QUICK VERIFICATION TEST")
print("=" * 80)

token = get_token()
timestamp = int(time.time())

# Create member with unique data
result, status = test_endpoint("POST", "/api/v1/members/register", {
    "email": f"member{timestamp}@ex.com",
    "first_name": "Test",
    "last_name": "Member",
    "membership_tier": "standard",
    "phone": "+2341234567890",
    "expiry_months": 12
}, token)

print(f"[1] Create member: {status} {'PASS' if status == 201 else 'FAIL'}")
member_id = result.get('id')

if member_id:
    tests = [
        ("GET", f"/api/v1/members/{member_id}", "Get by ID"),
        ("GET", "/api/v1/members?skip=0&limit=10", "List"),
        ("PUT", f"/api/v1/members/{member_id}/profile", {"bio": "Updated bio"}, "Update Profile"),
        ("POST", f"/api/v1/members/{member_id}/renew", {"months": 12}, "Renew"),
        ("POST", f"/api/v1/members/{member_id}/upgrade-tier", None, "Upgrade Tier"),
        ("POST", f"/api/v1/members/{member_id}/suspend", None, "Suspend"),
        ("POST", f"/api/v1/members/{member_id}/activate", None, "Activate"),
    ]
    
    passed = 0
    for i, test in enumerate(tests, 2):
        if len(test) == 3:
            method, path, name = test
            data = None
        else:
            method, path, data, name = test
        
        result, status = test_endpoint(method, path, data, token)
        ok = status in [200, 201]
        print(f"[{i}] {name}: {status} {'PASS' if ok else 'FAIL'}")
        if ok:
            passed += 1
    
    print("\n" + "=" * 80)
    print(f"Members: {passed + 1}/{len(tests) + 1} PASSED ({((passed+1)/(len(tests)+1)*100):.0f}%)")
    print("=" * 80)
