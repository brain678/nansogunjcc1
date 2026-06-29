"""
NANS BACKEND - FRESH COMPREHENSIVE ENDPOINT TEST V2 - WITH ERROR DETAILS
Tests all 4 modules: Auth, Users, Members, Meetings
"""

import urllib.request
import urllib.error
import json
import time
from datetime import datetime, timedelta

def json_serial(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def test_endpoint(method, path, data=None, token=None):
    """Make HTTP request to endpoint"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = json.dumps(data, default=json_serial).encode() if data else None
    try:
        req = urllib.request.Request(
            f"http://localhost:8000{path}",
            data=req_data,
            headers=headers,
            method=method
        )
        response = urllib.request.urlopen(req)
        body = response.read().decode()
        return json.loads(body) if body else {}, response.status, None
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            return json.loads(body) if body else {}, e.code, body
        except:
            return None, e.code, f"HTTP {e.code}"
    except Exception as e:
        return None, 0, str(e)

print("\n" + "=" * 90)
print("NANS BACKEND - FRESH COMPREHENSIVE ENDPOINT TEST")
print("=" * 90)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 90 + "\n")

# ==================== MODULE 1: AUTHENTICATION ====================
print("[MODULE 1] AUTHENTICATION")
print("-" * 90)

auth_results = []

# 1. Login
print("Testing: POST /api/v1/auth/login")
result, status, error = test_endpoint("POST", "/api/v1/auth/login", {
    "email": "test@example.com",
    "password": "TestPassword123!"
})
auth_results.append(("Login", status == 200))
access_token = result.get('token', {}).get('access_token') if status == 200 else None
refresh_token = result.get('token', {}).get('refresh_token') if status == 200 else None
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# 2. Get Current User
if access_token:
    print("Testing: GET /api/v1/auth/me")
    result, status, error = test_endpoint("GET", "/api/v1/auth/me", token=access_token)
    auth_results.append(("Get Current User", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# 3. Refresh Token
if refresh_token:
    print("Testing: POST /api/v1/auth/refresh")
    result, status, error = test_endpoint("POST", "/api/v1/auth/refresh", {
        "refresh_token": refresh_token
    })
    auth_results.append(("Refresh Token", status == 200))
    if status == 200:
        access_token = result.get('access_token')
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# 4. Logout
if access_token:
    print("Testing: POST /api/v1/auth/logout")
    result, status, error = test_endpoint("POST", "/api/v1/auth/logout", token=access_token)
    auth_results.append(("Logout", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# Re-login for subsequent tests
result, status, error = test_endpoint("POST", "/api/v1/auth/login", {
    "email": "test@example.com",
    "password": "TestPassword123!"
})
access_token = result.get('token', {}).get('access_token') if status == 200 else None

# ==================== MODULE 2: USERS ====================
print("[MODULE 2] USERS")
print("-" * 90)

user_results = []
timestamp = int(time.time())

# 1. Create User
print("Testing: POST /api/v1/users")
result, status, error = test_endpoint("POST", "/api/v1/users", {
    "email": f"user{timestamp}@ex.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "organization_id": "org123"
}, access_token)
user_results.append(("Create User", status == 201))
user_id = result.get('id') if status == 201 else None
print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}\n")

# 2. List Users
print("Testing: GET /api/v1/users")
result, status, error = test_endpoint("GET", "/api/v1/users", token=access_token)
user_results.append(("List Users", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# 3. Get User by ID
if user_id:
    print("Testing: GET /api/v1/users/{id}")
    result, status, error = test_endpoint("GET", f"/api/v1/users/{user_id}", token=access_token)
    user_results.append(("Get User", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 4. Update User
    print("Testing: PUT /api/v1/users/{id}")
    result, status, error = test_endpoint("PUT", f"/api/v1/users/{user_id}", {
        "first_name": "Updated",
        "last_name": "Name"
    }, access_token)
    user_results.append(("Update User", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 5. Delete User
    print("Testing: DELETE /api/v1/users/{id}")
    result, status, error = test_endpoint("DELETE", f"/api/v1/users/{user_id}", token=access_token)
    user_results.append(("Delete User", status == 204))
    print(f"  Status: {status} {'PASS' if status == 204 else 'FAIL'}\n")

# ==================== MODULE 3: MEMBERS ====================
print("[MODULE 3] MEMBERS")
print("-" * 90)

member_results = []

# 1. Register Member - create NEW USER, login with that user, then register as member  
print("Testing: Create new user, login, then POST /api/v1/members/register")

# Create unique user with timestamp to ensure fresh registration
unique_email = f"member.reg.{int(time.time() * 1000)}@ex.com"
unique_pass = "MemberPass123!"
user_result, user_status, _ = test_endpoint("POST", "/api/v1/users", {
    "email": unique_email,
    "password": unique_pass,
    "first_name": "Member",
    "last_name": f"Test{timestamp}",
    "organization_id": "org123"
}, access_token)

if user_status == 201:
    # Login with the new user to get their token
    login_result, login_status, _ = test_endpoint("POST", "/api/v1/auth/login", {
        "email": unique_email,
        "password": unique_pass
    })
    
    if login_status == 200:
        new_token = login_result.get('token', {}).get('access_token')
        # Now register this fresh user as a member using their own token
        result, status, error = test_endpoint("POST", "/api/v1/members/register", {
            "email": unique_email,
            "first_name": "Member",
            "last_name": f"Test{timestamp}",
            "membership_tier": "standard",
            "phone": f"+2341234{timestamp}",
            "expiry_months": 12
        }, new_token)
    else:
        result, status = {"detail": "Login failed"}, 401
else:
    result, status = {"detail": "User creation failed"}, user_status

print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}")
if status != 201:
    print(f"  Error Response: {result}")
member_results.append(("Register Member", status == 201))
member_id = result.get('id') if status == 201 else None
print()

# 2. List Members
print("Testing: GET /api/v1/members")
result, status, error = test_endpoint("GET", "/api/v1/members?skip=0&limit=10", token=access_token)
member_results.append(("List Members", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# 3. Get Member by ID
if member_id:
    print("Testing: GET /api/v1/members/{id}")
    result, status, error = test_endpoint("GET", f"/api/v1/members/{member_id}", token=access_token)
    member_results.append(("Get Member", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 4. Update Member
    print("Testing: PUT /api/v1/members/{id}/profile")
    result, status, error = test_endpoint("PUT", f"/api/v1/members/{member_id}/profile", {
        "bio": "Updated bio"
    }, access_token)
    member_results.append(("Update Profile", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 5. Renew Membership
    print("Testing: POST /api/v1/members/{id}/renew")
    result, status, error = test_endpoint("POST", f"/api/v1/members/{member_id}/renew", {
        "months": 12
    }, access_token)
    member_results.append(("Renew", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# ==================== MODULE 4: MEETINGS ====================
print("[MODULE 4] MEETINGS")
print("-" * 90)

meeting_results = []

# 1. Create Meeting - use Python datetime objects (they serialize to ISO format)
print("Testing: POST /api/v1/meetings")
meeting_start = datetime.now() + timedelta(days=7)
meeting_end = datetime.now() + timedelta(days=7, hours=2)
result, status, error = test_endpoint("POST", "/api/v1/meetings", {
    "title": f"Test Meeting {timestamp}",
    "meeting_type": "GENERAL_ASSEMBLY",
    "is_virtual": False,
    "scheduled_start_at": meeting_start,
    "scheduled_end_at": meeting_end,
    "requires_approval": False
}, access_token)
print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}")
if status != 201:
    print(f"  Error Response: {result}")
meeting_results.append(("Create Meeting", status == 201))
meeting_id = result.get('id') if status == 201 else None
print()

if meeting_id:
    # 2. Get Meeting
    print("Testing: GET /api/v1/meetings/{id}")
    result, status, error = test_endpoint("GET", f"/api/v1/meetings/{meeting_id}", token=access_token)
    meeting_results.append(("Get Meeting", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 3. List Meetings
    print("Testing: GET /api/v1/meetings")
    result, status, error = test_endpoint("GET", "/api/v1/meetings?skip=0&limit=10", token=access_token)
    meeting_results.append(("List Meetings", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 4. Start Meeting
    print("Testing: POST /api/v1/meetings/{id}/start")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/start", token=access_token)
    meeting_results.append(("Start Meeting", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 5. Add Attendee
    print("Testing: POST /api/v1/meetings/{id}/attendees")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/attendees", {
        "member_id": "m1",
        "email": "attendee@ex.com",
        "first_name": "Test",
        "last_name": "Attendee"
    }, access_token)
    meeting_results.append(("Add Attendee", status == 201))
    print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}\n")

    # 6. Check-in Attendee
    print("Testing: POST /api/v1/meetings/{id}/attendees/{aid}/check-in")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/check-in", token=access_token)
    meeting_results.append(("Check-in", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 7. Mark Attendance
    print("Testing: POST /api/v1/meetings/{id}/attendees/{aid}/mark-attendance")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/mark-attendance", {
        "status": "PRESENT"
    }, access_token)
    meeting_results.append(("Mark Attendance", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 8. Add Approver
    print("Testing: POST /api/v1/meetings/{id}/approvers")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/approvers", {
        "member_id": "a1",
        "email": "approver@ex.com",
        "first_name": "Approver",
        "last_name": "User"
    }, access_token)
    meeting_results.append(("Add Approver", status == 201))
    print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}\n")

    # 9. Approve Meeting
    print("Testing: POST /api/v1/meetings/{id}/approve/{aid}")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/approve/a1", token=access_token)
    meeting_results.append(("Approve", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 10. End Meeting
    print("Testing: POST /api/v1/meetings/{id}/end")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/end", token=access_token)
    meeting_results.append(("End Meeting", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

    # 11. Set Minutes
    print("Testing: POST /api/v1/meetings/{id}/minutes")
    result, status, error = test_endpoint("POST", f"/api/v1/meetings/{meeting_id}/minutes", {
        "minutes": "Meeting notes and action items"
    }, access_token)
    meeting_results.append(("Set Minutes", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}\n")

# ==================== FINAL SUMMARY ====================
print("\n" + "=" * 90)
print("FINAL TEST SUMMARY")
print("=" * 90)

def calc_percentage(results):
    if not results:
        return 0
    passed = sum(1 for _, success in results if success)
    return (passed / len(results)) * 100

auth_passed = sum(1 for _, success in auth_results if success)
user_passed = sum(1 for _, success in user_results if success)
member_passed = sum(1 for _, success in member_results if success)
meeting_passed = sum(1 for _, success in meeting_results if success)

print(f"\nAuth:     {auth_passed}/{len(auth_results):2} PASSED ({calc_percentage(auth_results):>5.1f}%)")
for name, success in auth_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

print(f"\nUsers:    {user_passed}/{len(user_results):2} PASSED ({calc_percentage(user_results):>5.1f}%)")
for name, success in user_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

print(f"\nMembers:  {member_passed}/{len(member_results):2} PASSED ({calc_percentage(member_results):>5.1f}%)")
for name, success in member_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

print(f"\nMeetings: {meeting_passed}/{len(meeting_results):2} PASSED ({calc_percentage(meeting_results):>5.1f}%)")
for name, success in meeting_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

total_tests = len(auth_results) + len(user_results) + len(member_results) + len(meeting_results)
total_passed = auth_passed + user_passed + member_passed + meeting_passed

print("\n" + "-" * 90)
print(f"TOTAL:   {total_passed}/{total_tests} PASSED ({(total_passed/total_tests*100):.1f}%)")
print("=" * 90 + "\n")

if total_passed == total_tests:
    print("STATUS: ALL ENDPOINTS WORKING PERFECTLY!")
else:
    print(f"STATUS: {total_passed} tests passing, {total_tests - total_passed} tests failing")

print("\n" + "=" * 90 + "\n")
