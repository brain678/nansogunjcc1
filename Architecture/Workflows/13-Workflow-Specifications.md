# Workflow Specifications
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Meeting Management Workflow

### 1.1 Meeting Lifecycle States

```
Workflow States:

Draft
  │ (Save as incomplete)
  ├─ Can edit all fields
  ├─ No notifications sent
  ├─ Can save multiple times
  └─ Only visible to creator

Draft → Scheduled
  │ (Publish meeting)
  ├─ All required fields must be complete
  ├─ Notifications sent to eligible attendees
  ├─ Calendar invite generated
  ├─ Invite email sent
  └─ Visible to all invited

Scheduled
  │ (Meeting date/time)
  ├─ Open for registration
  ├─ Reminders sent (1 day before, 1 hour before)
  ├─ Can be rescheduled
  ├─ Can add agenda items
  └─ Can update description (with notification)

Active
  │ (Meeting started)
  ├─ Check-in enabled
  ├─ Attendance tracking
  ├─ Cannot reschedule
  ├─ Real-time updates
  └─ Focus on participation

Completed
  │ (Meeting ended)
  ├─ Attendance finalized
  ├─ Minutes can be recorded
  ├─ Action items tracked
  ├─ Decisions documented
  └─ Results distributed

Cancelled
  │ (Meeting cancelled)
  ├─ Notifications sent to all registered
  ├─ Calendar invite revoked
  ├─ Registration refunds processed
  ├─ Archived for records
  └─ Reason documented
```

### 1.2 Meeting Creation Workflow

```
Actor: Chapter Administrator

Step 1: Create Meeting
├─ Form filled:
│   ├─ Title (required)
│   ├─ Description
│   ├─ Type (virtual/in-person/hybrid)
│   ├─ Scheduled date/time (required)
│   ├─ Duration (required)
│   ├─ Location/link
│   ├─ Agenda items
│   ├─ Facilitator assignment (required)
│   └─ Capacity limit
│
└─ Meeting created in "Draft" state

Step 2: Conflict Check
├─ Check for:
│   ├─ Room/location conflicts
│   ├─ Facilitator conflicts
│   ├─ Organization holiday conflicts
│   └─ Critical date conflicts
│
├─ If conflict found:
│   ├─ Warning displayed
│   └─ User prompted to resolve
│
└─ Conflict check passed

Step 3: Save Meeting
├─ DB write: Meeting record
├─ Cache: Invalidate org calendar
├─ Audit: Log meeting creation
└─ Response: Meeting ID returned

Step 4: Publish Meeting
├─ User clicks "Publish"
├─ Validation:
│   ├─ All required fields complete
│   ├─ No conflicts
│   ├─ Capacity > 0
│   └─ Facilitator assigned
│
├─ Status: Draft → Scheduled
│
├─ Notifications:
│   ├─ Eligible attendees identified
│   ├─ Email invitations queued
│   ├─ Calendar invites generated
│   └─ Async task: Send notifications
│
├─ Calendar:
│   ├─ Public calendar updated
│   ├─ Member calendars updated
│   └─ Cache updated
│
├─ Audit: Log publication
└─ Response: Meeting published

Step 5: Send Notifications
├─ Celery worker processes
├─ For each eligible attendee:
│   ├─ Generate email from template
│   ├─ Include meeting link/details
│   ├─ Generate calendar invite (iCal)
│   ├─ Send email via SendGrid
│   └─ Log delivery status
│
├─ If RSVP enabled:
│   ├─ Include RSVP link
│   └─ Track responses
│
└─ Complete: Meeting published
```

### 1.3 Meeting Registration Workflow

