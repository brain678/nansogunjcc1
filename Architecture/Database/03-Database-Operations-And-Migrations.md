# Database Operations and Migration Guide
## MongoDB Schema Evolution and Maintenance

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft

---

## 1. Schema Versioning and Evolution

### 1.1 Schema Versioning Strategy

```
Versioning Approach:

1. Code-Driven Versioning
   ├─ Version in Beanie model definition
   ├─ Track in Git with model changes
   ├─ Document breaking changes
   └─ Maintain backward compatibility

2. Migration Scripts
   ├─ One-off scripts for data transformations
   ├─ Run before deployment
   ├─ Include rollback capability
   ├─ Log all changes
   └─ Idempotent (safe to re-run)

3. Zero-Downtime Deployment
   ├─ Deploy new code with backward compatibility
   ├─ Run migration scripts in background
   ├─ Old and new code coexist briefly
   ├─ Rollback possible without data loss
   └─ Monitor for errors during transition

Version Tracking:

class ModelVersion(Document):
    model_name: str  # "users", "meetings"
    version: int = 1
    schema_hash: str  # Hash of current schema
    deployed_at: datetime
    applied_at: Optional[datetime]
    rollback_available: bool = True
    changes: List[str]  # Human-readable changes
    
    class Settings:
        collection = "model_versions"
        indexes = [["model_name", 1], ["version", -1]]
```

### 1.2 Migration Patterns

```python
# Migration Template

# app/migrations/001_add_phone_to_users.py
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncClient
from app.models.user import User

async def upgrade():
    """Forward migration: Add phone field"""
    # This runs in production to add new field
    # Existing documents won't have this field initially
    # New documents will have it
    # Queries use Optional[str] for compatibility
    pass

async def downgrade():
    """Backward migration: Remove phone field"""
    # Remove the field from all documents
    result = await User.find().update(
        {"$unset": {"phone": ""}}
    )
    print(f"Removed phone from {result.modified_count} documents")

# Running migrations:
# production_db$ beanie migrate upgrade 001
# production_db$ beanie migrate downgrade 001
```

### 1.3 Breaking Change Patterns

```
Non-Breaking Changes (Can deploy immediately):
├─ Add new optional field
├─ Add new collection
├─ Add new index
├─ Remove unused field (with cleanup phase first)
├─ Rename field (with dual-write phase)
└─ Change field type (with coercion)

Breaking Changes (Require migration):
├─ Make required field optional
├─ Change field type incompatibly
├─ Delete required field
├─ Add required field
├─ Rename required field
└─ Change array to single value

Safe Migration Process:

Phase 1: Code Deployment
├─ Deploy code that supports both old and new format
├─ Make old format optional
├─ Add new format as optional
├─ Enable dual-write if needed

Phase 2: Data Migration
├─ Background job migrates existing data
├─ Dual-read from new format
├─ Monitor for errors

Phase 3: Cleanup
├─ Remove old field support from code
├─ Remove dual-write logic
├─ Archive old data if needed

Phase 4: Rollback Capability
├─ Keep backup available for 30 days
├─ Document rollback procedure
├─ Alert if rollback needed
```

---

## 2. Backup and Recovery

### 2.1 Backup Strategy

```
Backup Tier Architecture:

Tier 1: Live Replicas (RTO: < 1 min, RPO: < 1 sec)
├─ Primary + 2 secondary replicas
├─ Automatic failover
├─ Synchronous replication
└─ Storage: All data in-memory + disk

Tier 2: Hourly Snapshots (RTO: 1 hour, RPO: 1 hour)
├─ Schedule: Every hour at :00
├─ Destination: S3 Standard
├─ Retention: 7 days (hot)
├─ Size: ~100 GB per snapshot
└─ Time: ~10 minutes to backup

Tier 3: Daily Full Backup (RTO: 2 hours, RPO: 1 day)
├─ Schedule: Daily at 2 AM UTC
├─ Destination: S3 Standard
├─ Retention: 30 days (warm)
├─ Size: ~2 TB per backup
└─ Time: ~30 minutes to backup

Tier 4: Weekly Archive (RTO: 4 hours, RPO: 1 week)
├─ Schedule: Every Sunday at 2 AM UTC
├─ Destination: S3 Glacier
├─ Retention: 7 years (cold)
├─ Compression: 10:1 (typical)
└─ Time: ~1 hour to backup
```

