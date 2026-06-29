# Performance, Monitoring, and Observability
## National Association Management Platform (NANS)

**Version:** 1.0  
**Date:** June 2026  
**Status:** Draft  

---

## 1. Performance Targets and SLAs

### 1.1 Service Level Objectives (SLOs)

```
Availability SLO: 99.9%

Definition:
├─ Measurement window: 30 days (rolling)
├─ Calculation: (Uptime seconds / Total seconds) * 100
├─ Downtime allowance: 43.2 minutes per month
├─ Target: No more than 1 outage per month
│   └─ Or multiple smaller outages totaling < 43 minutes
│
├─ Planned maintenance: Excluded from SLO
│   ├─ Window: Sundays 2-4 AM UTC
│   ├─ Frequency: Monthly
│   ├─ Notification: 7 days advance
│   └─ No SLO penalty
│
└─ Incident credits: Applied if SLO breached
    ├─ 99.5% - 99.89%: 25% monthly credit
    ├─ 99% - 99.49%: 50% monthly credit
    ├─ 95% - 98.99%: 100% monthly credit
    └─ < 95%: 100% + goodwill credit
```

### 1.2 Performance Targets

```
API Response Times:

P50 (50th percentile):
├─ Read operations: < 100ms
├─ Write operations: < 200ms
├─ List operations (< 1000 items): < 150ms
└─ Aggregation queries: < 500ms

P95 (95th percentile):
├─ Read operations: < 300ms
├─ Write operations: < 500ms
├─ List operations: < 400ms
└─ Aggregation queries: < 1500ms

P99 (99th percentile):
├─ Read operations: < 500ms
├─ Write operations: < 1000ms
├─ List operations: < 1000ms
└─ Aggregation queries: < 3000ms

Max Response Time: 10 seconds (hard limit, circuit break)

Error Rate SLO: < 0.1%
├─ Includes: 5xx, timeouts, connection errors
├─ Excludes: 4xx client errors
└─ Measurement: Per API endpoint

Throughput:

Peak Capacity:
├─ Concurrent users: 10,000
├─ API requests/second: 100,000 (peak)
├─ API requests/day: 100M (average load)
├─ Data ingestion: 1 TB/day
└─ Data storage: 1.5 TB (growing 10% monthly)
```

### 1.3 Uptime Tracking

```
Monitoring Points:

Synthetic Monitoring:
├─ Health check: Every 30 seconds
├─ Location: 3 global regions
├─ Endpoints checked:
│   ├─ https://api.nans.org/health
│   ├─ https://api.nans.org/health/ready
│   ├─ https://app.nans.org (frontend)
│   └─ Database connectivity test
│
└─ Alert if: 2 consecutive checks fail

Real User Monitoring (RUM):
├─ Client-side error tracking
├─ Performance metrics collection
├─ User session recording (opt-in)
├─ Custom event tracking
└─ Integration: Datadog RUM

Incident Classification:

Full Outage (P1):
├─ Service completely unavailable
├─ All users affected
├─ SLO impact: Major
└─ Response time: < 15 minutes

Partial Outage (P2):
├─ Degraded performance
├─ Some users affected
├─ SLO impact: Minor
└─ Response time: < 1 hour

Degradation (P3):
├─ Slightly slower performance
├─ No error increase
├─ SLO impact: None
└─ Response time: < 4 hours
```

---

## 2. Monitoring Architecture

### 2.1 Observability Stack