```
Actor: Member

Step 1: Browse Meetings
├─ Navigate to meetings calendar
├─ Filter by organization/date
├─ View meeting details
└─ Click "Register" button

Step 2: Registration Form
├─ Check eligibility:
│   ├─ Organization membership valid
│   ├─ Member status active
│   ├─ No access restrictions
│   └─ Not already registered
│
├─ Show form:
│   ├─ Confirm name/email
│   ├─ Dietary restrictions (if applicable)
│   ├─ Special accommodations
│   ├─ RSVP response
│   └─ Agree to terms
│
└─ Submission

Step 3: Capacity Check
├─ Query current registrations
├─ Compare to capacity limit
│
├─ If capacity available:
│   └─ Status: registered
│
├─ If capacity exceeded:
│   ├─ Check if waitlist enabled
│   ├─ If yes: Status = waitlisted, Position noted
│   └─ If no: Error - meeting full
│
└─ Continue

Step 4: Save Registration
├─ DB write: MeetingRegistration record
├─ Cache: Update meeting attendee count
├─ Update capacity bar
└─ Audit: Log registration

Step 5: Send Confirmation
├─ Generate confirmation email
├─ Include:
│   ├─ Meeting details
│   ├─ Calendar invite
│   ├─ Check-in information
│   ├─ Cancellation link
│   └─ Accessibility info
│
├─ Send via email
├─ Store: In notification log
└─ Response: Registration confirmed

Step 6: Monitor Waitlist
├─ If waitlisted:
│   ├─ Monitor for cancellations
│   ├─ Automatic promotion to registered (if capacity)
│   ├─ Send promotion notification
│   └─ Update calendar
│
└─ If promoted:
    ├─ Status: waitlisted → registered
    ├─ Send "congrats" email
    ├─ Calendar invite resent
    └─ Audit: Log promotion
```

### 1.4 Meeting Check-In Workflow

```
Actor: Meeting Facilitator

Step 1: Start Meeting
├─ Navigate to meeting detail
├─ Click "Start Check-In"
├─ System displays:
│   ├─ Registered attendees (alphabetical)
│   ├─ QR code for mobile check-in
│   ├─ Manual check-in input field
│   ├─ Attendance summary
│   └─ Real-time update
│
└─ Check-in enabled

Step 2: Manual Check-In
├─ Method 1: Search by name
│   ├─ Facilitator enters name
│   ├─ System filters matches
│   ├─ Facilitator clicks match
│   └─ Attendee marked present
│
├─ Method 2: QR Code scan
│   ├─ Attendee scans QR with phone
│   ├─ Redirects to check-in link
│   ├─ Attendee name auto-filled
│   ├─ Click "Check In"
│   └─ Real-time update to facilitator
│
├─ Method 3: Manual entry
│   ├─ Facilitator enters email/name
│   ├─ System validates (or adds guest)
│   ├─ Click "Check In"
│   └─ Record created/updated
│
└─ Time recorded: check-in timestamp

Step 3: Record Attendance
├─ Update meeting registration:
│   ├─ status: checked-in
│   ├─ check_in_time: timestamp
│   └─ late: calculated if after start time
│
├─ Update metrics:
│   ├─ Total attended
│   ├─ Late count
│   ├─ No-show count
│   └─ Cancellation count
│
├─ Cache: Update attendance data
├─ Real-time: WebSocket push to facilitator
└─ Audit: Log check-in

Step 4: Meeting End
├─ Facilitator clicks "End Meeting"
├─ System prompts:
│   ├─ Confirm meeting end
│   ├─ Any additional attendees
│   └─ Final attendance summary
│
├─ Finalize attendance:
│   ├─ Lock registration data
│   ├─ Calculate metrics
│   ├─ Generate report
│   └─ Archive data
│
├─ Transition state:
│   ├─ Meeting status: active → completed
│   ├─ Check-in: disabled
│   └─ Minutes recording: enabled
│
└─ Response: Meeting completed
```

### 1.5 Meeting Minutes Workflow

