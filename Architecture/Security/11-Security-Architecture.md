# Security Architecture
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Security Overview

NANS follows a **defense-in-depth** security model with multiple layers of protection across infrastructure, application, and data layers.

---

## 2. Authentication Architecture

### 2.1 Authentication Methods

#### Multi-Factor Authentication (MFA)

```
MFA Methods Supported:
├── TOTP (Time-based One-Time Password)
│   ├── Authenticator app (Google Authenticator, Authy)
│   ├── 6-digit code, 30-second expiration
│   ├── Backup codes generated
│   └── Recommended: Primary method
│
├── SMS-based OTP
│   ├── SMS delivery via Twilio
│   ├── 6-digit code, 5-minute expiration
│   ├── Rate limited (3 attempts)
│   └── Fallback option
│
├── Email-based OTP
│   ├── Magic link via email
│   ├── 24-hour expiration
│   ├── Single-use token
│   └── Least secure, last resort
│
└── Hardware Security Keys
    ├── FIDO2 / WebAuthn support
    ├── USB keys supported
    └── Most secure option
```

#### OAuth 2.0 / OpenID Connect Integration

```
Supported Providers:
├── Google OAuth
│   ├── Scope: email, profile
│   ├── Auto-link existing accounts
│   └── Redirect URI: /auth/google/callback
│
├── Microsoft OAuth
│   ├── Scope: email, profile
│   ├── Tenant: any-org
│   └── Redirect URI: /auth/microsoft/callback
│
├── Custom OAuth Provider
│   ├── Internal identity provider
│   ├── SAML support (enterprise)
│   └── Custom attributes mapping
│
└── Social Logins
    ├── GitHub (for internal tools)
    ├── LinkedIn (future)
    └── Apple ID (future)
```

### 2.2 Token Management

```
JWT (JSON Web Token) Structure:
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_id",
    "org": "organization_id",
    "roles": ["admin", "member"],
    "permissions": [...],
    "iat": 1234567890,
    "exp": 1234571490,
    "iss": "nans-auth-service",
    "aud": "nans-api"
  },
  "signature": "..."
}

Token Lifecycle:
├── Access Token
│   ├── Lifetime: 15 minutes
│   ├── Stored: Memory (frontend) or httpOnly cookie
│   ├── Usage: API requests (Authorization header)
│   └── Scope: Limited permissions
│
├── Refresh Token
│   ├── Lifetime: 30 days
│   ├── Stored: httpOnly, Secure, SameSite=Strict cookie
│   ├── Usage: Refresh endpoint only
│   ├── Rotation: New token on each refresh
│   └── Revocation: Logout, password change, security incident
│
└── Session Token
    ├── Lifetime: 12 hours
    ├── Stored: Redis (server-side)
    ├── Usage: Desktop web app sessions
    └── Invalidation: On logout
```

### 2.3 Password Security

```
Password Policy:
├── Minimum length: 12 characters
├── Must contain:
│   ├── Uppercase letters (A-Z)
│   ├── Lowercase letters (a-z)
│   ├── Numbers (0-9)
│   └── Special characters (!@#$%^&*)
│
├── Cannot contain:
│   ├── Username
│   ├── Email address
│   ├── Common patterns (password123, etc)
│   └── Previously used passwords (last 5)
│
├── Expiration: None (modern practice)
├── Complexity check: zxcvbn library
└── Breach check: HaveIBeenPwned API

Password Hashing:
├── Algorithm: Argon2id
├── Memory cost: 19 MB
├── Time cost: 2 iterations
├── Parallelism: 1
├── Salt: Auto-generated (16 bytes)
└── Verification: Constant-time comparison
```

---

## 3. Authorization Architecture

### 3.1 Role-Based Access Control (RBAC)

