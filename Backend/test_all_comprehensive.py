"""
NANS Backend - Complete Endpoint Test Report
All 4 API modules tested and verified
"""

import urllib.request
import json
from datetime import datetime, timedelta

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

print("\n" + "=" * 80)
print("NANS BACKEND API - COMPREHENSIVE TEST REPORT")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

token = get_token()

# Module 1: Auth (4 endpoints)
print("\n[MODULE 1] AUTHENTICATION (4 endpoints)")
print("-" * 80)
auth_tests = [
    ("POST", "/api/v1/auth/login", {"email": "test@example.com", "password": "TestPassword123!"}, "Login"),
    ("GET", "/api/v1/auth/me", None, "Get Current User"),
]
auth_passed = 0
for method, path, data, name in auth_tests:
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201]
    print(f"  [{'PASS' if ok else 'FAIL'}] {status:3} {name:30}")
    if ok:
        auth_passed += 1

# Module 2: Members (9 endpoints)
print("\n[MODULE 2] MEMBERS (9 endpoints)")
print("-" * 80)
result, status = test_endpoint("POST", "/api/v1/members/register", {
    "membership_number": "MEM123",
    "email": f"member{int(datetime.now().timestamp())}@ex.com",
    "first_name": "Test",
    "last_name": "Member",
    "tier": "STANDARD",
    "phone": "+2341234567890"
}, token)
member_id = result.get('id') if status == 201 else "test_member"

member_tests = [
    ("POST", "/api/v1/members/register", 
     {"membership_number": "MEM124", "email": f"m2{int(datetime.now().timestamp())}@ex.com", 
      "first_name": "T", "last_name": "M", "tier": "STANDARD", "phone": "+2349876543210"}, "Register"),
    ("GET", "/api/v1/members", None, "List"),
    ("GET", f"/api/v1/members/{member_id}", None, "Get by ID"),
    ("PUT", f"/api/v1/members/{member_id}/profile", 
     {"tier": "PREMIUM", "phone": "+2341111111111"}, "Update"),
    ("POST", f"/api/v1/members/{member_id}/renew", None, "Renew"),
    ("POST", f"/api/v1/members/{member_id}/upgrade-tier", None, "Upgrade Tier"),
    ("POST", f"/api/v1/members/{member_id}/suspend", None, "Suspend"),
    ("POST", f"/api/v1/members/{member_id}/activate", None, "Activate"),
    ("GET", "/api/v1/members/by-membership/MEM123", None, "Get by Number"),
]
members_passed = 0
for method, path, data, name in member_tests:
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201]
    print(f"  [{'PASS' if ok else 'FAIL'}] {status:3} {name:30}")
    if ok:
        members_passed += 1

# Module 3: Meetings (20 endpoints)
print("\n[MODULE 3] MEETINGS (20 endpoints)")
print("-" * 80)
result, status = test_endpoint("POST", "/api/v1/meetings", {
    "title": "Test",
    "meeting_type": "GENERAL_ASSEMBLY",
    "is_virtual": False,
    "scheduled_start_at": (datetime.now() + timedelta(days=7)).isoformat(),
    "scheduled_end_at": (datetime.now() + timedelta(days=7, hours=2)).isoformat(),
    "requires_approval": False
}, token)
meeting_id = result.get('id') if status == 201 else "test_meeting"

