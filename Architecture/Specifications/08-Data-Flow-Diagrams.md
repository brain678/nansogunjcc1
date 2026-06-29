# Data Flow Diagrams (DFD)
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Context Diagram (Level 0)

```
        ┌─────────────────┐
        │ External Users  │
        │  • Members      │
        │  • Admins       │
        │  • Public       │
        └────────┬────────┘
                 │
                 │ User Requests
                 │ Authentication
                 │
        ┌────────▼─────────────┐
        │   NANS Platform      │
        │   ┌──────────────┐   │
        │   │  Frontend    │   │
        │   │  Backend API │   │
        │   │  Database    │   │
        │   └──────────────┘   │
        └────────┬─────────────┘
                 │
        ┌────────┴──────────────────────┬───────────┬───────────┐
        │                               │           │           │
        ▼                               ▼           ▼           ▼
┌───────────────┐          ┌──────────────────┐ ┌──────────┐ ┌──────────┐
│ OAuth Provider│          │  Email Service   │ │ SMS      │ │External  │
│ (Google, etc.)│          │  (SendGrid, etc.)│ │ Service  │ │APIs      │
└───────────────┘          └──────────────────┘ └──────────┘ └──────────┘
```

---

## 2. Core Process Flow Diagram (Level 1)

```
┌────────────────────────────────────────────────────────────────────┐
│                        NANS System                                 │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                   External Systems                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │ │
│  │  │  OAuth   │  │  Email   │  │   SMS    │  │Document      │ │ │
│  │  │Providers │  │ Services │  │Services  │  │Storage       │ │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘ │ │
│  └───────┼─────────────┼─────────────┼───────────────┼─────────┘ │
│          │             │             │               │            │
│  ┌───────▼─────────────▼─────────────▼───────────────▼─────────┐ │
│  │              API Gateway & Middleware Layer                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │ │
│  │  │ Rate     │  │ Auth     │  │ Logging  │  │ Monitoring   │ │ │
│  │  │ Limiting │  │& Authz   │  │& Tracing │  │& Alerting    │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │ │
│  └───────────────────────────────────────────────────────────────┘ │
│          │                                                         │
│  ┌───────▼───────────────────────────────────────────────────────┐ │
│  │              Business Logic Services                          │ │
│  │                                                               │ │
│  │  ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │ │
│  │  │   User    │ │Organization│ │Meeting │ │Activity     │  │ │
│  │  │  Service  │ │ Service  │ │ Service │ │Service      │  │ │
│  │  └─────┬─────┘ └────┬─────┘ └────┬────┘ └──────┬──────┘  │ │
│  │        │            │            │             │          │ │
│  │  ┌─────▼─────────────▼────────────▼─────────────▼──────┐  │ │
│  │  │  Audit Service  │  Document Service  │  Notification  │  │ │
│  │  │ (All changes)   │ (Storage & Share)  │  Service       │  │ │
│  │  └─────┬───────────┬────────────────────┬────────────┬───┘  │ │
│  │        │           │                    │            │       │ │
│  └───────┼───────────┼────────────────────┼────────────┼───────┘ │
│          │           │                    │            │         │
│  ┌───────▼───────────▼────────────────────▼────────────▼───────┐ │
│  │         Infrastructure & Storage Layer                      │ │
│  │                                                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │ │
│  │  │  Cache   │  │  Queue   │  │ Database │  │  Logging   │ │ │
│  │  │ (Redis)  │  │ (Celery) │  │(MongoDB) │  │(ELK Stack) │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. User Authentication Flow

```
User
│
├─ Provides Credentials
│  (email, password)
│
▼
┌─────────────────────────┐
│ Authentication Service  │
│                         │
│ 1. Validate Format      │
│ 2. Lookup User          │
│ 3. Verify Password      │
│ 4. Check 2FA (if enabled)
│ 5. Generate JWT         │
└────────┬────────────────┘
         │
         ├─ JWT Token
         │  (Access Token)
         │
         ├─ Refresh Token
         │  (Stored in Redis)
         │
         ├─ Session Data
         │  (User ID, Roles)
         │
         ▼
┌─────────────────────────┐
│ Client (Next.js)        │
│                         │
│ 1. Store JWT in Memory  │
│ 2. Store Refresh in     │
│    Secure Cookie        │
│ 3. Include in Requests  │
└────────┬────────────────┘
         │
         ├─ Authenticated
         │  Requests
         │
         ▼