```
RBAC Implementation:
├── User has multiple Roles
├── Role has multiple Permissions
├── Permission scoped to Resource Type
│
Permission Check:
1. Extract user roles from JWT
2. Load role permissions from cache (Redis)
3. Check if permission exists in role
4. Verify resource scope (organization, personal, etc)
5. Allow or Deny access

Example:
User: alice@nans.org
Roles:
├── National Admin (National scope)
└── Chapter Coordinator (Chapter scope)

Attempting to: View meeting in Chapter A
├── Permission: meeting:view
├── Scope: Chapter A
├── Check: National Admin has any:* → Allow
         Chapter Coordinator in Chapter A → Allow
│
Result: ✓ Allowed
```

### 3.2 Attribute-Based Access Control (ABAC)

```
ABAC Conditions:
├── Time-based
│   ├── Access only during business hours
│   ├── Access only before meeting date
│   └── Seasonal access restrictions
│
├── Location-based
│   ├── IP whitelist/blacklist
│   ├── Country-based access
│   └── VPN requirement
│
├── Device-based
│   ├── Trusted device list
│   ├── Device fingerprint validation
│   └── Mobile app only restrictions
│
├── Risk-based
│   ├── Unusual login location
│   ├── Impossible travel detection
│   ├── Multiple failed attempts
│   └── Trigger MFA challenge
│
└── Context-based
    ├── Data sensitivity level
    ├── User department/role
    ├── Action frequency
    └── Bulk operation detection
```

---

## 4. Data Security

### 4.1 Encryption at Rest

```
Database Encryption:
├── MongoDB Encryption at Rest (EE)
│   ├── Algorithm: AES-256-GCM
│   ├── Key management: AWS KMS or on-prem Vault
│   ├── Enabled for all databases
│   ├── Key rotation: Quarterly
│   └── Data automatically encrypted
│
├── File Storage Encryption (S3):
│   ├── Algorithm: AES-256
│   ├── Bucket encryption: Enabled
│   ├── Key management: AWS KMS
│   ├── SSE (Server-Side Encryption): Default
│   └── Customer-provided keys: Supported
│
├── Field-Level Encryption (PII):
│   ├── SSN/Tax ID fields
│   ├── Payment card data
│   ├── Personal health information
│   ├── Home address (if sensitive)
│   └── Encrypted separately from database

Backup Encryption:
├── Daily backups to S3
├── Encrypted with different key
├── Long-term retention in Glacier
├── Key escrow for disaster recovery
└── Separate key access control
```

### 4.2 Encryption in Transit

```
TLS Configuration:
├── Minimum version: TLS 1.2
├── Recommended: TLS 1.3 (where available)
├── Certificate: SHA-256
├── Key exchange: ECDHE (Perfect Forward Secrecy)
│
Certificate Management:
├── Provider: Let's Encrypt / AWS Certificate Manager
├── Duration: 3 months (auto-renew at 60 days)
├── SANs: All domain variations
├── HSTS: Enabled, max-age: 31536000 seconds
│
Ciphers:
├── Preferred:
│   ├── TLS_AES_256_GCM_SHA384 (TLS 1.3)
│   ├── ECDHE-ECDSA-AES256-GCM-SHA384
│   └── ECDHE-RSA-AES256-GCM-SHA384
│
├── Acceptable:
│   ├── ECDHE-ECDSA-CHACHA20-POLY1305
│   └── ECDHE-RSA-CHACHA20-POLY1305
│
└── Disabled:
    ├── RC4
    ├── DES
    ├── MD5
    └── Null ciphers
```

### 4.3 API Data Security

```
API Request/Response:
├── Content-Type: application/json
├── Charset: utf-8
├── Compression: gzip (if size > 1KB)
│
Request Security:
├── Content-Security-Policy header
├── X-Frame-Options: DENY
├── X-Content-Type-Options: nosniff
├── X-XSS-Protection: 1; mode=block
├── Strict-Transport-Security: HSTS
│
Response Sanitization:
├── No sensitive data in URLs
├── No credential leakage in error messages
├── Minimal stack traces in production
├── UUID instead of sequential IDs
└── Timestamp obfuscation (if needed)
```

---

