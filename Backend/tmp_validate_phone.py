from app.application.dtos.auth_dto import UserProfileResponse

class Phone:
    def __init__(self, value, country_code):
        self.value = value
        self.country_code = country_code
    def __str__(self):
        return self.value

p = Phone('+15550000001', '+1')
print('phone type:', type(p))
user = UserProfileResponse(
    id='1',
    email='admin@example.com',
    first_name='Admin',
    last_name='User',
    phone=p,
    roles=['admin'],
    mfa_enabled=False,
    status='active',
    created_at='2026-06-25T00:00:00Z'
)
print('created phone:', repr(user.phone))
print('phone type after:', type(user.phone))