### 2.2 Backup Execution

```bash
# MongoDB backup commands

# Online backup using mongodump
mongodump \
  --uri="mongodb+srv://user:pass@cluster/db?retryWrites=true" \
  --archive=backup_$(date +%Y%m%d_%H%M%S).archive \
  --gzip

# Upload to S3
aws s3 cp backup_*.archive s3://nans-backups/hourly/

# Point-in-time recovery
mongorestore \
  --archive=backup_20260623_020000.archive \
  --gzip \
  --oplogReplay \
  --uri="mongodb+srv://user:pass@restore-cluster/db"

# Verify backup integrity
mongorestore --archive=backup.archive --dryRun --gzip

# List available backups
aws s3 ls s3://nans-backups/ --recursive --human-readable
```

### 2.3 Disaster Recovery Procedure

```
Recovery Time Objectives (RTO):

Scenario: Data Corruption in Production

RTO by Severity:
├─ P0 (Full outage): < 15 minutes to restore
│   ├─ Failover to replica: 1 minute
│   └─ Restore from backup: 5-10 minutes
│
├─ P1 (Partial corruption): < 1 hour
│   ├─ Identify affected collections
│   ├─ Restore to point-in-time
│   └─ Verify data integrity
│
├─ P2 (Single document corrupt): < 4 hours
│   ├─ Restore specific document from backup
│   ├─ Manual verification
│   └─ Gradual rollout
│
└─ P3 (Audit trail): 24 hours (non-blocking)
    └─ Restore audit_logs collection separately

Recovery Steps:

1. Immediate Assessment (< 5 minutes)
   ├─ Determine scope of corruption
   ├─ Identify affected data range
   ├─ Assess user impact
   └─ Decide: Failover vs. Restore vs. Rollback

2. Failover to Replica (if P0)
   ├─ Trigger automatic failover
   ├─ Promote secondary to primary
   ├─ Verify all services healthy
   └─ Estimated time: 1 minute

3. Backup Retrieval (if data corruption)
   ├─ Identify appropriate backup
   ├─ Validate backup integrity
   ├─ Stage restore on staging cluster
   ├─ Verify data quality
   └─ Estimated time: 10-30 minutes

4. Data Restoration
   ├─ Stop applications (brief downtime)
   ├─ Restore from backup to point-in-time
   ├─ Verify collection counts match
   ├─ Run data integrity checks
   └─ Estimated time: 5-15 minutes

5. Validation & Testing
   ├─ Test critical queries
   ├─ Verify relationships are intact
   ├─ Check audit trail completeness
   └─ Estimated time: 5-10 minutes

6. Failback to Production
   ├─ Gradual traffic shift
   ├─ Monitor error rates
   ├─ Confirm all systems healthy
   └─ Estimated time: 5 minutes

7. Post-Recovery Actions
   ├─ Root cause analysis
   ├─ Implement preventive measures
   ├─ Document lessons learned
   └─ Update runbooks
```

---

## 3. Data Migration Scenarios

### 3.1 Adding a New Field