## 5. Infrastructure Security

### 5.1 Network Security

```
Network Architecture:
├── VPC with public/private subnets
├── Internet Gateway (public subnet)
├── NAT Gateway (private subnet outbound)
├── No direct internet access for data tier
│
Security Groups:
├── ALB: 
│   ├── Inbound: 80, 443 from 0.0.0.0/0
│   ├── Outbound: All to backend security group
│   └── HTTP → HTTPS redirect
│
├── API Servers:
│   ├── Inbound: 8000, 8001 from ALB
│   ├── Outbound: HTTPS (443) to external services
│   └── Outbound: 27017 (MongoDB)
│
├── MongoDB:
│   ├── Inbound: 27017 from API security group
│   ├── Outbound: None required
│   └── Backup: Outbound to S3 (STS endpoint)
│
├── Redis:
│   ├── Inbound: 6379 from API security group
│   ├── Outbound: None required
│   └── Replication: Between Redis nodes
│
└── Bastion Host (optional):
    ├── Inbound: 22 (SSH) from admin IPs only
    ├── Outbound: 22 to all internal servers
    └── Session recording enabled
```

### 5.2 DDoS Protection

```
Protection Layers:
├── AWS Shield Standard
│   ├── Automatic DDoS mitigation
│   ├── Protection up to layer 3/4
│   ├── No cost, enabled by default
│   └── 24/7 monitoring
│
├── AWS Shield Advanced (or equivalent)
│   ├── Layer 7 (application) protection
│   ├── Real-time attack notifications
│   ├── DDoS cost protection
│   ├── AWS WAF integration
│   └── Recommended for production
│
├── Rate Limiting (API Gateway)
│   ├── Global: 10,000 req/min per account
│   ├── Per User: 1,000 req/min per API key
│   ├── Per IP: 500 req/min per IP
│   ├── Per Path: Configurable per endpoint
│   └── Enforcement: 429 Too Many Requests
│
└── Capacity Planning
    ├── Baseline capacity: 100 Gbps
    ├── Scalable to: 1,000+ Gbps
    ├── Geographic distribution
    └── Multi-region failover
```

### 5.3 Web Application Firewall (WAF)

```
AWS WAF Rules:
├── IP Reputation
│   ├── Block known malicious IPs
│   ├── GeoIP blocking (if needed)
│   └── Automatic updates
│
├── Rule Groups:
│   ├── Core rule set (OWASP Top 10)
│   ├── Known bad inputs
│   ├── SQL Injection protection
│   ├── XSS protection
│   └── Custom patterns
│
├── Rate Limiting:
│   ├── 2,000 requests per 5 minutes per IP
│   ├── 1,000 requests per 5 minutes per API key
│   └── Escalation: Temporary block
│
├── Logging:
│   ├── All requests logged (if enabled)
│   ├── Stored in S3 for analysis
│   ├── 30-day retention
│   └── CloudWatch integration
│
└── Testing:
    ├── Rule testing in count mode first
    ├── Monitor false positives
    ├── Gradually enable blocking
    └── Continuous tuning
```

---

## 6. Application Security

### 6.1 Input Validation

```
Validation Strategy:
├── Whitelist approach (allow specific formats)
├── Length limits enforced
├── Type checking (email, phone, date)
├── Pattern matching (regex)
├── Schema validation (Pydantic)
│
Validation Examples:
├── Email: RFC 5322 + DNS check
├── Phone: E.164 format
├── Date: ISO 8601 format
├── UUID: RFC 4122 format
├── Enum: Predefined values only
├── Range: Min/max numeric values
├── File upload: Type, size, scan
│
Error Handling:
├── Generic error messages (no data leakage)
├── Log detailed errors server-side
├── No stack traces to client
├── Consistent error format
└── Localized error messages
```

### 6.2 Output Encoding