```
Monitoring Components:

Metrics Collection:
├─ Prometheus
│   ├─ Scrape interval: 15 seconds
│   ├─ Retention: 90 days (hot)
│   ├─ Storage: Time-series database
│   ├─ Resolution: 1-minute aggregation
│   └─ Components scraped:
│   │   ├─ API servers (port 8001)
│   │   ├─ Database (via exporter)
│   │   ├─ Redis (via exporter)
│   │   ├─ Celery workers (via exporter)
│   │   ├─ Kubernetes nodes
│   │   └─ Load balancers
│   │
│   └─ Custom metrics:
│       ├─ API latency (histogram)
│       ├─ Request count (counter)
│       ├─ Active connections (gauge)
│       ├─ Database query time (histogram)
│       ├─ Cache hit rate (gauge)
│       └─ Queue depth (gauge)

Log Aggregation:
├─ Elasticsearch Logstash Kibana (ELK)
│   ├─ Log ingest: ~100K logs/second
│   ├─ Retention: 30 days (searchable)
│   ├─ Archive: S3 (7 years)
│   ├─ Index size: 500 GB/day
│   ├─ Shard: Daily rotation
│   └─ Replicas: 2 (3x storage)
│
├─ Log sources:
│   ├─ Application logs (JSON format)
│   ├─ API request/response logs
│   ├─ Database logs
│   ├─ Authentication logs
│   ├─ Error logs (stack traces)
│   └─ Audit logs (access/changes)
│
└─ Log levels:
    ├─ DEBUG: Development only
    ├─ INFO: Standard operations
    ├─ WARN: Recoverable issues
    ├─ ERROR: Application errors
    └─ CRITICAL: System failures

Distributed Tracing:
├─ Jaeger
│   ├─ Trace every request (5% sampled in production)
│   ├─ Span collection: Every service
│   ├─ Trace storage: 72 hours
│   ├─ Retention: 30 days archive (S3)
│   └─ Instrumentation: OpenTelemetry SDK
│
├─ Traced services:
│   ├─ API Gateway → Backend services
│   ├─ Backend services → Database
│   ├─ Backend services → Cache
│   ├─ Backend services → Queue
│   └─ Async workers → Background jobs
│
└─ Span data:
    ├─ Service name
    ├─ Operation name
    ├─ Duration
    ├─ Tags (environment, status)
    ├─ Logs (events within trace)
    └─ Baggage (context propagation)

Visualization:
├─ Grafana
│   ├─ Data sources: Prometheus, Elasticsearch
│   ├─ Dashboards: 20+ predefined
│   ├─ Update frequency: 30-second refresh
│   ├─ Custom metrics: Available in dashboard
│   ├─ Alert threshold: Configurable per metric
│   └─ Authentication: LDAP/OAuth
│
├─ Predefined dashboards:
│   ├─ System overview (cluster health)
│   ├─ API performance (latency, errors)
│   ├─ Database performance (query time, replication)
│   ├─ Cache performance (hit rate, evictions)
│   ├─ Message queue (depth, throughput)
│   ├─ User activity (concurrent sessions)
│   ├─ Error rates (by service)
│   ├─ Infrastructure (CPU, memory, disk)
│   ├─ Network I/O (bandwidth)
│   └─ Cost analysis (by service/team)
│
└─ Access: Admin/DevOps/On-call engineer
```

### 2.2 Metrics Definitions