```python
# Scenario: Add timezone field to Organization

# Step 1: Deploy code with optional field
class Organization(Document):
    # ...existing fields...
    timezone: str = "UTC"  # New field, default value
    
    class Settings:
        collection = "organizations"

# Step 2: Background migration to populate new field
# app/migrations/002_add_timezone_to_orgs.py

async def populate_timezone():
    """Populate timezone for existing organizations"""
    # Query by timezone not set
    orgs = await Organization.find(
        Organization.timezone == None
    ).to_list(None)
    
    for org in orgs:
        # Infer from location or use default
        if org.location:
            org.timezone = infer_timezone_from_location(org.location)
        else:
            org.timezone = "UTC"
        await org.save()
    
    return len(orgs)

# Step 3: Run migration
# python -m app.migrations.002_add_timezone_to_orgs

# Step 4: Verify migration
# Query to ensure all orgs have timezone set
```

### 3.2 Renaming a Field

```python
# Scenario: Rename 'phone' to 'phone_primary' in User

# Step 1: Add new field, keep old one
# Dual-write in code: Set both fields
class User(Document):
    phone: Optional[str] = None  # Old field (deprecated)
    phone_primary: Optional[str] = None  # New field
    
    async def set_phone(self, phone: str):
        """Set phone in both old and new field"""
        self.phone = phone
        self.phone_primary = phone

# Step 2: Deploy code with dual-write
# New documents use phone_primary
# Old documents still have phone
# Code reads from phone_primary, falls back to phone

# Step 3: Backfill existing data
# app/migrations/003_rename_phone_to_phone_primary.py

async def migrate_phone_field():
    """Migrate phone to phone_primary"""
    # Find all users with old phone field
    result = await User.find(
        User.phone != None,
        User.phone_primary == None
    ).update(
        {"$set": {"phone_primary": "$phone"}},
        multi=True
    )
    return result.modified_count

# Step 4: Remove old field support
# After backfill, update code to only use phone_primary
class User(Document):
    phone_primary: Optional[str] = None  # Only new field

# Step 5: Clean up old field
# Optional: Remove from all documents after rollout period

async def remove_old_phone_field():
    """Remove deprecated phone field"""
    result = await User.find().update(
        {"$unset": {"phone": ""}},
        multi=True
    )
    return result.modified_count
```

### 3.3 Changing Field Type

```python
# Scenario: Change meeting.capacity from int to int/unlimited

# Before: capacity: int = 100
# After: capacity: Optional[int] = None (None = unlimited)

# Step 1: Add new field
class Meeting(Document):
    capacity: Optional[int] = None  # New field (optional)
    capacity_limit: Optional[int] = None  # Old field (deprecated)

# Step 2: Code handles both
def get_capacity(meeting):
    if meeting.capacity is not None:
        return meeting.capacity
    elif meeting.capacity_limit is not None:
        return meeting.capacity_limit
    else:
        return None  # Unlimited

# Step 3: Migrate data
async def migrate_capacity():
    """Migrate capacity_limit to capacity"""
    await Meeting.find().update(
        {"$rename": {"capacity_limit": "capacity"}},
        multi=True
    )

# Step 4: Remove old field references
# Update code to only use capacity
```

### 3.4 Combining Collections

```python
# Scenario: Merge audit_logs into activity_log collection

# Before: Separate audit_logs and activity_logs collections
# After: Single unified_logs collection with type discriminator

# Step 1: Create new unified collection schema
class UnifiedLog(Document):
    log_id: str
    log_type: Literal["audit", "activity"]
    timestamp: datetime
    # ... common fields ...
    
    class Settings:
        collection = "unified_logs"

# Step 2: Copy data from old collections
async def migrate_to_unified():
    """Migrate to unified collection"""
    
    # Copy audit logs
    audit_logs = await AuditLog.find().to_list(None)
    for log in audit_logs:
        unified = UnifiedLog(
            log_id=str(log._id),
            log_type="audit",
            # ... map fields ...
        )
        await unified.insert()
    
    # Copy activity logs
    activity_logs = await ActivityLog.find().to_list(None)
    for log in activity_logs:
        unified = UnifiedLog(
            log_id=str(log._id),
            log_type="activity",
            # ... map fields ...
        )
        await unified.insert()

# Step 3: Switch read queries to new collection
# Code queries UnifiedLog instead of separate collections

# Step 4: Validate data completeness
# Query count from unified vs old collections

# Step 5: Archive old collections
# Keep for 30 days, then delete
```