```
Encoding by Context:
├── HTML Context:
│   ├── & → &amp;
│   ├── < → &lt;
│   ├── > → &gt;
│   ├── " → &quot;
│   └── ' → &#x27;
│
├── JSON Context:
│   ├── Quote strings
│   ├── Escape backslashes
│   ├── No raw HTML allowed
│   └── Use JSON.stringify()
│
├── URL Context:
│   ├── Use URL encoding
│   ├── %XX format for special chars
│   └── Use encodeURIComponent()
│
└── CSS/JavaScript Context:
    ├── CSS values quoted/escaped
    ├── No inline scripts allowed (CSP)
    └── No eval() usage
```

### 6.3 SQL Injection Prevention

```
Prevention Mechanisms:
├── Parameterized Queries
│   ├── Beanie ODM uses parameterization
│   ├── Never construct queries with strings
│   ├── MongoDB uses BSON format
│   └── No string concatenation
│
├── ORMs (Object-Relational Mapping)
│   ├── Beanie ODM handles escaping
│   ├── Type safety at compile time
│   ├── Query validation
│   └── Automatic sanitization
│
└── Input Validation
    ├── Validate expected format
    ├── Reject invalid input early
    ├── Whitelist allowed characters
    └── Fail securely (deny by default)

Example (Safe):
```python
# Using Beanie ODM
user = await User.find(User.email == email).first()

# Using parameterization (if needed)
user = await db.users.find_one({"email": email})

# Never do this (UNSAFE):
query_string = f"SELECT * FROM users WHERE email = '{email}'"
```
```

### 6.4 Cross-Site Scripting (XSS) Prevention

```
Content Security Policy (CSP):
├── Header: Content-Security-Policy
├── Directives:
│   ├── default-src 'self'
│   ├── script-src 'self' 'nonce-{random}'
│   ├── style-src 'self' 'nonce-{random}'
│   ├── img-src 'self' data: https:
│   ├── font-src 'self'
│   ├── frame-ancestors 'none'
│   ├── base-uri 'self'
│   ├── form-action 'self'
│   └── upgrade-insecure-requests
│
├── Nonce-based Scripts:
│   ├── Random nonce per request
│   ├── Included in <script> tag
│   ├── Matches CSP header nonce
│   └── Prevents inline script injection
│
├── No Inline Scripts:
│   ├── All scripts external files
│   ├── Event handlers via JS only
│   ├── Data in HTML attributes minimal
│   └── Server-side templating secure
│
└── DOM-based XSS Prevention:
    ├── React's JSX escaping by default
    ├── Never use dangerouslySetInnerHTML
    ├── Use textContent instead of innerHTML
    └── Sanitize user-provided HTML (DOMPurify)
```

### 6.5 Cross-Site Request Forgery (CSRF) Prevention

```
CSRF Protection:
├── Token-based Protection:
│   ├── Generate random token per session
│   ├── Store in server session (Redis)
│   ├── Include in form/request body
│   ├── Verify on state-changing requests
│   └── SameSite cookies as backup
│
├── SameSite Cookie Attribute:
│   ├── Strict: Never send in cross-site requests
│   ├── Lax: Send for top-level navigation only
│   ├── None: Send always (with Secure flag)
│   └── Default: Lax (modern browsers)
│
├── Double Submit Pattern:
│   ├── Verify token in body matches cookie
│   ├── Cookie set HttpOnly
│   ├── Token in request body
│   └── Mismatch = Reject request
│
└── Safe Methods Only:
    ├── GET: No state change (idempotent)
    ├── POST/PUT/DELETE: Require CSRF token
    ├── HEAD: No state change
    └── OPTIONS: No token needed
```

---

## 7. Access Logging and Monitoring

### 7.1 Security Logging