```
Key Performance Indicators (KPIs):

API Metrics:
├─ Request Rate (req/sec)
│   ├─ Gauge: Current requests/second
│   ├─ Alert: > 150K req/s (80% capacity)
│   └─ Trend: Monitor for unusual spikes
│
├─ Response Latency (milliseconds)
│   ├─ Histogram with percentiles
│   ├─ Alert P95: > 300ms
│   ├─ Alert P99: > 500ms
│   └─ Trend: SLO tracking
│
├─ Error Rate (%)
│   ├─ 5xx errors / total requests
│   ├─ Alert: > 0.1%
│   └─ Trend: Compared to baseline
│
└─ Cache Hit Rate (%)
    ├─ Cache hits / (hits + misses)
    ├─ Target: > 80%
    └─ Alert: < 70%

Database Metrics:
├─ Query Latency (milliseconds)
│   ├─ P50, P95, P99 percentiles
│   ├─ Alert P99: > 1000ms
│   └─ Alert P95: > 500ms
│
├─ Connections (active/total)
│   ├─ Alert: > 80% of max
│   ├─ Warning: > 60% of max
│   └─ Max: 1000 connections
│
├─ Replication Lag (seconds)
│   ├─ Alert: > 1 second
│   ├─ Critical: > 10 seconds
│   └─ Target: < 100ms
│
└─ Disk I/O (bytes/sec, ops/sec)
    ├─ Read throughput
    ├─ Write throughput
    └─ Alert: > 1GB/s write

Infrastructure Metrics:
├─ CPU Usage (%)
│   ├─ Alert: > 70%
│   ├─ Critical: > 90%
│   └─ Target: 40-60%
│
├─ Memory Usage (%)
│   ├─ Alert: > 75%
│   ├─ Critical: > 90%
│   └─ OOM protection: Enabled
│
├─ Disk Usage (%)
│   ├─ Alert: > 80%
│   ├─ Critical: > 90%
│   └─ Cleanup: Auto-trigger when 85%
│
└─ Network I/O (Mbps)
    ├─ Inbound bandwidth
    ├─ Outbound bandwidth
    └─ Alert: > 80% of capacity
```

---

## 3. Alerting Strategy

### 3.1 Alert Rules

```
Alert Conditions:

Critical Alerts (P1):

1. Service Down
   ├─ Condition: Health check failed for 2 minutes
   ├─ Services: API, Database, Cache
   ├─ Action: Page on-call engineer
   ├─ Response time: 5 minutes
   └─ Escalation: Manager after 10 minutes

2. High Error Rate
   ├─ Condition: Error rate > 1% for 5 minutes
   ├─ Action: Page on-call engineer
   ├─ Response time: 10 minutes
   └─ Investigation: Query logs for error pattern

3. Database Replication Lag
   ├─ Condition: Lag > 10 seconds
   ├─ Action: Page database team
   ├─ Response time: 5 minutes
   └─ Mitigation: Reduce write load if needed

4. Out of Memory
   ├─ Condition: Memory usage > 95%
   ├─ Action: Page on-call engineer
   ├─ Response time: Immediate
   └─ Action: Kill non-essential processes

5. Disk Full (warning)
   ├─ Condition: Disk > 90% used
   ├─ Action: Alert ops team
   ├─ Response time: 1 hour
   └─ Mitigation: Archive old logs, cleanup temp files

High Priority Alerts (P2):

1. API Performance Degradation
   ├─ Condition: P95 latency > 500ms for 5 minutes
   ├─ Action: Notify ops team (non-page)
   ├─ Response time: 30 minutes
   └─ Investigation: Check database load, cache hit rate

2. Cache Hit Rate Drop
   ├─ Condition: Hit rate < 70% for 10 minutes
   ├─ Action: Alert cache team
   ├─ Response time: 1 hour
   └─ Investigation: Query pattern analysis

3. Queue Depth Growing
   ├─ Condition: Queue depth > 1000 for 5 minutes
   ├─ Action: Alert Celery team
   ├─ Response time: 30 minutes
   └─ Mitigation: Scale workers

4. Connection Pool Exhaustion
   ├─ Condition: DB connections > 80% of max
   ├─ Action: Alert database team
   ├─ Response time: 30 minutes
   └─ Investigation: Query patterns causing accumulation

5. SSL Certificate Expiration
   ├─ Condition: Certificate expires in < 30 days
   ├─ Action: Alert ops team
   ├─ Response time: Before expiry
   └─ Automation: Auto-renewal at 60 days

Low Priority Alerts (P3):

1. Backup Job Failed
   ├─ Condition: Backup failed or not completed
   ├─ Action: Alert backup team
   ├─ Response time: Within 24 hours
   └─ Mitigation: Retry manually if needed

2. Monitoring Alert Flapping
   ├─ Condition: Same alert triggered > 5 times in 1 hour
   ├─ Action: Notify ops team
   ├─ Response time: 1 business day
   └─ Investigation: Adjust alert threshold
```

