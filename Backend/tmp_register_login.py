import json
import urllib.request
import urllib.error
import time

BASE_URL = 'http://localhost:8000'

def send_request(path, data):
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            return json.loads(body), resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8')
        print('ERROR', exc.code, body)
        return json.loads(body) if body else {}, exc.code

if __name__ == '__main__':
    ts = int(time.time())
    email = f'testuser{ts}@example.com'
    password = 'TestPass123!'
    print('registering', email)
    reg_body, reg_status = send_request('/api/v1/auth/register', {
        'email': email,
        'firstName': 'Test',
        'lastName': 'User',
        'phone': '+15550009999',
        'password': password
    })
    print('register status', reg_status, reg_body)
    print('logging in', email)
    login_body, login_status = send_request('/api/v1/auth/login', {
        'email': email,
        'password': password
    })
    print('login status', login_status, login_body)