```
Actor: Meeting Facilitator → Approver

Step 1: Create Minutes
├─ Post-meeting, facilitator navigates to meeting
├─ Clicks "Record Minutes"
├─ System shows template:
│   ├─ Attended list (pre-populated)
│   ├─ Action items section
│   ├─ Decisions section
│   ├─ Notes section
│   └─ Recommendations section
│
├─ Facilitator completes:
│   ├─ Reviews attendee list
│   ├─ Adds action items:
│   │   ├─ Description
│   │   ├─ Assigned to
│   │   ├─ Due date
│   │   └─ Priority
│   │
│   ├─ Records decisions:
│   │   ├─ Decision made
│   │   ├─ Impact/next steps
│   │   ├─ Owner assigned
│   │   └─ Priority
│   │
│   ├─ Adds meeting notes
│   └─ Drafts recommendations
│
└─ Save as draft

Step 2: Review Minutes
├─ Facilitator reviews/edits
├─ Adds additional details if needed
├─ Verifies accuracy
└─ Ready for approval

Step 3: Submit for Approval
├─ Facilitator clicks "Submit for Approval"
├─ Select approver (usually meeting organizer/chair)
├─ Add personal note to approver
├─ Submit
│
├─ Workflow transitions:
│   ├─ Status: draft → pending_approval
│   ├─ Approver assigned
│   └─ Approver notified
│
└─ Audit: Log submission

Step 4: Approval Review
├─ Approver receives notification
├─ Reviews minutes in detail
├─ Can:
│   ├─ Approve (publish immediately)
│   ├─ Request changes (return to facilitator)
│   └─ Reject (with reason)
│
├─ If approved:
│   └─ Continue to Step 5
│
├─ If changes requested:
│   ├─ Facilitator notified
│   ├─ Status: pending_approval → revision_requested
│   ├─ Facilitator updates minutes
│   ├─ Resubmit
│   └─ Back to this step
│
└─ If rejected:
    ├─ Reason documented
    ├─ Facilitator notified
    ├─ Status: draft
    └─ Facilitator must revise
```

---

## 2. Historical Archive and Data Retention Workflow

### 2.1 Data Classification

```
Classification Levels:

Active (Current Use):
├─ Meetings within last 30 days
├─ Current year activities
├─ Active memberships
├─ Recent documents
└─ Retention: Hot storage (MongoDB)

Warm (Historical, Infrequent Access):
├─ Meetings from last 30 days to 1 year
├─ Prior year activities (recent)
├─ Closed memberships
├─ Document archives
└─ Retention: Warm storage (MongoDB archive)

Cold (Compliance/Legal Hold):
├─ Data older than 1 year
├─ Audit trails
├─ Deleted account backups
├─ Legal proceedings
└─ Retention: Cold storage (S3 Glacier)

Destroyed:
├─ Data beyond retention period
├─ No legal hold
├─ Destruction verified
├─ Certificate issued
└─ Retention: None (deleted)
```

### 2.2 Archival Workflow

```
Schedule: Daily (12:00 AM UTC)

Automated Process:

Step 1: Identify Archive Candidates
├─ Query meetings:
│   ├─ status = "completed"
│   ├─ created_at < 30 days ago
│   └─ not already archived
│
├─ Query activities:
│   ├─ completed_at < 30 days ago
│   └─ not archived
│
├─ Query documents:
│   ├─ created_at < 365 days ago
│   ├─ access_count = 0 (no recent access)
│   └─ not archived
│
└─ Query audit logs:
    ├─ timestamp < 90 days ago
    └─ size > 500MB (batch)

Step 2: Create Archive Bundle
├─ Package related data:
│   ├─ Meeting + registration + attendees
│   ├─ Activity + participants
│   ├─ Document + versions + sharing
│   └─ Audit logs + related records
│
├─ Compression:
│   ├─ Format: .tar.gz
│   ├─ Compression ratio: 10:1 (typical)
│   └─ Verify integrity: SHA-256 checksum
│
└─ Bundling complete

Step 3: Encryption
├─ Algorithm: AES-256-GCM
├─ Key source: AWS KMS / Vault
├─ Key rotation: 90-day cycle
├─ Metadata: Encrypted separately
└─ Encrypted package created

Step 4: Upload to Archive
├─ Destination: S3 Glacier
├─ Bucket structure:
│   ├─ s3://nans-archive/YYYY/MM/DD/...
│   ├─ Multiple regions (replication)
│   └─ Versioning enabled
│
├─ Upload:
│   ├─ Multi-part upload (parallel)
│   ├─ Retry on failure
│   ├─ Verify: ETags match
│   └─ Set lifecycle policy
│
└─ Archive stored

Step 5: Indexing
├─ Create metadata index:
│   ├─ Original ID
│   ├─ Archive location
│   ├─ Date archived
│   ├─ Content checksum
│   ├─ Encryption key version
│   └─ Retention expiry date
│
├─ Store in separate MongoDB:
│   ├─ Separate cluster (read-only)
│   ├─ Backup of index
│   └─ Accessible for queries
│
└─ Index complete

Step 6: Delete from Hot Storage
├─ Verify archive successful
├─ Delete from MongoDB (primary)
├─ Delete from cache (Redis)
├─ Wait for replication
├─ Verify deletion
├─ Audit: Log deletion
└─ Complete

Step 7: Reporting
├─ Archive job summary:
│   ├─ Records archived
│   ├─ Archive size
│   ├─ Duration
│   ├─ Success/failure count
│   ├─ Cost savings
│   └─ Issues encountered
│
├─ Email report to admin
├─ Dashboard update
└─ Alert if failures
```