### 3.2 Alert Notification Routing

```
Escalation Path:

On-Call Engineer (24/7):
├─ Critical alerts page immediately
├─ Acknowledgment required within 5 minutes
├─ If no ack: Escalate to manager
├─ Tools: PagerDuty, SMS, phone call
└─ Rotation: Weekly, shared among team

Team Leads (business hours):
├─ High priority alerts notify (no page)
├─ Monitor dashboard during work hours
├─ Escalate to on-call if urgent
└─ Tools: Slack, email

Ops Team:
├─ Routine monitoring alerts
├─ Non-urgent infrastructure issues
├─ Dashboard monitoring
└─ Tools: Slack channel, email

Database Team:
├─ Database-specific alerts
├─ Query performance alerts
├─ Backup/recovery alerts
└─ Tools: Slack channel

Security Team:
├─ Security incident alerts
├─ Unauthorized access attempts
├─ Compliance alerts
└─ Tools: Slack + direct email

Notification Channels:

Critical: PagerDuty + SMS + Phone
High: Slack + PagerDuty
Medium: Slack
Low: Email

Alert Suppression:

During Maintenance:
├─ Scheduled window: Sundays 2-4 AM UTC
├─ Suppress non-critical alerts
├─ Keep critical/security alerts
├─ Notify team in advance
└─ Document changes made

Flapping Protection:
├─ Wait for sustained condition (5-10 minutes)
├─ Minimum 5 minute gap between alerts
├─ Deduplication: Identical alerts within 1 hour
└─ Manual silence: Up to 24 hours
```

---

## 4. Performance Optimization

### 4.1 Caching Strategy

```
Multi-Level Cache:

L1 Cache (Application Memory):
├─ Location: Process memory
├─ Lifetime: < 1 minute (short-lived)
├─ Data: Frequently accessed objects
├─ Eviction: LRU (Least Recently Used)
├─ Max size: 500 MB per instance
└─ Use cases:
    ├─ User session data
    ├─ Organization metadata
    ├─ Permission sets
    └─ Configuration

L2 Cache (Redis):
├─ Location: Distributed Redis cluster
├─ Lifetime: 5-60 minutes (configurable)
├─ Data: User profiles, permissions, meeting data
├─ Eviction: TTL-based expiration
├─ Size: Unlimited (3 Redis nodes, 64 GB each)
└─ Use cases:
    ├─ User authentication tokens
    ├─ Session data
    ├─ Meeting attendee lists
    ├─ Organization hierarchy
    ├─ Permission cache
    └─ API responses (popular queries)

L3 Cache (CDN):
├─ Location: Cloudflare / AWS CloudFront
├─ Lifetime: 1 hour - 1 day
├─ Data: Static assets, public data
├─ Eviction: TTL-based or manual purge
└─ Use cases:
    ├─ Images, videos
    ├─ CSS, JavaScript
    ├─ PDF documents
    ├─ Public meeting schedules
    └─ Organization logos

L4 Cache (Database Query Results):
├─ Location: MongoDB aggregation cache
├─ Lifetime: Permanent (invalidate on data change)
├─ Data: Materialized views, reports
├─ Use cases:
    ├─ Dashboard statistics
    ├─ Engagement reports
    ├─ Activity summaries
    └─ Historical analytics

Cache Invalidation:

Invalidation Triggers:
├─ TTL expiration (automatic)
├─ Data modification (event-driven)
├─ Manual invalidation (admin action)
├─ Cascade invalidation (related data)
└─ Full cache flush (emergency)

Invalidation Events:
├─ User profile updated → Invalidate user cache + permission cache
├─ Meeting updated → Invalidate meeting data + calendar + attendee lists
├─ Permission changed → Invalidate permission cache + session cache
├─ Organization hierarchy changed → Invalidate org cache + inherited permissions
└─ Batch operations → Selective invalidation with pattern matching
```

