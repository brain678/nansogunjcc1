# Role Hierarchy and Permission Matrix
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Role Hierarchy Overview

### 1.1 Role Definition

A role represents a collection of permissions assigned to users. Roles are organized hierarchically based on organizational levels and functional responsibilities.

### 1.2 Role Assignment Pattern

Users can have multiple roles:
- One primary role per organizational level
- Multiple supplementary roles
- Temporary role assignments with expiration
- Role inheritance from parent organizational levels

---

## 2. Organizational Roles

### 2.1 National Level Roles

#### **Executive Director** (ED)
- **Scope:** National organization
- **Responsibilities:** 
  - Strategic direction
  - Financial oversight
  - Chapter approval and oversight
  - Organizational policy setting
  - Board management

- **Authority Level:** Highest
- **Delegate Responsibility:** Yes
- **Can Create Chapters:** Yes
- **Reports To:** Board of Directors

#### **National Administrator** (NA)
- **Scope:** National organization and all chapters
- **Responsibilities:**
  - User management
  - System configuration
  - Data integrity
  - Compliance oversight
  - Support escalation

- **Authority Level:** Very High
- **Delegate Responsibility:** Yes (limited)
- **Can Create Chapters:** Yes
- **Reports To:** Executive Director

#### **National Finance Officer** (NFO)
- **Scope:** National financial data
- **Responsibilities:**
  - Financial reporting
  - Budget management
  - Compliance auditing
  - Financial policy enforcement

- **Authority Level:** High
- **Delegate Responsibility:** No
- **Can Create Chapters:** No
- **Reports To:** Executive Director

#### **National Communications Director** (NCD)
- **Scope:** All organizational communications
- **Responsibilities:**
  - Newsletter management
  - Announcement distribution
  - Public communications
  - Member outreach

- **Authority Level:** Medium-High
- **Delegate Responsibility:** Yes
- **Can Create Chapters:** No
- **Reports To:** Executive Director

#### **National Auditor** (NAU)
- **Scope:** Audit trail and compliance data
- **Responsibilities:**
  - Compliance verification
  - Audit trail review
  - Policy enforcement review
  - Risk assessment

- **Authority Level:** Medium
- **Delegate Responsibility:** No
- **Can Create Chapters:** No
- **Reports To:** Executive Director

#### **National Archivist** (NARCH)
- **Scope:** Historical records and archives
- **Responsibilities:**
  - Document archival
  - Historical record management
  - Retention policy enforcement
  - Archive access control

- **Authority Level:** Medium
- **Delegate Responsibility:** No
- **Can Create Chapters:** No
- **Reports To:** National Administrator

---

### 2.2 Chapter/Division Level Roles

#### **Chapter President/Chair** (CP)
- **Scope:** Single chapter
- **Responsibilities:**
  - Chapter leadership
  - Meeting organization
  - Member engagement
  - Chapter administration

- **Authority Level:** High (within chapter)
- **Delegate Responsibility:** Yes
- **Can Modify Members:** Yes
- **Reports To:** Executive Director

#### **Chapter Administrator** (CA)
- **Scope:** Single chapter operations
- **Responsibilities:**
  - Membership management
  - Meeting scheduling
  - Document management
  - Activity coordination

- **Authority Level:** Medium-High (within chapter)
- **Delegate Responsibility:** Yes (limited)
- **Can Modify Members:** Yes
- **Reports To:** Chapter President

#### **Chapter Finance Officer** (CFO)
- **Scope:** Chapter financial data
- **Responsibilities:**
  - Local financial reporting
  - Budget management
  - Expense tracking

- **Authority Level:** Medium (within chapter)
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** Chapter President

#### **Chapter Secretary** (CS)
- **Scope:** Chapter records
- **Responsibilities:**
  - Meeting minutes
  - Record keeping
  - Document management
  - Communication coordination

- **Authority Level:** Medium (within chapter)
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** Chapter President

#### **Meeting Facilitator** (MF)
- **Scope:** Specific meetings
- **Responsibilities:**
  - Meeting coordination
  - Attendance tracking
  - Minutes recording
  - Attendee communication

- **Authority Level:** Low-Medium (meeting-specific)
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** Chapter Administrator

---

### 2.3 Member Level Roles

#### **Active Member** (AM)
- **Scope:** Own data and shared resources
- **Responsibilities:**
  - Participate in activities
  - Attend meetings
  - View organizational information
  - Manage own profile

- **Authority Level:** Base
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** Chapter Administrator