### 2.3 Archive Retrieval Workflow

```
Actor: Administrator / Auditor

Step 1: Request Archive
├─ Search archive index:
│   ├─ Query by date range
│   ├─ Query by organization
│   ├─ Query by user
│   └─ Query by content type
│
├─ Results display:
│   ├─ Matching archives found
│   ├─ Archive location
│   ├─ Date created
│   ├─ Size
│   └─ Retention expiry
│
└─ Select archive for retrieval

Step 2: Request Retrieval
├─ Verify authorization:
│   ├─ Role check: Auditor/Admin
│   ├─ Organization scope
│   └─ Data sensitivity check
│
├─ Create retrieval job:
│   ├─ Source: S3 Glacier
│   ├─ Destination: S3 standard (staging)
│   ├─ Priority: Standard (3-5 hours) or Expedited (5-15 min)
│   ├─ Temporary location: 24-hour expiry
│   └─ Audit: Log request
│
└─ Job submitted

Step 3: Retrieval Processing
├─ S3 Glacier initiates restore:
│   ├─ Retrieve from archive tier
│   ├─ Decrypt package
│   ├─ Decompress
│   ├─ Write to staging location
│   └─ Update job status
│
├─ Verify integrity:
│   ├─ Calculate checksum
│   ├─ Compare to stored checksum
│   ├─ If mismatch: Alert and retry
│   └─ If match: Continue
│
└─ Ready for access

Step 4: Download
├─ Generate download link (signed URL)
├─ Link expires: 24 hours
├─ Include in notification
├─ User downloads file
├─ Log download event
│
├─ After download:
│   ├─ File remains accessible for 24 hours
│   ├─ Auto-delete after 24 hours
│   └─ Staging area cleaned
│
└─ Download complete

Step 5: Restoration (if needed)
├─ If data needs to be restored to live system:
│   ├─ Verify backup first (don't lose current)
│   ├─ Restore with new IDs initially
│   ├─ Verify data integrity
│   ├─ Merge with current data carefully
│   ├─ Audit all restoration steps
│   └─ Notify affected users
│
└─ Restoration complete
```

---

## 3. Activity Management Workflow

### 3.1 Activity Creation Workflow

```
Actor: Activity Coordinator

Step 1: Create Activity
├─ Form filled:
│   ├─ Title (required)
│   ├─ Description
│   ├─ Category (Workshop, Training, Social, etc.)
│   ├─ Tags/Keywords
│   ├─ Organizer (auto-filled)
│   ├─ Start date (required)
│   ├─ End date (if multi-day)
│   ├─ Location (required)
│   ├─ Expected participants
│   └─ Activity details
│
├─ Activity created
└─ Save as draft

Step 2: Publish Activity
├─ Validation:
│   ├─ All required fields complete
│   ├─ Dates valid (end > start)
│   ├─ Location specified
│   └─ At least 1 coordinator assigned
│
├─ Status: draft → published
├─ Visibility: Members can see
├─ Notifications sent (if configured)
└─ Calendar updated

Step 3: Record Participation
├─ Before/during/after activity:
│   ├─ Coordinator manually enters participants
│   ├─ Or: Upload participant list (CSV)
│   ├─ Or: System auto-records (if QR/check-in)
│   └─ Or: Self-registration by members
│
├─ For each participant:
│   ├─ Record member_id
│   ├─ Record participation_date
│   ├─ Record participation_type (attended/presented/organized)
│   └─ Optional: Hours, role
│
└─ Submission

Step 4: Calculate Engagement
├─ Engagement points:
│   ├─ Base: Attendance = 1 point
│   ├─ Leadership: Organizer = 5 points
│   ├─ Speaking: Presenter = 3 points
│   ├─ Facilitator: Organizer/Facilitator = 5 points
│   └─ Multiplier: Organization level (national = 1.5x)
│
├─ Update member engagement score:
│   ├─ Add points to lifetime total
│   ├─ Update streak (consecutive participations)
│   ├─ Update engagement level (low/medium/high)
│   └─ Cache updated
│
└─ Metrics recalculated

Step 5: Complete Activity
├─ After activity concludes:
│   ├─ Coordinator marks as completed
│   ├─ Records outcomes/results
│   ├─ Documents photos/materials (if applicable)
│   ├─ Provides lessons learned
│   └─ Status: published → completed
│
├─ Archive:
│   ├─ Move to historical storage
│   ├─ Maintain participation records
│   ├─ Keep engagement data
│   └─ Preserve for reporting
│
└─ Activity archived

Step 6: Send Thank You Notifications
├─ Send emails to:
│   ├─ All participants
│   ├─ Facilitators/organizers
│   ├─ Speakers/presenters
│   └─ Volunteers
│
├─ Include:
│   ├─ Thank you message
│   ├─ Engagement points awarded
│   ├─ Certificate (if applicable)
│   ├─ Feedback link
│   └─ Future activity suggestions
│
└─ Notifications sent
```