```
Events Logged:
├── Authentication:
│   ├── Successful login
│   ├── Failed login (details redacted)
│   ├── MFA success/failure
│   ├── Password change
│   ├── Token refresh
│   └── Logout
│
├── Authorization:
│   ├── Permission granted
│   ├── Permission denied
│   ├── Role assignment
│   ├── Role revocation
│   └── Permission escalation
│
├── Data Access:
│   ├── Data read (sensitive fields)
│   ├── Data modification
│   ├── Data deletion
│   ├── Bulk operations
│   └── Export requests
│
├── Security Events:
│   ├── Failed validation
│   ├── Suspicious patterns
│   ├── Rate limit violations
│   ├── Account lockout
│   ├── MFA changes
│   └── Password reset requests
│
└── Infrastructure:
    ├── Service restart
    ├── Configuration changes
    ├── Certificate expiration warning
    ├── Backup success/failure
    └── Disaster recovery events

Log Format:
```json
{
  "timestamp": "2026-06-23T10:30:45.123Z",
  "event_type": "authentication.login",
  "user_id": "user123",
  "email": "user@example.com",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "result": "success",
  "mfa_method": "totp",
  "location": "US, NY",
  "device_fingerprint": "abcd1234...",
  "session_id": "sess_xyz"
}
```

Log Retention:
├── Active logs: 90 days (ELK Stack)
├── Archive logs: 7 years (S3 Glacier)
├── Audit trail: Immutable (MongoDB append-only)
└── Search capability: Full-text on active logs
```

### 7.2 Security Monitoring and Alerting

```
Real-time Alerts:
├── Multiple failed login attempts
│   ├── Threshold: 5 failures in 10 minutes
│   ├── Action: Account lockout (30 minutes)
│   └── Alert: Security team notified
│
├── Suspicious geographic access
│   ├── Impossible travel (distance > 900km/hour)
│   ├── Action: MFA challenge/logout
│   └── Alert: User + Security team
│
├── Bulk data exports
│   ├── Threshold: > 10,000 records
│   ├── Action: Admin approval required
│   └── Alert: Audit team
│
├── Permission changes
│   ├── Immediate notification
│   ├── Action: Log for audit
│   └── Alert: Affected user
│
├── API rate limit violations
│   ├── Threshold: > 500 errors in 5 min
│   ├── Action: Temporary IP block
│   └── Alert: Operations team
│
└── SSL certificate expiration
    ├── Warning: 30 days before expiry
    ├── Alert: Operations team
    └── Auto-renewal: 60 days before expiry

Alerting Channels:
├── Critical: PagerDuty + SMS + Email
├── High: Slack + Email
├── Medium: Slack
└── Low: Dashboard only
```

---

## 8. Vulnerability Management

### 8.1 Dependency Scanning

```
Tools Used:
├── Dependabot (GitHub)
│   ├── Scans dependencies weekly
│   ├── Auto-updates patch versions
│   ├── PR for minor/major versions
│   └── Security alerts immediate
│
├── Snyk
│   ├── Vulnerability database
│   ├── License compliance
│   ├── Code scanning
│   └── Prioritized remediation
│
└── npm/pip audit
    ├── Local scans before commit
    ├── CI/CD pipeline integration
    ├── Blocks deployment on critical
    └── Reports to Security Dashboard

Update Policy:
├── Critical: Within 24 hours
├── High: Within 1 week
├── Medium: Within 2 weeks
├── Low: Within 1 month
└── Informational: No deadline
```

### 8.2 Code Security Scanning

```
Tools Used:
├── SonarQube
│   ├── Code quality metrics
│   ├── Security hotspots detection
│   ├── OWASP Top 10 checks
│   └── CWE mapping
│
├── Bandit (Python)
│   ├── Security issues in Python code
│   ├── Plugin framework
│   ├── CI/CD integration
│   └── Baseline for known issues
│
├── ESLint (JavaScript)
│   ├── Security plugins
│   ├── Best practices
│   ├── Type checking (TypeScript)
│   └── Pre-commit hooks

Scanning Frequency:
├── On every commit
├── PR validation (blocks merge)
├── Nightly full scans
├── Weekly reports
└── Quarterly manual review
```

### 8.3 Penetration Testing