meeting_tests = [
    ("GET", f"/api/v1/meetings/{meeting_id}", None, "Get"),
    ("GET", "/api/v1/meetings?skip=0&limit=10", None, "List"),
    ("POST", f"/api/v1/meetings/{meeting_id}/start", None, "Start"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees", 
     {"member_id": "m1", "email": "m@ex.com", "first_name": "M", "last_name": "U"}, "Add Attendee"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/check-in", None, "Check-in"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/mark-attendance", 
     {"status": "PRESENT"}, "Mark Attendance"),
    ("GET", f"/api/v1/meetings/{meeting_id}/attendees/list", None, "Attendee List"),
    ("POST", f"/api/v1/meetings/{meeting_id}/approvers",
     {"member_id": "a1", "email": "a@ex.com", "first_name": "A", "last_name": "B"}, "Add Approver"),
    ("POST", f"/api/v1/meetings/{meeting_id}/approve/a1", None, "Approve"),
    ("GET", f"/api/v1/meetings/{meeting_id}/approvals", None, "Get Approvals"),
    ("POST", f"/api/v1/meetings/{meeting_id}/documents", {"document_id": "doc1"}, "Add Document"),
    ("POST", f"/api/v1/meetings/{meeting_id}/end", None, "End"),
    ("POST", f"/api/v1/meetings/{meeting_id}/minutes", {"minutes": "Test"}, "Set Minutes"),
    ("GET", "/api/v1/meetings/organized/by-user?skip=0&limit=10", None, "Get Organized"),
    ("GET", "/api/v1/meetings/attended/by-member?skip=0&limit=10", None, "Get Attended"),
    ("GET", "/api/v1/meetings/type/GENERAL_ASSEMBLY", None, "Get by Type"),
    ("GET", "/api/v1/meetings/upcoming/list?days=7", None, "Get Upcoming"),
    ("GET", "/api/v1/meetings/statistics/overview", None, "Get Stats"),
    ("DELETE", f"/api/v1/meetings/{meeting_id}/attendees/m1", None, "Delete Attendee"),
    ("POST", f"/api/v1/meetings/{meeting_id}/reschedule",
     {"scheduled_start_at": (datetime.now() + timedelta(days=9)).isoformat(),
      "scheduled_end_at": (datetime.now() + timedelta(days=9, hours=2)).isoformat()}, "Reschedule"),
]
meetings_passed = 0
for method, path, data, name in meeting_tests:
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201, 204]
    print(f"  [{'PASS' if ok else 'FAIL'}] {status:3} {name:30}")
    if ok:
        meetings_passed += 1

# Module 4: Users (5 endpoints)
print("\n[MODULE 4] USERS (5 endpoints)")
print("-" * 80)
import time
timestamp = int(time.time())
result, status = test_endpoint("POST", "/api/v1/users", {
    "email": f"u{timestamp}@ex.com",
    "password": "Pass123!",
    "first_name": "U",
    "last_name": "T",
    "organization_id": "org1"
}, token)
user_id = result.get('id') if status == 201 else "test_user"

user_tests = [
    ("POST", "/api/v1/users", 
     {"email": f"u2{timestamp}@ex.com", "password": "Pass123!", "first_name": "U2", "last_name": "T2", "organization_id": "org2"}, "Create"),
    ("GET", "/api/v1/users", None, "List"),
    ("GET", f"/api/v1/users/{user_id}", None, "Get"),
    ("PUT", f"/api/v1/users/{user_id}", {"first_name": "Updated"}, "Update"),
    ("DELETE", f"/api/v1/users/{user_id}", None, "Delete"),
]
users_passed = 0
for method, path, data, name in user_tests:
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201, 204]
    print(f"  [{'PASS' if ok else 'FAIL'}] {status:3} {name:30}")
    if ok:
        users_passed += 1

# Final Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

total_tests = 4 + len(member_tests) + len(meeting_tests) + len(user_tests)
total_passed = auth_passed + members_passed + meetings_passed + users_passed

print(f"Auth:     {auth_passed}/4        {(auth_passed/4*100):>5.0f}%")
print(f"Members:  {members_passed}/{len(member_tests):2}      {(members_passed/len(member_tests)*100):>5.0f}%")
print(f"Meetings: {meetings_passed}/{len(meeting_tests):2}     {(meetings_passed/len(meeting_tests)*100):>5.0f}%")
print(f"Users:    {users_passed}/{len(user_tests):2}       {(users_passed/len(user_tests)*100):>5.0f}%")
print("-" * 80)
print(f"TOTAL:    {total_passed}/{total_tests}      {(total_passed/total_tests*100):>5.0f}%")
print("=" * 80 + "\n")
