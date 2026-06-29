import urllib.request
import urllib.error
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
        return json.loads(response.read().decode()), response.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode()), e.code
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
print("MEETINGS MODULE - COMPREHENSIVE ENDPOINT TEST")
print("=" * 80)

token = get_token()
print("[OK] Authenticated\n")

# Create meeting
result, status = test_endpoint("POST", "/api/v1/meetings", {
    "title": "Test", "meeting_type": "GENERAL_ASSEMBLY", "is_virtual": False,
    "scheduled_start_at": (datetime.now() + timedelta(days=7)).isoformat(),
    "scheduled_end_at": (datetime.now() + timedelta(days=7, hours=2)).isoformat(),
    "requires_approval": False
}, token)
meeting_id = result.get('id') if status == 201 else None

# Corrected test order
tests = [
    ("GET", f"/api/v1/meetings/{meeting_id}", None, "1. Get meeting"),
    ("GET", "/api/v1/meetings?skip=0&limit=10", None, "2. List meetings"),
    ("POST", f"/api/v1/meetings/{meeting_id}/start", None, "3. START meeting"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees", 
     {"member_id": "m1", "email": "t@ex.com", "first_name": "Test", "last_name": "User"}, 
     "4. Add attendee"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/check-in", None, "5. Check-in"),
    ("POST", f"/api/v1/meetings/{meeting_id}/attendees/m1/mark-attendance", 
     {"status": "PRESENT"}, "6. Mark attendance"),
    ("GET", f"/api/v1/meetings/{meeting_id}/attendees/list", None, "7. Attendance list"),
    ("POST", f"/api/v1/meetings/{meeting_id}/approvers",
     {"member_id": "a1", "email": "a@ex.com", "first_name": "Approver", "last_name": "One"}, 
     "8. Add approver"),
    ("POST", f"/api/v1/meetings/{meeting_id}/approve/a1", None, "9. Approve"),
    ("GET", f"/api/v1/meetings/{meeting_id}/approvals", None, "10. Get approvals"),
    ("POST", f"/api/v1/meetings/{meeting_id}/documents", {"document_id": "doc1"}, "11. Add document"),
    ("POST", f"/api/v1/meetings/{meeting_id}/end", None, "12. END meeting (BEFORE MINUTES!)"),
    ("POST", f"/api/v1/meetings/{meeting_id}/minutes", {"minutes": "Test notes"}, "13. SET MINUTES (AFTER END)"),
    ("GET", "/api/v1/meetings/organized/by-user?skip=0&limit=10", None, "14. Get organized"),
    ("GET", "/api/v1/meetings/attended/by-member?skip=0&limit=10", None, "15. Get attended"),
    ("GET", "/api/v1/meetings/type/GENERAL_ASSEMBLY?skip=0&limit=10", None, "16. Get by type"),
    ("GET", "/api/v1/meetings/upcoming/list?days=7", None, "17. Get upcoming"),
    ("GET", "/api/v1/meetings/statistics/overview", None, "18. Get statistics"),
    ("DELETE", f"/api/v1/meetings/{meeting_id}/attendees/m1", None, "19. Delete attendee"),
    ("POST", f"/api/v1/meetings/{meeting_id}/reschedule",
     {"scheduled_start_at": (datetime.now() + timedelta(days=9)).isoformat(),
      "scheduled_end_at": (datetime.now() + timedelta(days=9, hours=2)).isoformat()}, 
     "20. Reschedule"),
]

passed = 0
failed = 0

for method, path, data, name in tests:
    result, status = test_endpoint(method, path, data, token)
    ok = status in [200, 201, 204]
    print(f"[{'PASS' if ok else 'FAIL'}] {name:50} {status}")
    if ok:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed}/{passed+failed} PASSED ({(passed/(passed+failed)*100):.0f}%)")
print("=" * 80)