┌─────────────────────────┐
│ Authorization Check     │
│                         │
│ 1. Validate JWT         │
│ 2. Extract Claims       │
│ 3. Load User Roles      │
│ 4. Evaluate Permissions │
│ 5. Grant/Deny Access    │
└─────────────────────────┘
```

---

## 4. Meeting Management Flow

```
Chapter Admin
│
├─ Create Meeting
│
▼
┌──────────────────────┐
│ Meeting Service      │
│ ┌────────────────┐   │
│ │ Validate Input │   │
│ │ Check Conflicts│   │
│ │ Create Record  │   │
│ └────────┬───────┘   │
└─────────┼────────────┘
          │
          ├─ Store in DB
          │  (MongoDB)
          │
          ├─ Cache Data
          │  (Redis)
          │
          ▼
┌──────────────────────┐
│ Notification Service │
│ ┌────────────────┐   │
│ │ Create Message │   │
│ │ Queue Task     │   │
│ └────────┬───────┘   │
└─────────┼────────────┘
          │
          ├─ Celery Worker
          │
          ├─ Send Emails
          │
          ├─ Send SMS
          │
          ├─ In-app Alert
          │
          ▼
┌──────────────────────┐
│ Audit Service        │
│ ┌────────────────┐   │
│ │ Log Creation   │   │
│ │ Store in DB    │   │
│ │ (Append-only)  │   │
│ └────────────────┘   │
└──────────────────────┘

Meeting Registration Flow:
┌──────────────────────┐
│ Member               │
│ (View Meeting)       │
│ (Click Register)     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Registration Service │
│ ┌────────────────┐   │
│ │ Check Capacity │   │
│ │ Validate Eligib│   │
│ │ Add to List    │   │
│ │ or Waitlist    │   │
│ └────────┬───────┘   │
└─────────┼────────────┘
          │
          ├─ DB Update
          │
          ├─ Cache Invalidate
          │
          ▼
┌──────────────────────┐
│ Notification Service │
│ │Send Confirmation   │
└──────────────────────┘

Meeting Check-In Flow:
┌──────────────────────┐
│ Facilitator          │
│ (Opens Check-in)     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────┐
│ Check-in Service         │
│ ┌────────────────────┐   │
│ │ Generate QR Code   │   │
│ │ Display to Member  │   │
│ │ Scan or Manual     │   │
│ │ Record Attendance  │   │
│ │ Update Metrics     │   │
│ └────────┬───────────┘   │
└─────────┼────────────────┘
          │
          ├─ Attendance DB
          │
          ├─ Cache Update
          │
          ├─ Real-time Update
          │  (WebSocket)
          │
          ▼
┌──────────────────────────┐
│ Audit Service            │
│ │Log Check-in Event      │
└──────────────────────────┘

Meeting Minutes Flow:
┌──────────────────────┐
│ Facilitator          │
│ (Post-Meeting)       │
│ (Record Minutes)     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Minutes Service      │
│ ┌────────────────┐   │
│ │ Create from    │   │
│ │ Template       │   │
│ │ Add Content    │   │
│ │ Action Items   │   │
│ │ Decisions      │   │
│ └────────┬───────┘   │
└─────────┼────────────┘
          │
          ├─ Store Draft
          │
          ▼
┌──────────────────────┐
│ Workflow Engine      │
│ ┌────────────────┐   │
│ │ Route to       │   │
│ │ Approver       │   │
│ │ Notify         │   │
│ │ Wait Approval  │   │
│ └────────┬───────┘   │
└─────────┼────────────┘
          │
     ┌────┴────┐
     │          │
  Approve    Reject
     │          │
     ▼          ▼
  Publish    Return to Edit
     │
     ▼
┌──────────────────────┐
│ Notification Service │
│ │Send to Attendees   │
└──────────────────────┘
```

---

## 5. Member Enrollment Flow

```
New Member
│
├─ Register
│  (Email, Password)
│
▼
┌──────────────────────────┐
│ User Service             │
│ ┌──────────────────────┐ │
│ │ Create User Account  │ │
│ │ Send Verify Email    │ │
│ │ Store in DB          │ │
│ │ Await Verification   │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ Email Service
            │
            ├─ Verification Link
            │
            ▼
        Verify Email
            │
            ▼
┌──────────────────────────┐
│ User Service             │
│ │Mark Email Verified     │
│ │Enable Login            │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Member Service           │
│ ┌──────────────────────┐ │
│ │ Get Organization ID  │ │
│ │ Create Membership    │ │
│ │ Assign Member Role   │ │
│ │ Send Welcome Email   │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ DB Write
            │
            ├─ Role Assignment
            │
            ├─ Permission Cache
            │
            ▼
