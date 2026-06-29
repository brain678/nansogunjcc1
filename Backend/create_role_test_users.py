import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"
CREATE_USER_PATH = "/api/v1/users"
LOGIN_PATH = "/api/v1/auth/login"

ROLE_ACCOUNTS = [
    {
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "first_name": "Admin",
        "last_name": "User",
        "phone": "+15550000001",
        "organization_id": "org1",
        "roles": ["admin"]
    },
    {
        "email": "secretary@example.com",
        "password": "SecretaryPass123!",
        "first_name": "General",
        "last_name": "Secretary",
        "phone": "+15550000002",
        "organization_id": "org1",
        "roles": ["general_secretary"]
    },
    {
        "email": "chairman@example.com",
        "password": "ChairmanPass123!",
        "first_name": "Chair",
        "last_name": "Man",
        "phone": "+15550000003",
        "organization_id": "org1",
        "roles": ["chairman"]
    },
    {
        "email": "member@example.com",
        "password": "MemberPass123!",
        "first_name": "Regular",
        "last_name": "Member",
        "phone": "+15550000004",
        "organization_id": "org1",
        "roles": ["member"]
    }
]


def send_request(path, method="POST", data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode()
            return json.loads(body) if body else {}, response.status
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode()
            return json.loads(body) if body else {}, exc.code
        except Exception:
            return {"error": "http_error", "message": str(exc)}, exc.code
    except Exception as exc:
        return {"error": "request_failed", "message": str(exc)}, None


def create_user(user_data):
    return send_request(CREATE_USER_PATH, "POST", user_data)


def login_user(email, password):
    return send_request(LOGIN_PATH, "POST", {"email": email, "password": password})


def main():
    print("Creating one user for each role...\n")
    created = []
    for account in ROLE_ACCOUNTS:
        print(f"Creating {account['email']} with roles={account['roles']}...", end=" ")
        result, status = create_user(account)
        if status == 201:
            print("OK")
            created.append((account, result))
        elif status == 400 and result.get("detail") and "already exists" in str(result.get("detail")).lower():
            print("Already exists")
            created.append((account, result))
        else:
            print(f"FAILED ({status})")
            print(json.dumps(result, indent=2))
    
    print("\nVerifying login for created accounts...\n")
    for account, _ in created:
        print(f"Logging in {account['email']}...", end=" ")
        result, status = login_user(account["email"], account["password"])
        if status == 200:
            token = result.get("token", {})
            access_token = token.get("access_token")
            refresh_token = token.get("refresh_token")
            print("OK")
            print(f"  access_token: {access_token[:40]}..." if access_token else "  access_token: missing")
            print(f"  refresh_token: {refresh_token[:40]}..." if refresh_token else "  refresh_token: missing")
        else:
            print(f"FAILED ({status})")
            print(json.dumps(result, indent=2))

    print("\nDone.")


if __name__ == "__main__":
    main()