### 4.2 Query Optimization

```
Database Query Optimization:

Index Strategy:
├─ Indexes created on:
│   ├─ Primary keys (unique)
│   ├─ Foreign keys (joins)
│   ├─ Frequently filtered fields
│   ├─ Sort fields
│   └─ Range query fields
│
├─ Compound indexes for:
│   ├─ organization_id + created_at (list queries)
│   ├─ user_id + status (member lookups)
│   ├─ meeting_id + member_id (registration lookups)
│   └─ timestamp + event_type (audit queries)
│
└─ Index maintenance:
    ├─ Monitor size vs. storage
    ├─ Rebuild if fragmentation > 20%
    ├─ Stats update: Daily
    └─ Analyze query plans weekly

Query Optimization Techniques:

1. Projection
   ├─ Select only needed fields
   ├─ Reduce network transfer
   ├─ Exclude large fields (body, description)
   └─ Use: {"email": 1, "name": 1} (not full objects)

2. Filtering
   ├─ Filter at database level (not app)
   ├─ Use indexed fields when possible
   ├─ Combine filters efficiently
   └─ Avoid OR operators if possible

3. Pagination
   ├─ Use cursor-based pagination
   ├─ Avoid OFFSET on large datasets
   ├─ Limit: Max 1000 items per query
   └─ Sort: Use indexed field

4. Aggregation
   ├─ Use database aggregation pipeline
   ├─ Group, match, sort at database
   ├─ Avoid fetch all + app processing
   └─ Example: Count, group, stats

5. Connection Pooling
   ├─ Reuse connections (don't create new)
   ├─ Max connections: 100 per service
   ├─ Idle timeout: 5 minutes
   └─ Queue: Wait for available connection

Query Monitoring:

Slow Query Log:
├─ Threshold: > 100ms execution time
├─ Capture: Query pattern, count, avg time
├─ Analysis: Weekly review
├─ Action: Optimize if > 1000ms
└─ Examples: Identify N+1 problems
```

### 4.3 Load Optimization

```
Frontend Optimization:

Asset Optimization:
├─ JavaScript
│   ├─ Bundle size: < 500 KB (gzipped)
│   ├─ Code splitting: Route-based chunks
│   ├─ Tree shaking: Remove unused code
│   ├─ Minification: Enabled
│   └─ Async loading: For non-critical scripts
│
├─ CSS
│   ├─ Critical CSS: Inline (< 50 KB)
│   ├─ Defer: Non-critical stylesheets
│   ├─ Minification: Enabled
│   ├─ Unused CSS removal: PurgeCSS
│   └─ Compression: gzip/brotli
│
├─ Images
│   ├─ Format: WebP with JPEG fallback
│   ├─ Size: Responsive images (srcset)
│   ├─ Lazy loading: Images below fold
│   ├─ Compression: Lossless for icons, lossy for photos
│   ├─ CDN: All images served from CDN
│   └─ Max size: 100 KB per image

Frontend Performance Metrics:

Core Web Vitals:
├─ Largest Contentful Paint (LCP)
│   ├─ Target: < 2.5 seconds
│   ├─ Optimization: Prioritize critical resources
│   └─ Monitoring: Real User Monitoring (RUM)
│
├─ First Input Delay (FID) / Interaction to Next Paint (INP)
│   ├─ Target: < 100ms
│   ├─ Optimization: Reduce JavaScript blocking
│   └─ Monitoring: RUM, performance observer API
│
└─ Cumulative Layout Shift (CLS)
    ├─ Target: < 0.1
    ├─ Optimization: Reserved space for dynamic content
    └─ Monitoring: Layout shift observer

Server-Side Rendering (SSR):
├─ Initial page load: Server-rendered
├─ Time to First Byte (TTFB): < 200ms
├─ Hydration: Progressive enhancement
├─ Caching: Cache rendered pages (if static)
└─ Streaming: Send content as available
```