### 3.2 Participation Tracking Workflow

```
Multi-Method Participation Recording:

Method 1: Self-Registration
├─ Member registers online
├─ Activity page → "Register"
├─ Quick form → "Confirm"
├─ Confirmation email sent
├─ Status: Interested (pending confirmation at event)
│
└─ At event: Confirm attendance during check-in

Method 2: QR Code Check-In
├─ Event coordinator prints/displays QR code
├─ Member scans with smartphone
├─ Links to check-in page
├─ Shows activity name/details
├─ Member clicks "Check In"
├─ Real-time confirmation
├─ Check-in recorded with timestamp
│
└─ Analytics updated in real-time

Method 3: Manual Check-In
├─ Event coordinator has attendance sheet
├─ Facilitator checks off attendees as they arrive
├─ End of event: Upload list to system
│ ├─ CSV format: email, name, hours
│ ├─ Validation: Check members exist
│ └─ Match/unmatched records
│
├─ System processes:
│   ├─ Matched: Record participation
│   ├─ Unmatched: Flag for review
│   └─ Create guest profile if non-member
│
└─ Participation recorded

Method 4: Supervisor Entry
├─ Organization admin/supervisor
├─ Records staff participation
├─ Batch upload:
│   ├─ Date
│   ├─ Activity type
│   ├─ Participants
│   └─ Hours/details
│
├─ System processes:
│   ├─ Validates data
│   ├─ Records participation
│   ├─ Updates engagement
│   └─ Sends confirmations
│
└─ Participation recorded

Engagement Score Calculation:
├─ Base participation: 1 point
├─ Facilitator/Organizer: 5 points
├─ Speaker/Presenter: 3 points
├─ Leadership role: 2x multiplier
├─ Multi-day event: Points per day
├─ Organization level multiplier:
│   ├─ National level: 1.5x
│   ├─ Chapter level: 1.0x
│   ├─ Sub-group level: 0.75x
│   └─ Local level: 0.5x
│
├─ Update member profile:
│   ├─ Total engagement score
│   ├─ Monthly/quarterly/annual breakdown
│   ├─ Streak calculation
│   ├─ Engagement level classification
│   └─ Leaderboard ranking
│
└─ Badges/rewards (if configured)
    ├─ 5 participation badge
    ├─ 10 participation badge
    ├─ Streak badges
    └─ Leadership badges
```

### 3.3 Reporting Workflow

```
Analytics & Reporting:

Real-Time Dashboard:
├─ Active activities
├─ Today's participants
├─ Current engagement trending
├─ Upcoming activities
└─ Top participants (live)

Daily Reports:
├─ Activities completed
├─ Participants count
├─ Engagement points awarded
├─ New records added
└─ Sent to coordinators

Weekly Reports:
├─ Activities summary
├─ Participation trends
├─ Top activities
├─ Top participants
├─ Chapter comparison (if multi-chapter)
└─ Sent to admins

Monthly Reports:
├─ Detailed activity analysis
├─ Participant demographics
├─ Engagement level distribution
├─ Growth metrics
├─ Recommendations for improving engagement
└─ Sent to executive team

Custom Reports:
├─ Date range selection
├─ Organization level filtering
├─ Activity type filtering
├─ Export formats: PDF, CSV, Excel
├─ Scheduled delivery available
└─ On-demand generation supported
```