#### **Inactive Member** (IM)
- **Scope:** Read-only access
- **Responsibilities:**
  - View organizational information
  - Cannot modify anything
  - Cannot register for activities

- **Authority Level:** Minimal
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** Chapter Administrator

#### **Guest** (G)
- **Scope:** Limited public resources
- **Responsibilities:**
  - View limited public information
  - Register for public events (if applicable)

- **Authority Level:** Minimal
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Reports To:** N/A

---

### 2.4 Functional Roles

#### **Auditor** (AUD)
- **Scope:** Audit logs and compliance data
- **Responsibilities:**
  - Audit trail review
  - Compliance reporting
  - Access pattern analysis

- **Authority Level:** Medium
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Can Override:** View-only access to audit logs

#### **System Administrator** (SA)
- **Scope:** Entire system infrastructure
- **Responsibilities:**
  - System maintenance
  - Backup and recovery
  - Infrastructure management
  - Performance optimization

- **Authority Level:** Critical
- **Delegate Responsibility:** Yes (limited)
- **Can Modify Members:** Yes (emergency only)
- **Emergency Access:** Yes

#### **Support Specialist** (SUPP)
- **Scope:** User support and escalation
- **Responsibilities:**
  - User assistance
  - Issue escalation
  - Troubleshooting
  - User account support

- **Authority Level:** Low-Medium
- **Delegate Responsibility:** No
- **Can Modify Members:** No
- **Limited Override:** Password reset, account unlock

---

## 3. Role Hierarchy Visualization

```
National Level
├── Executive Director (Apex)
├── National Administrator
│   ├── National Finance Officer
│   ├── National Communications Director
│   ├── National Auditor
│   └── National Archivist
│
├── Chapter/Division Level (recursive)
│   ├── Chapter President
│   ├── Chapter Administrator
│   │   ├── Chapter Finance Officer
│   │   ├── Chapter Secretary
│   │   └── Meeting Facilitator (meeting-specific)
│   │
│   └── Member Level
│       ├── Active Member
│       ├── Inactive Member
│       └── Guest
│
└── Functional/Cross-cutting
    ├── Auditor
    ├── System Administrator
    └── Support Specialist
```

---

## 4. Permission Matrix

### 4.1 Permission Categories

Permissions are organized into categories:

| Category | Description |
|----------|-------------|
| `user:*` | User management permissions |
| `org:*` | Organization management permissions |
| `meeting:*` | Meeting management permissions |
| `activity:*` | Activity management permissions |
| `document:*` | Document management permissions |
| `audit:*` | Audit and compliance permissions |
| `report:*` | Reporting and analytics permissions |
| `system:*` | System administration permissions |

### 4.2 Detailed Permission Matrix

#### User Management Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `user:create` | Create new user | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `user:view` | View user profile | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| `user:edit` | Edit user profile | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ◐ | ✗ | ✗ | ✓ | ✗ |
| `user:delete` | Delete user account | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `user:role-assign` | Assign roles to users | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `user:role-revoke` | Revoke roles from users | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `user:password-reset` | Reset user password | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ◐ | ✗ | ✗ | ✓ | ✗ |
| `user:view-directory` | View member directory | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| `user:export-directory` | Export member directory | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |

#### Organization Management Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `org:create-chapter` | Create new chapter | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `org:edit-chapter` | Edit chapter information | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `org:view-hierarchy` | View organizational hierarchy | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| `org:manage-hierarchy` | Move chapters in hierarchy | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `org:enroll-member` | Enroll new member | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `org:bulk-import` | Bulk import members | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `org:manage-policy` | Define org policies | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |

#### Meeting Management Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `meeting:create` | Create meeting | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `meeting:edit` | Edit meeting details | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ◐ | ✗ | ✗ | ✓ | ✗ |
| `meeting:cancel` | Cancel meeting | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `meeting:register` | Register for meeting | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ◐ | ✓ | ✓ |
| `meeting:check-in` | Check in attendees | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `meeting:view-attendees` | View attendee list | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `meeting:record-minutes` | Record meeting minutes | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `meeting:approve-minutes` | Approve meeting minutes | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |

#### Activity Management Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `activity:create` | Create activity | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `activity:edit` | Edit activity details | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ◐ | ✗ | ✗ | ✓ | ✗ |
| `activity:record-participation` | Record participant | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `activity:view-participation` | View participation data | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |

