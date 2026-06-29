import json
import urllib.request
import urllib.error
from datetime import datetime

BASE_URL = "http://localhost:8000"


def request_endpoint(method, path, data=None, headers=None):
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=req_data,
        headers=req_headers,
        method=method
    )
    try:
        response = urllib.request.urlopen(req)
        body = response.read().decode()
        result = json.loads(body) if body else {}
        return result, response.status
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return json.loads(body), e.code
        except Exception:
            return {"error": body}, e.code


def get_token():
    data = {"email": "test@example.com", "password": "TestPassword123!"}
    result, status = request_endpoint("POST", "/api/v1/auth/login", data)
    assert status == 200, f"Login failed: {status} {result}"
    token_data = result.get("token") or {}
    if isinstance(token_data, dict):
        return token_data.get("access_token") or token_data.get("accessToken")
    return token_data


def test_member_registration_photo_upload():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    timestamp = int(datetime.now().timestamp())
    email = f"member{timestamp}@example.com"

    registration_data = {
        "membership_number": f"MEM{timestamp}",
        "email": email,
        "first_name": "Photo",
        "last_name": "Tester",
        "tier": "STANDARD",
        "phone": "+2341234567890"
    }

    result, status = request_endpoint("POST", "/api/v1/members/register", registration_data, headers)
    if status == 201:
        member_id = result.get("id")
        assert member_id, "Registered member response missing id"
    else:
        assert status == 409, f"Unexpected member registration error: {status} {result}"
        assert "already exists" in str(result.get("detail", "")).lower()
        member_id = None

    # Upload profile photo through auth endpoint
    photo_content = b"\x89PNG\r\n\x1a\n" + b"0" * 1024
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = []
    body.append(f"--{boundary}")
    body.append('Content-Disposition: form-data; name="photo"; filename="passport.png"')
    body.append('Content-Type: image/png\r\n')
    body.append(photo_content.decode('latin1'))
    body.append(f"--{boundary}--\r\n")
    body_bytes = '\r\n'.join(body).encode('latin1')

    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/auth/me/photo",
        data=body_bytes,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )
    response = urllib.request.urlopen(req)
    upload_result = json.loads(response.read().decode())
    assert response.status == 200, f"Photo upload failed: {response.status} {upload_result}"
    assert upload_result.get("url"), "Photo upload response missing url"

    # Verify current user profile includes profile_photo_url
    profile_result, profile_status = request_endpoint("GET", "/api/v1/auth/me", None, headers)
    assert profile_status == 200, f"Get profile failed: {profile_status} {profile_result}"
    profile_url = profile_result.get("profilePhotoUrl") or profile_result.get("profile_photo_url")
    assert profile_url, "Profile photo URL was not saved to user record"

    print("Member registration with photo upload succeeded. Photo URL was saved.")