┌──────────────────────────┐
│ Audit Service            │
│ │Log Member Enrollment   │
└──────────────────────────┘
```

---

## 6. Document Management Flow

```
User
│
├─ Upload Document
│
▼
┌──────────────────────────┐
│ Document Service         │
│ ┌──────────────────────┐ │
│ │ Validate File Type   │ │
│ │ Check File Size      │ │
│ │ Generate Unique ID   │ │
│ │ Store Metadata       │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ Scan File
            │
            ▼
┌──────────────────────────┐
│ Security Service         │
│ ┌──────────────────────┐ │
│ │ Virus Scan (ClamAV)  │ │
│ │ Validate Content     │ │
│ │ Mark Safe            │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ If Unsafe: Quarantine
            │
            ├─ If Safe: Continue
            │
            ▼
┌──────────────────────────┐
│ File Service             │
│ ┌──────────────────────┐ │
│ │ Upload to S3         │ │
│ │ Generate URL         │ │
│ │ Store Reference      │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ Store in DB
            │
            ├─ Index for Search
            │
            ▼
┌──────────────────────────┐
│ Notification Service     │
│ │Notify Uploader Success │
└──────────────────────────┘

Document Share Flow:
┌──────────────────────────┐
│ Document Owner           │
│ │Share Document          │
│ │Select Users/Groups     │
│ │Set Permissions         │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Share Service            │
│ ┌──────────────────────┐ │
│ │ Create Share Record  │ │
│ │ Generate Link Token  │ │
│ │ Set Expiration       │ │
│ │ Store Permissions    │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ DB Write
            │
            ├─ Permission Cache
            │
            ▼
┌──────────────────────────┐
│ Notification Service     │
│ │Send Share Invitation   │
└──────────────────────────┘

Document Search Flow:
┌──────────────────────────┐
│ User                     │
│ │Enter Search Query      │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Search Service           │
│ ┌──────────────────────┐ │
│ │ Query Elasticsearch  │ │
│ │ Filter by Permission │ │
│ │ Rank Results         │ │
│ │ Return Top Results   │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

---

## 7. Audit and Compliance Flow

```
System Action
│ (Create, Update, Delete)
│
▼
┌──────────────────────────┐
│ Audit Service            │
│ ┌──────────────────────┐ │
│ │ Capture Event        │ │
│ │ Extract Metadata     │ │
│ │ Calculate Hash       │ │
│ │ Append to Log        │ │
│ │ (Immutable)          │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ User ID
            ├─ Action Type
            ├─ Resource Type
            ├─ Resource ID
            ├─ Before State
            ├─ After State
            ├─ IP Address
            ├─ User Agent
            ├─ Timestamp
            │
            ▼
┌──────────────────────────┐
│ MongoDB Collection       │
│ (Append-only)            │
│ ┌──────────────────────┐ │
│ │ Immutable Log Entry  │ │
│ │ Indexed by:          │ │
│ │ • Timestamp          │ │
│ │ • User ID            │ │
│ │ • Action Type        │ │
│ │ • Resource           │ │
│ └──────────────────────┘ │
└──────────────────────────┘

GDPR Data Request Flow:
┌──────────────────────────┐
│ Member                   │
│ │Request Data Export     │
│ │or Deletion             │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Compliance Service       │
│ ┌──────────────────────┐ │
│ │ Verify Request       │ │
│ │ Queue Processing     │ │
│ │ Send Confirmation    │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
            ├─ Celery Worker
            │
            ├─ Collect Data
            │  (All collections)
            │
            ├─ If Deletion:
            │  • Anonymize
            │  • Preserve Audit
            │  • Archive
            │
            ├─ If Export:
            │  • Compile to JSON
            │  • Encrypt
            │  • Generate Link
            │
            ▼
┌──────────────────────────┐
│ File Service / Email     │
│ │Send Result to Member   │
└──────────────────────────┘
```

---

## 8. Notification Dispatch Flow

```
Event Trigger
│ (Meeting reminder time)
│ (Activity update)
│ (Comment on document)
│
▼
┌──────────────────────────┐
│ Notification Service     │
│ ┌──────────────────────┐ │
│ │ Create Notification  │ │
│ │ Load Preferences     │ │
│ │ Select Channels      │ │
│ │ Queue Tasks          │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
   ┌────────┼────────┬────────┐
   │        │        │        │
   ▼        ▼        ▼        ▼
 Email    SMS      Push      In-App
   │        │        │        │
   │        │        │        ├─ Store in DB
   │        │        │        │
   ├─ Render    ├─ Format   ├─ Format  └─ Real-time
   │  Template   │ Message   │ Payload   via WebSocket
   │            │          │
   ├─ Queue     ├─ Queue    ├─ Queue
   │  Task      │  Task     │  Task
   │            │          │
   ▼            ▼          ▼
┌──────────┐┌──────────┐┌──────────────┐
│Email Svc ││SMS Svc   ││Push Provider ││
│(SendGrid)││(Twilio)  ││(Firebase)    ││
└────┬─────┘└────┬─────┘└──────┬───────┘
     │           │            │
     └───────────┼────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Delivery Log  │
         │ • Queued      │
         │ • Sent        │
         │ • Delivered   │
         │ • Failed      │
         │ • Bounced     │
         └───────────────┘
```