#### Document Management Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `document:upload` | Upload documents | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `document:view` | View documents | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ◐ | ✓ | ✓ |
| `document:edit` | Edit documents | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ◐ | ✗ | ✗ | ✓ | ✗ |
| `document:share` | Share documents | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ |
| `document:delete` | Delete documents | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `document:archive` | Archive documents | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |

#### Audit and Compliance Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `audit:view-logs` | View audit logs | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `audit:export-logs` | Export audit logs | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `audit:generate-reports` | Generate compliance reports | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `audit:view-data-requests` | View data access requests | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `compliance:data-export` | Request personal data export | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| `compliance:data-delete` | Request data deletion | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ |

#### Reporting and Analytics Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `report:view` | View reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| `report:create` | Create custom reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `report:export` | Export reports | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `report:schedule` | Schedule report generation | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |

#### System Administration Permissions

| Permission | Description | ED | NA | NFO | NCD | NAU | CP | CA | CFO | CS | MF | AM | IM | G | SA | AUD |
|-----------|-------------|----|----|-----|-----|----|----|----|-----|----|----|----|----|---|----|----|
| `system:config` | Configure system settings | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `system:backup` | Manage backups | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| `system:monitor` | Monitor system health | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| `system:logs` | View system logs | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |

### 4.3 Legend

- ✓ = Full Permission
- ✗ = No Permission
- ◐ = Limited Permission (own data only or with restrictions)

---

## 5. Scope Limitations

### 5.1 Data Scope Rules

1. **National Scope:** Can access all organizational data (ED, NA, NAU, SA, AUD)
2. **Chapter Scope:** Can access chapter data and member data within chapter (CP, CA, CS, CFO)
3. **Meeting Scope:** Can access specific meeting data (MF)
4. **Personal Scope:** Can access own data only (AM, IM, G)

### 5.2 Organization-Level Inheritance

Permissions inherit down the organizational hierarchy:
- National-level permissions apply to all chapters
- Chapter-level permissions apply only to that chapter
- Division-level permissions apply only to that division and subdivisions

### 5.3 Temporal Scoping

Permissions can be time-scoped:
- Permanent (no expiration)
- Temporary (with expiration date)
- Event-based (valid during meeting/activity only)

---

## 6. Permission Delegation

### 6.1 Delegatable Roles

- Executive Director → Chapter President
- National Administrator → Chapter Administrator
- Chapter President → Chapter Administrator, Meeting Facilitator
- Chapter Administrator → Meeting Facilitator

### 6.2 Delegation Rules

1. Delegator must have explicit delegation permission
2. Delegation recorded in audit trail
3. Delegated permissions are time-scoped (maximum 1 year)
4. Delegator remains accountable for delegated permissions
5. Delegation can be revoked at any time

---

## 7. Emergency Access

### 7.1 System Administrator Emergency Access

System Administrators may assume roles temporarily:
- Requires approval from Executive Director
- Logged with reason and timestamp
- Maximum duration: 4 hours
- Automatic expiration and audit alert

### 7.2 Escalation Rules

1. User permission denied
2. Escalation to Support Specialist
3. Support Specialist escalates to Chapter Administrator
4. Chapter Administrator may escalate to National Administrator
5. National Administrator escalates to Executive Director
6. Final escalation to System Administrator

---

## 8. Role Assignment Workflow

### 8.1 New Member Onboarding

1. Member registers and creates account
2. Assigned "Active Member" role in appropriate chapter
3. Chapter Administrator assigns additional roles if needed
4. Permission inheritance applied automatically
5. Audit trail recorded

### 8.2 Role Changes

1. Manager initiates role change
2. Change requires approval based on role level
3. Automated notification to user
4. Permissions updated in real-time
5. Audit trail recorded

---

## 9. Permission Audit and Review

### 9.1 Regular Audit Schedule

- Quarterly: Review all role assignments
- Semi-annually: Review all custom permissions
- Annually: Complete compliance audit
- On-demand: Incident investigation

### 9.2 Least Privilege Verification

- Confirm all users have minimum necessary permissions
- Identify and remove unused roles
- Flag permission creep
- Recommend consolidation

---

## 10. Role Conflict Resolution

### 10.1 Conflicting Permissions

When conflicting permissions exist:
1. Deny is more restrictive than allow (Deny wins)
2. Explicit permission wins over inherited
3. Time-scoped permissions override permanent
4. Functional role conflicts escalated to Executive Director

### 10.2 Permission Precedence

1. Explicit deny (highest priority)
2. Time-scoped permission
3. Functional role permission
4. Organizational role permission
5. Inherited permission (lowest priority)