---

## 4. Indexing Maintenance

### 4.1 Index Management

```python
# Create indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.organizations.createIndex(
    { parent_id: 1, status: 1 },
    { background: true }  # Don't block writes
)

# List indexes
db.users.getIndexes()

# Drop index
db.users.dropIndex("email_1")

# Rebuild indexes
db.users.reIndex()

# Get index statistics
db.users.aggregate([
    { $indexStats: {} }
])
```

### 4.2 Index Performance Tuning

```python
# Find slow queries using profiler
db.setProfilingLevel(1, { slowms: 100 })

# Query explain plan
db.users.find({status: "active"}).explain("executionStats")

# Check if query uses index
explain_result = db.users.find(
    {email: "user@example.com"}
).explain("executionStats")

if "COLLSCAN" in str(explain_result):
    print("WARNING: Full collection scan!")
else:
    print("Using index:", explain_result)

# Monitor index usage
db.aggregate([
    { $indexStats: {} },
    { $match: { "accesses.ops": { $gt: 0 } } },
    { $sort: { "accesses.ops": -1 } }
])
```

### 4.3 Unused Index Cleanup

```python
# Find unused indexes
db.aggregate([
    { $indexStats: {} },
    { $match: { "accesses.ops": 0 } }
])

# Drop unused indexes
for index in unused_indexes:
    db[index['ns']['coll']].dropIndex(index['name'])
```

---

## 5. Data Validation and Integrity

### 5.1 Consistency Checks

```python
# Verify referential integrity

async def verify_referential_integrity():
    """Check all foreign key references are valid"""
    
    # Check: All meeting registrations point to valid meetings
    invalid_registrations = []
    registrations = await MeetingRegistration.find().to_list(None)
    
    for reg in registrations:
        meeting = await Meeting.get(reg.meeting_id)
        if not meeting:
            invalid_registrations.append(reg._id)
    
    if invalid_registrations:
        print(f"WARNING: {len(invalid_registrations)} orphan registrations")
        # Fix: Delete or handle orphans
        await MeetingRegistration.find(
            MeetingRegistration._id.in_(invalid_registrations)
        ).delete()
    
    return len(invalid_registrations)

# Run regularly
# Scheduled job: Daily at 3 AM UTC
```

### 5.2 Data Quality Checks

```python
# Verify data quality

async def verify_data_quality():
    """Check for data quality issues"""
    
    issues = []
    
    # Check 1: Users without email verification after 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    stale_unverified = await User.find(
        User.is_verified == False,
        User.created_at < thirty_days_ago
    ).count()
    
    if stale_unverified > 0:
        issues.append(f"Stale unverified users: {stale_unverified}")
    
    # Check 2: Organizations with no members
    empty_orgs = await Organization.find(
        Organization.active_member_count == 0
    ).count()
    
    if empty_orgs > 0:
        issues.append(f"Empty organizations: {empty_orgs}")
    
    # Check 3: Meetings in past without completion status
    past_incomplete = await Meeting.find(
        Meeting.scheduled_at < datetime.utcnow(),
        Meeting.status != "completed",
        Meeting.status != "cancelled"
    ).count()
    
    if past_incomplete > 0:
        issues.append(f"Uncompleted past meetings: {past_incomplete}")
    
    return issues
```

---

## 6. Performance Monitoring

### 6.1 Query Performance

```python
# Analyze query performance

async def analyze_query_performance():
    """Get statistics on query execution"""
    
    stats = db.command("aggregate", "users", pipeline=[
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "count": {"$sum": 1}}}
    ])
    
    # Check execution time
    if stats.get("executionStats", {}).get("executionStages", {}).get("stage") == "COLLSCAN":
        print("WARNING: Query performs full collection scan")
    
    return stats

# Monitor slow queries
slow_query_threshold = 100  # ms

db.system.profile.find({
    "millis": {"$gt": slow_query_threshold}
}).sort({"ts": -1}).limit(10)
```