---

## 9. Analytics and Reporting Flow

```
Data Sources
│
├─ Meeting Service
│  (Meeting counts,
│   Attendance rates)
│
├─ Activity Service
│  (Activity counts,
│   Participation)
│
├─ User Service
│  (User counts,
│   Engagement)
│
├─ Audit Service
│  (Event counts,
│   Patterns)
│
▼
┌──────────────────────────┐
│ Analytics Service        │
│ ┌──────────────────────┐ │
│ │ Aggregate Data       │ │
│ │ Calculate Metrics    │ │
│ │ Update Time Series   │ │
│ │ Cache Results        │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
   ┌────────┼────────┐
   │        │        │
   ▼        ▼        ▼
Cache     DB       Storage
Redis   MongoDB   Historical
(Real-   (Daily   (Archive
time)   Snapshot)Warehousing)

Report Generation Flow:
┌──────────────────────────┐
│ User                     │
│ │Request Report          │
│ │Select Filters          │
│ │Choose Format           │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Report Service           │
│ ┌──────────────────────┐ │
│ │ Validate Permissions │ │
│ │ Query Data           │ │
│ │ Render Format        │ │
│ │ Generate File        │ │
│ └──────────┬───────────┘ │
└───────────┼───────────────┘
            │
   ┌────────┼────────────┐
   │        │            │
   ▼        ▼            ▼
 PDF      CSV         Excel
   │        │            │
   └────────┼────────────┘
            │
            ▼
┌──────────────────────────┐
│ File Service             │
│ │Store & Generate Link   │
│ │Email Link to User      │
└──────────────────────────┘

Dashboard Real-time Flow:
┌──────────────────────────┐
│ Frontend Dashboard       │
│ (Next.js Component)      │
└──────────┬───────────────┘
           │
           ├─ WebSocket Connection
           │
           ▼
┌──────────────────────────┐
│ Dashboard Service        │
│ ┌──────────────────────┐ │
│ │ Poll Analytics Cache │ │
│ │ Push Updates via WS   │ │
│ │ Every 60 seconds      │ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

---

## 10. Error Handling and Retry Flow

```
Request to Service
│
▼
┌─────────────┐
│Service      │
│Processing  │
└────┬────────┘
     │
     ├─ Success → Response
     │
     └─ Error
         │
         ▼
     ┌─────────────┐
     │Error Type?  │
     └────┬────────┘
          │
     ┌────┼────┬────────┐
     │    │    │        │
Retry  Log Fail Notify  Escalate
     │    │    │        │
     ├─   ├─   ├─       └─ Alert Ops
     │    │    │           (PagerDuty)
     │    │    │
     │    │    └─ User Alert
     │    │       (In-app error)
     │    │
     │    └─ Audit Log
     │       (Error event)
     │
     ▼
┌──────────────────┐
│Retry Logic       │
│                  │
│ Exponential      │
│ Backoff:         │
│ • 1 second       │
│ • 2 seconds      │
│ • 4 seconds      │
│ • 8 seconds      │
│ • Max 5 retries  │
└─────┬────────────┘
      │
      ├─ Success → Return
      │
      └─ Failure → Dead Letter Queue
           (DLQ for manual review)
```

---

## 11. Data Consistency Flow

```
Transaction Initiated
│
▼
┌──────────────────────────┐
│ Begin Transaction        │
│ (MongoDB Session)        │
└──────────┬───────────────┘
           │
           ├─ Multi-document ACID
           │  (MongoDB 4.0+)
           │
           ▼
┌──────────────────────────┐
│ Execute Business Logic   │
│ • Validation             │
│ • Calculations           │
│ • State Changes          │
└──────────┬───────────────┘
           │
      ┌────┴────┐
      │          │
   Success    Error
      │          │
      ▼          ▼
  Commit      Rollback
      │          │
      ├─ Update DB  ├─ Undo Changes
      │             │
      ├─ Invalidate ├─ Restore Cache
      │  Cache      │
      │             │
      ├─ Log Event  ├─ Log Error
      │             │
      ├─ Notify     ├─ Notify
      │  Listeners  │  Error
      │             │
      └─────┬───────┘
            │
            ▼
      Consistency Verified
```