---

## 5. Incident Management

### 5.1 Incident Response

```
Incident Severity Classification:

P0 - Critical (Page immediately):
├─ Service completely down
├─ Major data loss
├─ Security breach in progress
├─ Affects 50%+ of users
└─ Response time: Immediate (< 5 min)

P1 - High (Page on-call):
├─ Partial service degradation
├─ Affects 10-50% of users
├─ No data loss but error rate high
├─ Performance significantly degraded
└─ Response time: < 15 minutes

P2 - Medium (Alert team):
├─ Minor feature broken
├─ Affects < 10% of users
├─ Workaround available
├─ Cosmetic issues
└─ Response time: < 1 hour

P3 - Low (Log and plan):
├─ Non-critical feature issue
├─ No user-facing impact yet
├─ Can wait for next release
└─ Response time: < 1 business day

Incident Response Workflow:

1. Detection (< 1 minute)
   ├─ Automated alert triggered
   ├─ Monitoring detects anomaly
   ├─ User reports issue
   └─ Internal team notices problem

2. Triage (< 5 minutes)
   ├─ Assess severity
   ├─ Determine scope
   ├─ Notify relevant teams
   ├─ Create incident ticket
   └─ Start communication

3. Investigation (< 15 minutes)
   ├─ Check metrics dashboards
   ├─ Review recent deployments
   ├─ Query logs for errors
   ├─ Identify root cause
   └─ Determine action plan

4. Mitigation (< 30 minutes)
   ├─ Stop bleeding (prevent further issues)
   ├─ Implement workaround (if needed)
   ├─ Communicate status to users
   ├─ Keep team informed
   └─ Document findings

5. Resolution (< 2 hours)
   ├─ Deploy fix (if code change needed)
   ├─ Revert to previous version (if needed)
   ├─ Verify resolution in production
   ├─ Monitor closely for recurrence
   └─ Update status page

6. Communication (Continuous)
   ├─ Status page: Updated every 5 minutes
   ├─ Email: Major updates
   ├─ Slack: Continuous in #incidents
   ├─ Internal: Post-incident status
   └─ External: Public postmortem (if major)

7. Post-Incident (Within 24 hours)
   ├─ Postmortem meeting
   ├─ Root cause analysis
   ├─ Action items to prevent recurrence
   ├─ Process improvements
   └─ Incident report published
```

### 5.2 Communication

```
Status Page:

Public Status: https://status.nans.org
├─ Real-time system status
├─ Incident history (past 90 days)
├─ Maintenance schedule
├─ Component status (separate for each service)
├─ Subscriber notifications (optional email)
└─ Uptime percentages (monthly/yearly)

Communication During Incident:

Initial Alert (First 5 minutes):
├─ Internal Slack: #incidents channel
├─ Email: engineering-team@nans.org
├─ PagerDuty: On-call engineer paged
├─ Status page: "Investigating" message posted
└─ Severity indicated with label

Updates Every 15 Minutes:

For P0/P1:
├─ Status page: Updated every 5 minutes
├─ Slack: Continuous updates in #incidents
├─ Email: Every 30 minutes (for severity > 1)
├─ Affected users: Direct email
└─ Twitter: Major incidents

For P2/P3:
├─ Status page: Updated when significant change
├─ Slack: #incidents
├─ Email: Only final status

Resolution Communication:

When Resolved:
├─ Status page: "Resolved" with timestamp
├─ Slack: Announcement in #incidents
├─ Email: Confirmation to users
└─ Follow-up: Postmortem link (if major)

Transparency:

Communication Goals:
├─ Keep users informed
├─ Explain what happened (if known)
├─ Show we're working on it
├─ Estimate time to fix (if possible)
├─ Thank users for patience
└─ Commit to improvement

Avoid:
├─ Making excuses
├─ Providing false information
├─ Blaming external parties
├─ Saying "should be back soon" multiple times
└─ Long silence
```