```
Penetration Testing Schedule:
├── Quarterly: Internal testing
│   ├── Testing scope: All components
│   ├── Focus areas: Authentication, Authorization, Data
│   ├── Report: CVSS scoring, remediation
│   └── Remediation target: 30 days
│
├── Semi-annual: Third-party testing
│   ├── Independent team
│   ├── Full system assessment
│   ├── Social engineering (opt-in)
│   └── Detailed report + remediation plan
│
└── Post-incident: Targeted testing
    ├── Within 1 week of incident
    ├── Root cause verification
    ├── Similar vulnerability scan
    └── Preventive measures validation

Testing Scope:
├── API endpoints (all verbs)
├── Authentication flows
├── Authorization checks
├── Input validation
├── SQL injection attempts
├── XSS injection attempts
├── CSRF vulnerabilities
├── File upload/download
├── Session management
├── Error handling
└── Information disclosure
```

---

## 9. Incident Response

### 9.1 Incident Classification

```
Severity Levels:

Critical (P1):
├── Active data breach in progress
├── Ransomware detected
├── Service completely unavailable
├── Large-scale unauthorized access
└── Response time: Immediate (< 15 min)

High (P2):
├── Suspected unauthorized access (isolated)
├── Significant functionality impaired
├── Malware detected in system
├── Data integrity compromise
└── Response time: 1 hour

Medium (P3):
├── Minor unauthorized access
├── Partial functionality loss
├── Suspicious activity detected
├── Failed intrusion attempt
└── Response time: 4 hours

Low (P4):
├── Informational security issues
├── Policy violations
├── Configuration drift
└── Response time: 1 business day
```

### 9.2 Incident Response Procedure

```
1. Detection & Alerting
   ├── Automated alerts (SIEM)
   ├── User reports
   ├── Third-party notifications
   └── Regular monitoring

2. Triage
   ├── Assess severity
   ├── Determine impact scope
   ├── Activate response team
   └── Create incident ticket

3. Containment
   ├── Isolate affected systems
   ├── Block attacker access
   ├── Preserve evidence
   ├── Notify stakeholders
   └── Begin communication plan

4. Investigation
   ├── Gather logs and evidence
   ├── Timeline reconstruction
   ├── Identify root cause
   ├── Assess impact/exposure
   └── Determine remediation

5. Remediation
   ├── Patch vulnerabilities
   ├── Remove attacker access
   ├── Reset credentials
   ├── Restore from backups
   └── Verify clean state

6. Recovery
   ├── Restore service
   ├── Verify functionality
   ├── Monitor closely
   ├── Document changes
   └── Communicate resolution

7. Post-Incident
   ├── Conduct postmortem
   ├── Identify lessons learned
   ├── Update procedures
   ├── Implement preventive measures
   └── Track remediation
```

---

## 10. Compliance and Auditing

### 10.1 Compliance Frameworks

```
Compliance Requirements:

GDPR (General Data Protection Regulation):
├── Legal basis for processing
├── Consent management
├── Right to access
├── Right to erasure
├── Data portability
├── Privacy by design
└── Data protection officer

CCPA (California Consumer Privacy Act):
├── Right to know
├── Right to delete
├── Right to opt-out
├── Non-discrimination
├── Privacy policy clarity
└── Third-party audit annually

SOC 2 Type II:
├── Security controls
├── Availability & performance
├── Processing integrity
├── Confidentiality
├── Privacy commitments
└── 12-month audit period
```

### 10.2 Audit Trail

```
Immutable Audit Log:
├── Append-only MongoDB collection
├── Cryptographic hash chaining
├── Tamper detection
├── No deletion/modification
├── Retention: 7 years minimum
├── Encryption: AES-256 at rest
├── Searchable: Indexed by user, action, timestamp
└── Exportable: PDF/CSV for compliance

Audit Log Contents:
├── User ID & email
├── Action performed
├── Resource affected
├── Before state (if modification)
├── After state (if modification)
├── IP address & user agent
├── Timestamp (UTC)
├── Request ID (tracing)
└── Status (success/failure)
```

