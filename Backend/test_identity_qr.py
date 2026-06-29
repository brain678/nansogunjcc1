"""
Comprehensive test script for Digital Identity and QR System
Tests all identity and QR endpoints
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

print("\n" + "=" * 100)
print("NANS BACKEND - DIGITAL IDENTITY & QR SYSTEM TEST")
print("=" * 100)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100 + "\n")

identity_results = []
qr_results = []

# ==================== AUTHENTICATION & USER SETUP ====================
print("[SETUP] Authentication and user creation")
print("-" * 100)

# 1. Login with test user
result, status, error = test_endpoint("POST", "/api/v1/auth/login", {
    "email": "test@example.com",
    "password": "TestPassword123!"
})
access_token = result.get('token', {}).get('access_token') if status == 200 else None
user_id = result.get('user', {}).get('id') if status == 200 else None
print(f"✓ Login: Status {status} - User ID: {user_id}\n")

if not access_token or not user_id:
    print("❌ Failed to get auth token. Cannot proceed with tests.")
    exit(1)

# ==================== IDENTITY INITIALIZATION ====================
print("[INIT] Initialize digital identity for user")
print("-" * 100)

result, status, error = test_endpoint("POST", "/api/v1/identity/initialize", {
    "role": "MEMBER",
    "institution": "University of Lagos",
    "chapter": "Lagos Chapter",
    "profile_photo_url": None
}, access_token)

if status == 201:
    print(f"✓ Identity initialized: Status {status}")
    print(f"  Membership ID: {result.get('membership_id')}")
    print(f"  QR Token: {result.get('qr_token')[:20]}...")
    print()
else:
    print(f"❌ Failed to initialize identity: Status {status}")
    if isinstance(result, dict):
        print(f"  Error: {result.get('detail', str(result))}")
    print()

# ==================== DIGITAL IDENTITY ENDPOINTS ====================
print("[MODULE 1] DIGITAL IDENTITY ENDPOINTS")
print("-" * 100)

# 1. Get digital card
print("Testing: GET /api/v1/identity/card")
result, status, error = test_endpoint("GET", "/api/v1/identity/card", token=access_token)
identity_results.append(("Get Digital Card", status == 200))
if status == 200:
    print(f"  Status: {status} PASS")
    print(f"  Membership ID: {result.get('membership_id')}")
    print(f"  Full Name: {result.get('full_name')}")
    print(f"  Role: {result.get('role')}")
    membership_id = result.get('membership_id')
    qr_token = result.get('qr_token')
else:
    print(f"  Status: {status} FAIL")
    if isinstance(result, dict) and 'detail' in result:
        print(f"  Error: {result['detail']}")
print()

# 2. Get card status
print("Testing: GET /api/v1/identity/card/status")
result, status, error = test_endpoint("GET", "/api/v1/identity/card/status", token=access_token)
identity_results.append(("Get Card Status", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
if status == 200:
    print(f"  Card Status: {result.get('card_status')}")
    print(f"  Verification Count: {result.get('verification_count')}")
print()

# 3. Regenerate QR code
print("Testing: POST /api/v1/identity/qr/regenerate")
result, status, error = test_endpoint("POST", "/api/v1/identity/qr/regenerate", token=access_token)
identity_results.append(("Regenerate QR Code", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
if status == 200:
    print(f"  New QR Token: {result.get('qr_token')[:20]}...")
    new_qr_token = result.get('qr_token')
print()

# 4. Disable card
print("Testing: POST /api/v1/identity/card/disable")
result, status, error = test_endpoint("POST", "/api/v1/identity/card/disable", token=access_token)
identity_results.append(("Disable Card", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
if status == 200:
    print(f"  Card Status: {result.get('card_status')}")
print()

# 5. Activate card
print("Testing: POST /api/v1/identity/card/activate")
result, status, error = test_endpoint("POST", "/api/v1/identity/card/activate", token=access_token)
identity_results.append(("Activate Card", status == 200))
print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
if status == 200:
    print(f"  Card Status: {result.get('card_status')}")
print()

# ==================== QR VERIFICATION ENDPOINTS ====================
print("[MODULE 2] QR VERIFICATION ENDPOINTS")
print("-" * 100)

# Get current QR token for verification
result, status, error = test_endpoint("GET", "/api/v1/identity/card", token=access_token)
current_qr_token = result.get('qr_token') if status == 200 else None

# 1. Verify QR token
if current_qr_token:
    print("Testing: POST /api/v1/qr/verify")
    result, status, error = test_endpoint("POST", "/api/v1/qr/verify", {
        "qr_token": current_qr_token
    })
    qr_results.append(("Verify QR Token", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
    if status == 200:
        print(f"  Valid: {result.get('is_valid')}")
        print(f"  Member: {result.get('full_name')}")
        print(f"  Membership ID: {result.get('membership_id')}")
        print(f"  Role: {result.get('role')}")
        print(f"  Institution: {result.get('institution')}")
    else:
        print(f"  Error: {result.get('detail') if isinstance(result, dict) else error}")
    print()

# 2. Verify invalid QR token
print("Testing: POST /api/v1/qr/verify (Invalid Token)")
result, status, error = test_endpoint("POST", "/api/v1/qr/verify", {
    "qr_token": "invalid_qr_token_00000000000000000000000000000000"
})
qr_results.append(("Verify Invalid QR", status != 200))
print(f"  Status: {status} {'PASS (correctly rejected)' if status != 200 else 'FAIL'}")
print()

# ==================== MEETING QR ENDPOINTS ====================
print("[MODULE 3] MEETING QR ENDPOINTS")
print("-" * 100)

# 1. Create meeting (for testing)
print("Testing: Create test meeting")
meeting_start = datetime.now() + timedelta(days=7)
meeting_end = datetime.now() + timedelta(days=7, hours=2)
result, status, error = test_endpoint("POST", "/api/v1/meetings", {
    "title": "QR Test Meeting",
    "meeting_type": "GENERAL_ASSEMBLY",
    "is_virtual": False,
    "scheduled_start_at": meeting_start,
    "scheduled_end_at": meeting_end,
    "requires_approval": False
}, access_token)
meeting_id = result.get('id') if status == 201 else None
print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}")
if meeting_id:
    print(f"  Meeting ID: {meeting_id}")
print()

# 2. Create meeting QR
if meeting_id:
    print("Testing: POST /api/v1/qr/meeting/create")
    result, status, error = test_endpoint("POST", "/api/v1/qr/meeting/create", {
        "meeting_id": meeting_id
    }, access_token)
    qr_results.append(("Create Meeting QR", status == 201))
    print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}")
    if status == 201:
        print(f"  QR Token: {result.get('qr_token')[:20]}...")
        print(f"  Verification URL: {result.get('verification_url')}")
        meeting_qr_token = result.get('qr_token')
    print()
    
    # 3. Check-in to meeting
    if meeting_qr_token:
        print("Testing: POST /api/v1/qr/meeting/check-in")
        result, status, error = test_endpoint("POST", "/api/v1/qr/meeting/check-in", {
            "qr_token": meeting_qr_token,
            "event_id": meeting_id
        }, access_token)
        qr_results.append(("Check-in Meeting", status == 200))
        print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
        if status == 200:
            print(f"  Attendance ID: {result.get('attendance_id')}")
            print(f"  Check-in Time: {result.get('check_in_time')}")
            print(f"  Message: {result.get('message')}")
        else:
            print(f"  Error: {result.get('detail') if isinstance(result, dict) else error}")
        print()

# ==================== ACTIVITY QR ENDPOINTS ====================
print("[MODULE 4] ACTIVITY QR ENDPOINTS")
print("-" * 100)

activity_id = f"activity_{int(time.time())}"

# 1. Create activity QR
print("Testing: POST /api/v1/qr/activity/create")
result, status, error = test_endpoint("POST", "/api/v1/qr/activity/create", {
    "activity_id": activity_id,
    "activity_name": "QR Test Workshop"
}, access_token)
qr_results.append(("Create Activity QR", status == 201))
print(f"  Status: {status} {'PASS' if status == 201 else 'FAIL'}")
if status == 201:
    print(f"  Activity ID: {result.get('activity_id')}")
    print(f"  QR Token: {result.get('qr_token')[:20]}...")
    print(f"  Verification URL: {result.get('verification_url')}")
    activity_qr_token = result.get('qr_token')
print()

# 2. Check-in to activity
if 'activity_qr_token' in locals():
    print("Testing: POST /api/v1/qr/activity/check-in")
    result, status, error = test_endpoint("POST", "/api/v1/qr/activity/check-in", {
        "qr_token": activity_qr_token,
        "event_id": activity_id
    }, access_token)
    qr_results.append(("Check-in Activity", status == 200))
    print(f"  Status: {status} {'PASS' if status == 200 else 'FAIL'}")
    if status == 200:
        print(f"  Attendance ID: {result.get('attendance_id')}")
        print(f"  Event Name: {result.get('event_name')}")
        print(f"  Check-in Time: {result.get('check_in_time')}")
        print(f"  Message: {result.get('message')}")
    else:
        print(f"  Error: {result.get('detail') if isinstance(result, dict) else error}")
    print()

# ==================== FINAL SUMMARY ====================
print("\n" + "=" * 100)
print("FINAL TEST SUMMARY")
print("=" * 100)

def calc_percentage(results):
    if not results:
        return 0
    passed = sum(1 for _, success in results if success)
    return (passed / len(results)) * 100

identity_passed = sum(1 for _, success in identity_results if success)
qr_passed = sum(1 for _, success in qr_results if success)

print(f"\nDigital Identity: {identity_passed}/{len(identity_results):2} PASSED ({calc_percentage(identity_results):>5.1f}%)")
for name, success in identity_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

print(f"\nQR System:       {qr_passed}/{len(qr_results):2} PASSED ({calc_percentage(qr_results):>5.1f}%)")
for name, success in qr_results:
    print(f"  [{('PASS' if success else 'FAIL'):4}] {name}")

total_tests = len(identity_results) + len(qr_results)
total_passed = identity_passed + qr_passed

print("\n" + "-" * 100)
print(f"TOTAL:           {total_passed}/{total_tests} PASSED ({(total_passed/total_tests*100):.1f}%)")
print("=" * 100 + "\n")

if total_passed == total_tests:
    print("✅ STATUS: ALL TESTS PASSED - IDENTITY & QR SYSTEM WORKING PERFECTLY!")
else:
    print(f"⚠️  STATUS: {total_passed} tests passing, {total_tests - total_passed} tests failing")

print("\n" + "=" * 100 + "\n")