### 6.2 Storage Usage

```python
# Monitor storage

db.command("collStats", "users")

# Get total database size
db.command("dbStats")

# Storage by collection
for collection_name in db.list_collection_names():
    stats = db.command("collStats", collection_name)
    size_mb = stats['size'] / (1024 * 1024)
    print(f"{collection_name}: {size_mb:.2f} MB")
```

---

## 7. Archival Strategy

### 7.1 Cold Storage

```python
# Archive old data to cold storage

async def archive_completed_meetings():
    """Move completed meetings older than 1 year to archive"""
    
    cutoff_date = datetime.utcnow() - timedelta(days=365)
    
    # Find meetings to archive
    old_meetings = await Meeting.find(
        Meeting.status == "completed",
        Meeting.end_time < cutoff_date
    ).to_list(None)
    
    print(f"Found {len(old_meetings)} meetings to archive")
    
    # Export to archive collection
    for meeting in old_meetings:
        archive_doc = {
            "original_id": meeting._id,
            "data": meeting.dict(),
            "archived_at": datetime.utcnow(),
            "source_collection": "meetings"
        }
        await db.meetings_archive.insert_one(archive_doc)
    
    # Delete from live collection
    result = await Meeting.find(
        Meeting.status == "completed",
        Meeting.end_time < cutoff_date
    ).delete()
    
    return result.deleted_count

# Schedule: Monthly
# CronJob: 0 2 1 * * (1st of month at 2 AM)
```

### 7.2 Archive Retrieval

```python
# Retrieve archived data

async def restore_from_archive(original_id: PydanticObjectId):
    """Restore archived meeting back to live collection"""
    
    archive_doc = await db.meetings_archive.find_one(
        {"original_id": original_id}
    )
    
    if not archive_doc:
        raise ValueError(f"No archived meeting found: {original_id}")
    
    # Restore to live collection
    meeting = Meeting(**archive_doc["data"])
    await meeting.insert()
    
    # Remove from archive
    await db.meetings_archive.delete_one({"_id": archive_doc["_id"]})
    
    return meeting
```

---

## 8. Checklists

### 8.1 Pre-Production Deployment Checklist

```
Database Deployment Checklist:

Schema Changes:
  ☐ All migrations are backward compatible
  ☐ Migrations tested on staging
  ☐ Rollback procedure documented
  ☐ Data migration scripts verified
  ☐ Model versioning updated

Indexes:
  ☐ New indexes created on staging
  ☐ Query performance tested
  ☐ Index maintenance scheduled
  ☐ No duplicate indexes

Backups:
  ☐ Backup completed and verified
  ☐ Restore test performed
  ☐ Backup retention policy current
  ☐ Backup location accessible

Monitoring:
  ☐ Query performance baseline established
  ☐ Slow query logging enabled
  ☐ Alerts configured for storage usage
  ☐ Alerts configured for replication lag

Documentation:
  ☐ Schema changes documented
  ☐ Migration procedure documented
  ☐ Rollback procedure documented
  ☐ Runbook updated
```

### 8.2 Post-Production Deployment Checklist

```
Post-Deployment Verification:

Immediate (First hour):
  ☐ All queries execute successfully
  ☐ New fields populated correctly
  ☐ No unexpected errors in logs
  ☐ Data integrity checks passed
  ☐ Performance metrics normal

Short-term (First 24 hours):
  ☐ Data consistency verified
  ☐ Audit trail complete
  ☐ Referential integrity maintained
  ☐ No orphaned documents
  ☐ Backup captures new schema

Long-term (First week):
  ☐ No migration-related support issues
  ☐ Query performance acceptable
  ☐ Storage usage within limits
  ☐ Replication lag minimal
  ☐ No data anomalies detected
```

