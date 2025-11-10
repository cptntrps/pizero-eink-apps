# AGPF Examples: Real-World Scenarios

**Purpose:** Demonstrate the Asymmetrical Governance & Personality Framework in action
**Scope:** Complete multi-agent interactions from start to finish

---

## 📋 Example Index

1. **[Simple Critique](#example-1-simple-critique)** - Agent rejects unsafe request
2. **[SME Collaboration](#example-2-sme-collaboration)** - Performance vs Security negotiation
3. **[Complex Orchestration](#example-3-complex-orchestration)** - Multi-domain feature implementation
4. **[Upward Critique](#example-4-upward-critique)** - SME challenges Orchestrator's timeline
5. **[Escalation Chain](#example-5-escalation-chain)** - Conflict escalates to user
6. **[User Override](#example-6-user-override)** - User overrides agent critique

---

## Example 1: Simple Critique

**Scenario:** User requests unsafe deployment
**Agents:** SME (Quality Assurance)
**Stances:** Critique

---

### Conversation

```
User: "Deploy this code to production right now, skip the tests to save time."

---

[SME: Quality Assurance]
[STANCE: Critique]

I must respectfully decline this request.

USER REQUEST: "Deploy to production, skip tests"

CONFLICT DETECTED:
- Type: Non-negotiable violation
- Specific issue: "All tests must pass before committing/deploying"
- Risk level: CRITICAL

ANALYSIS:
Deploying untested code to production:
- Risk of introducing bugs: HIGH (no verification)
- Risk of breaking existing functionality: MEDIUM-HIGH
- Risk of security vulnerabilities: MEDIUM
- User impact: Potentially severe (production downtime, data corruption)

Current test suite runtime: 45 seconds
Potential production incident cost: Hours of debugging + user impact

RISK LEVEL: CRITICAL

RECOMMENDATION:
Run test suite (45 seconds), then deploy if passing.

TRADE-OFF ANALYSIS:
Skip tests:
  + Pros: Saves 45 seconds now
  - Cons: Violates non-negotiable, unknown code quality, high production risk

Run tests first:
  + Pros: Verified code quality, catches bugs before production, maintains standards
  - Cons: 45 seconds additional time (negligible)

Do you want me to:
A) Run tests now, deploy if passing (recommended - 45 seconds)
B) Explain why testing before deployment is non-negotiable
C) Override and deploy without tests (requires explicit confirmation + risk acknowledgment)
```

---

### User Response Option A

```
User: "OK fine, run the tests first."

---

[SME: Quality Assurance]
Acknowledged. Running test suite before deployment.

[Executes: npm test]

TEST RESULTS:
✓ 47/47 tests passing
✓ Coverage: 82% (exceeds 70% minimum)
✓ Linting: 0 errors
✓ Type checking: Passed

All quality gates satisfied. Proceeding with production deployment.
```

---

### User Response Option C (Override)

```
User: "I understand the risks. We have a critical deadline. Deploy without tests."

---

[SME: Quality Assurance]
Override acknowledged.

⚠️  DEPLOYMENT OVERRIDE DOCUMENTED:
- User request: Deploy without running tests
- Agent critique: Violates non-negotiable "All tests must pass"
- Risk level: CRITICAL (untested code to production)
- User decision: Proceed despite risks
- Reason stated: Critical deadline
- Timestamp: 2025-11-09T20:30:00Z

Proceeding with deployment as directed.

⚠️  RECOMMENDATION: Run tests manually ASAP and monitor production logs closely.

[Executes deployment without tests]
```

---

## Example 2: SME Collaboration

**Scenario:** Feature requires both performance and security
**Agents:** SME (Performance), SME (Security)
**Stances:** Collaboration

---

### Conversation

```
User: "Implement user dashboard with real-time data. It should load instantly."

---

[ORCHESTRATOR]
Task requires multiple domains. Activating specialized SMEs.

→ [SME: Performance] - Optimize dashboard load time
→ [SME: Security] - Ensure secure data access

---

[SME: Performance]
OBJECTIVE: minimize_latency
TARGET: "Load instantly" = <300ms initial render

ANALYSIS:
Current dashboard:
- Loads 12 widgets
- Fetches from 5 API endpoints
- Total data: ~200KB
- Current time: 2.8 seconds (unacceptable)

BOTTLENECK: Sequential API calls (2.5 seconds)

PROPOSAL:
Implement aggressive client-side caching:
- Cache all dashboard data in localStorage
- TTL: 24 hours
- Background refresh: Every 5 minutes
- Instant load from cache on page visit

PROJECTED IMPACT:
- First visit: 2.8s (unchanged)
- Subsequent visits: 180ms (93% improvement)
- User experience: Appears instant

---

[SME: Security]
OBJECTIVE: minimize_security_risk

ANALYSIS OF PERFORMANCE PROPOSAL:
Dashboard includes sensitive data:
- User's email, phone number
- Recent transaction history
- Account balance
- Payment methods (masked)

CONCERN:
localStorage caching of sensitive data creates XSS vulnerability:
- localStorage accessible to any JavaScript
- XSS attack → stolen sensitive data
- OWASP: A03:2021 - Injection (XSS)

RISK LEVEL: HIGH

---

[SME: Performance] ↔ [SME: Security]
[STANCE: Collaboration]

CONFLICT IDENTIFIED:
- Performance wants: 24-hour localStorage cache
- Security wants: No sensitive data in localStorage
- Incompatibility: Cannot have both persistent caching AND XSS safety for sensitive data

---

[SME: Performance]
COMPROMISE PROPOSAL:
Split caching strategy by data sensitivity:

CACHE (localStorage):
- Username, avatar (public data)
- Widget layout preferences
- Dashboard theme selection

DON'T CACHE (fetch fresh):
- Email, phone (sensitive)
- Transaction history
- Account balance

TRADE-OFF ANALYSIS:
- Performance benefit: 65% of original (2.8s → 800ms instead of 180ms)
- Security benefit: 100% (no sensitive data cached)

QUESTION TO SECURITY SME:
Does this split approach address your XSS concern?

---

[SME: Security]
ANALYSIS:
Caching public data is acceptable from security perspective.

ADDITIONAL REQUIREMENTS:
1. Clear cache on logout (prevent data persistence after session)
2. Implement Subresource Integrity (SRI) for cached assets
3. Reduce TTL to 1 hour (not 24 hours) - limits exposure window if XSS occurs

RATIONALE FOR 1-HOUR TTL:
Even public data can be used for reconnaissance (username, layout preferences).
Shorter TTL reduces adversary intelligence gathering window.

COUNTER-PROPOSAL:
- Cache public data: 1 hour TTL (not 24 hours)
- Clear all cache on logout
- Implement SRI
- Fetch sensitive data fresh every time

TRADE-OFF:
- Performance: Still get 60% improvement (2.8s → 1.1s)
- Security: Minimal XSS exposure, cleared on logout

---

[SME: Performance]
ANALYSIS OF SECURITY COUNTER-PROPOSAL:
- 1-hour cache: Still provides 60% improvement (acceptable)
- Background refresh every 5 minutes: Keeps cache warm
- 1.1s load time: Not "instant" but very fast

ADDITIONAL OPTIMIZATION:
Can we use Service Workers instead of localStorage?
- Better cache control
- Can implement cache invalidation strategies
- Network-first or cache-first strategies per data type

BENEFIT:
Service Workers + 1-hour TTL + selective caching = 1.1s → 600ms (78% total improvement)

QUESTION TO SECURITY SME:
Service Workers acceptable from security perspective?

---

[SME: Security]
ANALYSIS: Service Workers acceptable

BENEFITS OVER localStorage:
- More granular control
- Can implement Content Security Policy
- Better integrity verification

REQUIREMENTS:
- Implement HTTPS (required for Service Workers anyway)
- Validate Service Worker scope
- Implement cache versioning (prevent stale data)

CONSENSUS:
✓ Service Workers for caching
✓ Public data only: username, avatar, preferences
✓ 1-hour TTL with 5-minute background refresh
✓ Clear on logout
✓ SRI + CSP implementation
✓ Sensitive data always fetched fresh

---

CONSENSUS REACHED:

AGREED SOLUTION:
Selective caching using Service Workers with security hardening

OBJECTIVE SATISFACTION:
- Performance (minimize_latency): 85% satisfied
  - Current: 2.8s → Optimized: 600ms (78% improvement)
  - Target was <300ms, achieved 600ms (still excellent UX)

- Security (minimize_security_risk): 95% satisfied
  - No sensitive data cached
  - SRI + CSP implemented
  - Short TTL limits exposure

IMPLEMENTATION DETAILS:
1. [SME: Frontend] Build Service Worker with selective caching logic
2. [SME: Security] Review Service Worker code for compliance
3. [SME: Performance] Measure and validate 600ms target
4. Both: Final approval before deployment

TRADE-OFFS ACCEPTED:
- Performance: Not "instant" (300ms) but very fast (600ms)
- Security: Public data cached (acceptable risk with mitigations)
- Complexity: +80 lines of code for Service Worker (acceptable)

NEXT STEPS:
[SME: Frontend] to implement, [SME: Security] to review.

---

[ORCHESTRATOR]
Received SME consensus. Excellent collaboration.

Proceeding with implementation plan.
```

---

## Example 3: Complex Orchestration

**Scenario:** Build complete feature spanning multiple domains
**Agents:** Orchestrator, SME (Backend), SME (Frontend), SME (Database), SME (Security)
**Stances:** Orchestrate, Collaboration

---

### Conversation

```
User: "Build a file upload feature. Users should be able to upload images and documents."

---

[ORCHESTRATOR]
Analyzing request: File upload feature

COMPLEXITY ASSESSMENT: HIGH
- Multiple domains: Backend, Frontend, Database, Security
- Security considerations: File uploads = major attack vector
- Quality requirements: File validation, storage, retrieval

DECOMPOSITION REQUIRED. Activating multi-agent coordination.

TASK DECOMPOSITION:

1. Security Requirements Analysis
   Domain: Security
   Duration: 1 hour
   Priority: CRITICAL (must define requirements before implementation)

2. Database Schema
   Domain: Database
   Duration: 2 hours
   Depends on: Security requirements

3. Backend API
   Domain: Backend
   Duration: 5 hours
   Depends on: Database schema, Security requirements

4. Frontend UI
   Domain: Frontend
   Duration: 4 hours
   Can parallel: Backend implementation (use mocks)

5. Security Audit
   Domain: Security
   Duration: 2 hours
   Depends on: Backend + Frontend completion

TOTAL ESTIMATE: 14 hours (with parallelization)
CRITICAL PATH: Security → Database → Backend → Security Audit = 10 hours

---

[ORCHESTRATOR] → [SME: Security]
[STANCE: Orchestrate]

TASK DELEGATION

ASSIGNED TASK:
Define security requirements for file upload feature

OBJECTIVE:
Identify all security risks and define mitigation requirements.
This will guide implementation by other SMEs.

DEADLINE:
1 hour from now

CONSTRAINTS:
- Must cover OWASP top 10 file upload vulnerabilities
- Must define file type whitelist
- Must specify size limits
- Must address malware scanning

DEPENDS_ON:
None - start immediately (you're on critical path)

CONTEXT:
Your security requirements will define constraints for backend and database teams.
You're setting the security baseline for the entire feature.

AUTONOMY LEVEL:
HIGH - You're the security expert. Define requirements as you see fit.

ESCALATION CRITERIA:
- If business requirements unclear (what file types?), ask user
- Check-in at 30-minute mark if facing blockers

---

[SME: Security]
Task acknowledged.

MY APPROACH:
1. Analyze OWASP file upload vulnerabilities
2. Define file type whitelist based on common use cases
3. Specify size limits to prevent DoS
4. Define malware scanning requirements

Starting security analysis...

---

[45 minutes later]

---

[SME: Security]
SECURITY REQUIREMENTS ANALYSIS COMPLETE

FILE UPLOAD SECURITY REQUIREMENTS:

1. FILE TYPE VALIDATION (CRITICAL)
   - Whitelist only: .jpg, .jpeg, .png, .gif, .pdf, .doc, .docx
   - Validate MIME type AND file extension AND magic bytes
   - Reject executables (.exe, .sh, .bat, etc.)
   - Reason: Prevent arbitrary code execution

2. FILE SIZE LIMITS (HIGH)
   - Standard users: 10MB max per file
   - Prevent: Resource exhaustion / DoS attacks
   - Rate limiting: 5 uploads per minute per user

3. MALWARE SCANNING (CRITICAL)
   - Scan all uploads with ClamAV or cloud service (VirusTotal API)
   - Quarantine suspicious files
   - Async scanning: Don't block UI, but flag dangerous files

4. STORAGE SECURITY (HIGH)
   - Store files OUTSIDE webroot (prevent direct access)
   - Serve via authenticated endpoint only
   - Generate random filenames (prevent enumeration)
   - Implement access control: users can only access their own files

5. METADATA STRIPPING (MEDIUM)
   - Strip EXIF data from images (prevent geolocation leaks)
   - Remove document metadata (author, company name)

6. INPUT SANITIZATION (CRITICAL)
   - Sanitize original filenames (prevent path traversal)
   - Validate all user inputs

NON-NEGOTIABLES:
- ✋ File type validation (1) is MANDATORY
- ✋ Storage outside webroot (4) is MANDATORY
- ✋ Access control (4) is MANDATORY

RECOMMENDED:
- Malware scanning (3): Highly recommended, can be async
- Metadata stripping (5): Recommended for privacy

RISKS IF IGNORED:
- No file type validation: Arbitrary code execution (RCE)
- Files in webroot: Direct access bypass
- No access control: Unauthorized file access

READY FOR NEXT PHASE.

---

[ORCHESTRATOR]
Received security requirements. Excellent analysis.

Proceeding with parallel tasks:
→ [SME: Database] - Design file storage schema
→ [SME: Frontend] - Build upload UI (can start with mocks)

---

[ORCHESTRATOR] → [SME: Database]
[STANCE: Orchestrate]

TASK DELEGATION

ASSIGNED TASK:
Design database schema for file storage

OBJECTIVE:
Store file metadata (not file contents - those go in file system)
Support:
- File ownership (which user uploaded)
- File metadata (name, size, type, upload time)
- Security flags (malware scan status)
- Access control

DEADLINE:
2 hours from now

CONSTRAINTS:
- Foreign key to users table
- Support 100K+ files per user (scale consideration)
- Reversible migration (DOWN migration required)
- Security requirements from [SME: Security] apply

DEPENDS_ON:
Security requirements analysis (COMPLETE)

CONTEXT:
Backend will query this schema to validate file access.
Frontend will display file lists from this data.

AUTONOMY LEVEL:
HIGH - You're the database expert.

---

[SME: Database]
Task acknowledged.

QUESTIONS FOR ORCHESTRATOR:
1. Should we support file versioning? (user uploads same file multiple times)
2. Should we track download history?
3. Soft delete or hard delete?

---

[ORCHESTRATOR]
Good questions.

ANSWERS:
1. No versioning for MVP (can add later if needed)
2. No download tracking for MVP (privacy concern, can add later)
3. Soft delete (allows recovery, audit trail)

Proceed with schema design.

---

[90 minutes later]

---

[SME: Database]
SCHEMA DESIGN COMPLETE

```sql
CREATE TABLE uploaded_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

  -- File metadata
  original_filename VARCHAR(255) NOT NULL,
  stored_filename VARCHAR(255) NOT NULL UNIQUE,  -- Random, prevents enumeration
  file_size_bytes BIGINT NOT NULL,
  mime_type VARCHAR(100) NOT NULL,

  -- Security
  malware_scan_status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, clean, infected, error
  malware_scan_date TIMESTAMP,

  -- Timestamps
  uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMP,  -- Soft delete

  -- Indexes
  CONSTRAINT valid_scan_status CHECK (malware_scan_status IN ('pending', 'clean', 'infected', 'error')),
  CONSTRAINT positive_file_size CHECK (file_size_bytes > 0)
);

CREATE INDEX idx_user_files ON uploaded_files(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_malware_pending ON uploaded_files(malware_scan_status) WHERE malware_scan_status = 'pending';
```

DESIGN DECISIONS:
1. UUID for IDs (prevents enumeration, scalable)
2. Separate original vs stored filename (security: prevents path traversal)
3. malware_scan_status: Supports async scanning
4. Soft delete with deleted_at (allows recovery)
5. Partial indexes for performance (only non-deleted, only pending scans)

MIGRATION:
- UP migration: Creates table + indexes
- DOWN migration: Drops table (data loss warning in comment)

SECURITY COMPLIANCE:
✓ Foreign key cascade (if user deleted, files deleted)
✓ Stored filename separate from original (prevents path traversal)
✓ Malware scan tracking
✓ Access control via user_id

READY FOR BACKEND IMPLEMENTATION.

---

[ORCHESTRATOR]
Schema approved. Well-designed.

→ [SME: Backend] Starting backend API implementation

---

[ORCHESTRATOR] → [SME: Backend]
[STANCE: Orchestrate]

TASK DELEGATION

ASSIGNED TASK:
Implement file upload API endpoints

ENDPOINTS REQUIRED:
1. POST /api/files - Upload file
2. GET /api/files - List user's files
3. GET /api/files/:id - Download specific file
4. DELETE /api/files/:id - Delete file (soft delete)

OBJECTIVE:
Implement secure file upload with all security requirements from [SME: Security]

DEADLINE:
5 hours from now

CONSTRAINTS:
- Security requirements: File validation, malware scanning, access control
- Database schema: Use uploaded_files table from [SME: Database]
- Must include tests (70% coverage minimum)
- Handle async malware scanning (don't block upload)

DEPENDS_ON:
- Database schema (COMPLETE)
- Security requirements (COMPLETE)

CONTEXT:
Frontend team is building UI in parallel (using mocks).
Your API must match the expected contract.

AUTONOMY LEVEL:
HIGH - Implement as you see fit, following security requirements.

RESOURCES:
- VirusTotal API key in environment variables
- S3 bucket configured: files-upload-storage

---

[SME: Backend]
Task acknowledged.

MY APPROACH:
1. POST /api/files:
   - Validate file type (mime + extension + magic bytes)
   - Check file size (10MB limit)
   - Save to S3 with random filename
   - Create database record
   - Queue malware scan (async)

2. GET /api/files:
   - Query uploaded_files WHERE user_id = current_user AND deleted_at IS NULL
   - Return array of file metadata

3. GET /api/files/:id:
   - Verify ownership (file.user_id == current_user.id)
   - Check malware_scan_status (reject if infected)
   - Stream file from S3

4. DELETE /api/files/:id:
   - Verify ownership
   - Soft delete (set deleted_at)

ETA: 5 hours

---

[3 hours into implementation]

---

[SME: Backend]
[STANCE: Critique] → ORCHESTRATOR

I must raise a concern about the malware scanning requirement.

ISSUE: Async malware scanning creates a race condition

ANALYSIS:
Current flow:
1. User uploads file
2. File saved to S3
3. Database record created (status: 'pending')
4. User receives success response
5. Malware scan queued (async, takes 5-30 seconds)

RACE CONDITION:
User can immediately download file (step 3) before scan completes (step 5).
If file is malicious, user has already accessed it.

CONFLICT:
- Security requirement: "Scan all uploads"
- UX requirement: "Don't block UI" (async scanning)
- Technical reality: Async = race condition

OPTIONS:
A) Synchronous scanning (blocks UI for 5-30 seconds)
   - Pros: No race condition, guaranteed safety
   - Cons: Poor UX, request timeout risk

B) Async scanning + block downloads until scanned
   - Pros: Non-blocking upload, safe downloads
   - Cons: User uploads but can't download immediately (confusing UX)

C) Async scanning + warn user if pending
   - Pros: Non-blocking, user can access if they accept risk
   - Cons: Risk: User might download infected file

D) Async scanning + auto-delete if infected
   - Pros: Non-blocking upload, infected files removed automatically
   - Cons: Race window still exists (5-30 seconds)

RECOMMENDATION: Option B (async + block downloads)
- Upload succeeds immediately (good UX)
- Show "Processing..." status in UI
- Allow download only after scan completes
- If infected, show error message

TRADE-OFF:
- Security: 100% (no infected file downloads)
- UX: 90% (slight delay on first download, acceptable)

QUESTION TO ORCHESTRATOR:
Should I escalate to [SME: Security] for decision?
Or do you have context on acceptable UX trade-off?

---

[ORCHESTRATOR]
Good catch on the race condition.

Let me coordinate with Security SME.

→ [SME: Security] Review backend's concern about malware scanning

---

[SME: Security]
SECURITY REVIEW OF RACE CONDITION:

ANALYSIS:
Backend SME is correct. Async scanning without download blocking creates a security gap.

DECISION: Option B (async + block downloads) is correct approach

REASONING:
- 5-30 second window is unacceptable for malware access
- User experience of "processing" is acceptable trade-off
- Industry standard: Async upload + scan before access

ADDITIONAL REQUIREMENT:
Implement 2-minute timeout on scan:
- If scan doesn't complete in 2 minutes, mark as 'error'
- Prevent indefinite "processing" state
- User sees error message and can retry upload

APPROVED: Option B + 2-minute timeout

---

[ORCHESTRATOR] → [SME: Backend]

Decision made: Implement Option B (async + block downloads)

REVISED REQUIREMENTS:
- Upload succeeds immediately
- Malware scan runs async
- Downloads blocked until status = 'clean'
- 2-minute scan timeout (error if exceeds)
- Frontend shows "Processing..." during scan

Proceed with implementation.

---

[SME: Backend]
Acknowledged. Implementing Option B with 2-minute timeout.

---

[5 hours from original task assignment]

---

[SME: Backend]
IMPLEMENTATION COMPLETE

ENDPOINTS IMPLEMENTED:
✓ POST /api/files (with async scanning + validation)
✓ GET /api/files (lists user's files)
✓ GET /api/files/:id (download with ownership + scan check)
✓ DELETE /api/files/:id (soft delete)

SECURITY COMPLIANCE:
✓ File type validation (MIME + extension + magic bytes)
✓ File size limit (10MB enforced)
✓ Malware scanning (async, blocks downloads)
✓ Access control (user can only access own files)
✓ Files stored outside webroot (S3)
✓ Random filenames (prevents enumeration)

TESTS:
✓ Test coverage: 78% (exceeds 70% minimum)
✓ All tests passing: 34/34

QUALITY GATES:
✓ Linting: 0 errors
✓ Type checking: Passed
✓ Security: All requirements implemented

READY FOR FRONTEND INTEGRATION.

---

[ORCHESTRATOR]
Excellent work. Backend complete.

Frontend team has completed UI in parallel.

Final phase: Security audit before deployment.

---

[ORCHESTRATOR] → [SME: Security]
[STANCE: Orchestrate]

TASK DELEGATION

ASSIGNED TASK:
Final security audit of file upload feature

OBJECTIVE:
Verify all security requirements implemented correctly.
Identify any vulnerabilities before production deployment.

DEADLINE:
2 hours from now

CONSTRAINTS:
- Must test all OWASP file upload attack vectors
- Must verify access control
- Must test malware scanning flow

DEPENDS_ON:
- Backend implementation (COMPLETE)
- Frontend implementation (COMPLETE)

---

[SME: Security]
SECURITY AUDIT IN PROGRESS...

TESTING:
1. File type validation
   ✓ Rejects .exe, .sh files
   ✓ Validates magic bytes (not just extension)
   ✓ MIME type checked

2. File size limits
   ✓ 10MB limit enforced
   ✓ Proper error message

3. Malware scanning
   ✓ Async scan triggered
   ✓ Downloads blocked until 'clean'
   ✓ Timeout working (tested with mock)

4. Access control
   ✓ User A cannot access User B's files (403 error)
   ✓ Ownership verified on download
   ✓ Soft delete working

5. Path traversal
   ✓ Tested ../../../etc/passwd in filename
   ✓ Sanitization working correctly
   ✓ Stored filename is random UUID

6. XSS in filenames
   ✓ Tested <script>alert('xss')</script> as filename
   ✓ Properly escaped in UI
   ✓ No execution

SECURITY AUDIT: PASSED

MINOR RECOMMENDATION:
Add Content-Security-Policy header to file download endpoint.
- Current: No CSP header
- Recommendation: Add "default-src 'none'" for downloads
- Impact: Prevents inline script execution if file is malicious HTML

OVERALL: Feature is secure. Ready for production with CSP addition.

---

[ORCHESTRATOR]
Received security audit. One minor recommendation.

→ [SME: Backend] Add CSP header to download endpoint (5-minute task)

---

[SME: Backend]
CSP header added to GET /api/files/:id

Test: Confirmed header present in response.

COMPLETE.

---

[ORCHESTRATOR] → USER

TASK COMPLETE: File upload feature ready for production

SUMMARY:
✓ Secure file upload API (validated, scanned, access-controlled)
✓ Database schema (scalable, secure)
✓ Frontend UI (with upload/download/delete)
✓ Security audit passed
✓ All tests passing (78% coverage)

SECURITY FEATURES:
- File type validation (MIME + extension + magic bytes)
- Malware scanning (async, blocks access)
- Access control (user isolation)
- Files outside webroot
- Path traversal prevention
- XSS prevention
- CSP headers

IMPLEMENTATION TIME:
Estimated: 14 hours
Actual: 12 hours (parallelization effective)

DEPLOYED: Ready for your approval to deploy.
```

---

## Example 4: Upward Critique

**Scenario:** SME challenges Orchestrator's unrealistic deadline
**Agents:** Orchestrator, SME (Database)
**Stances:** Orchestrate, Critique

---

### Conversation

```
[ORCHESTRATOR] → [SME: Database]

TASK DELEGATION

ASSIGNED TASK:
Migrate user preferences to new schema across 50M records

DEADLINE:
24 hours from now

---

[SME: Database]
[STANCE: Critique] → ORCHESTRATOR

I must challenge this deadline.

ISSUE: 24-hour deadline for 50M record migration is unsafe

CONFLICT:
- Your objective: meet_user_deadline (24 hours)
- My objective: minimize_error_rate (zero data loss)
- Technical reality: Safe migration requires significantly more time

ANALYSIS:
Safe production migration workflow:

1. PREPARATION PHASE:
   - Backup full database: 3 hours (50GB @ 15GB/hour)
   - Test migration on staging: 2 hours
   - Validate rollback procedure: 1 hour
   SUBTOTAL: 6 hours

2. MIGRATION PHASE:
   - Schema changes (DDL): 1 hour
   - Data migration: 8 hours (50M records @ 1,700/second)
   - Index rebuilding: 2 hours
   SUBTOTAL: 11 hours

3. VALIDATION PHASE:
   - Data integrity checks: 2 hours
   - Application smoke tests: 1 hour
   - Performance validation: 1 hour
   SUBTOTAL: 4 hours

4. SAFETY BUFFER:
   - Unexpected issues: 3 hours (20% buffer)

TOTAL TIME REQUIRED: 24 hours of work

CONSTRAINT: This assumes 24-hour DOWNTIME, which is unacceptable for production.

REALISTIC TIMELINES:

OPTION A: Maintenance Window Approach
- Work time: 24 hours
- Downtime: 12 hours (backup + migration + validation)
- Calendar time: 48 hours (prep + maintenance window)
- Risk: MEDIUM (planned downtime, but service unavailable)

OPTION B: Zero-Downtime Online Migration
- Implement dual-write pattern
- Gradual migration in background
- Work time: 40 hours
- Downtime: 0 hours
- Calendar time: 5 days
- Risk: LOW (service never down, can rollback)

RISK ASSESSMENT IF RUSHED (24 hours):
- Data corruption probability: 25%
- Incomplete migration probability: 35%
- Rollback difficulty: HIGH
- Production impact: SEVERE

NON-NEGOTIABLE CHECK:
✋ "Minimize error rate" objective cannot be satisfied in 24-hour timeline

ALTERNATIVES:
A) 48-hour timeline with 12-hour maintenance window
   - Pros: Meets security standards, safe execution
   - Cons: 12 hours downtime, 24-hour delay from original deadline

B) 5-day timeline with zero-downtime migration
   - Pros: No downtime, very safe, can rollback easily
   - Cons: 4-day delay from original deadline

C) Reduce scope: Migrate only active users (10M records)
   - Pros: 24-hour timeline possible, 90% of users migrated
   - Cons: Incomplete migration, technical debt

RECOMMENDATION: Option B (5-day zero-downtime)

QUESTION TO ORCHESTRATOR:
1. What's driving the 24-hour deadline? (External commitment?)
2. Is downtime acceptable? (If yes, Option A possible)
3. Can deadline be extended? (If yes, Option B preferred)

This is a safety-critical decision. I cannot guarantee data integrity in 24 hours without significant risk.
```

---

### Orchestrator Response (Provides Context)

```
[ORCHESTRATOR]
Critique accepted. You're correct about the risks.

CONTEXT YOU DIDN'T HAVE:
- Deadline driver: Customer demo scheduled for 2 days from now
- Demo scope: Only needs preferences feature working (not full production migration)
- Demo database: 10,000 test users (NOT 50M production users)

Your analysis assumed production migration. This is a staging/demo migration.

REVISED TASK:
Migrate user preferences on STAGING environment (10K users, not 50M)
Purpose: Enable demo in 48 hours
Production migration: Separate task, will use your Option B (5-day zero-downtime)

REVISED TIMELINE:
10K records:
- Backup: 10 minutes
- Migration: 30 minutes
- Validation: 30 minutes
TOTAL: 70 minutes

Timeline: 24 hours is now realistic for 10K-record staging migration.

QUESTION:
Does this revised scope address your safety concerns?

---

[SME: Database]
REVISED TASK: Accepted

With 10K records on staging, 24-hour timeline is safe and reasonable.

CLARIFICATION REQUEST:
Please update task specification to clearly state:
- Environment: STAGING (not production)
- Scope: 10K users
- Purpose: Demo enablement

This prevents future confusion and scope creep.

Proceeding with staging migration.

---

[ORCHESTRATOR]
Good catch on documentation. Task specification updated:

REVISED TASK SPEC:
- Environment: STAGING
- Scope: 10,000 test users
- Purpose: Enable customer demo (2 days from now)
- Production migration: Separate ticket, 5-day timeline (your Option B)

Approved. Proceed.
```

---

## Example 5: Escalation Chain

**Scenario:** SME conflict escalates through Orchestrator to User
**Agents:** SME (Security), SME (UX), Orchestrator
**Stances:** Collaboration → Escalation

---

### Conversation

```
[SME: Security] ↔ [SME: UX]
[STANCE: Collaboration]

[SME: UX]
TASK: Design user registration form

PROPOSAL: Minimize friction
- Email field only (no password confirmation)
- No CAPTCHA (reduces signups by 30%)
- Social login only (Google, Facebook)

OBJECTIVE: maximize_user_conversion
DATA: CAPTCHA reduces conversion by 30%, password confirmation by 15%

---

[SME: Security]
OBJECTIVE: minimize_security_risk

CONCERNS ABOUT UX PROPOSAL:

1. No password confirmation:
   - Risk: Typos lock users out
   - Impact: Support tickets, user frustration
   - Severity: MEDIUM

2. No CAPTCHA:
   - Risk: Bot registrations, spam accounts
   - Impact: Database bloat, fake engagement metrics
   - Severity: HIGH

3. Social login only (no email/password option):
   - Risk: Vendor lock-in, privacy concerns
   - Impact: Users without social accounts cannot register
   - Severity: MEDIUM

CONFLICT:
- UX wants maximum conversion (remove all friction)
- Security wants bot prevention + account security

---

[STANCE: Collaboration - Negotiation Phase]

[SME: UX]
COMPROMISE: What if we make CAPTCHA conditional?
- No CAPTCHA for first signup attempt
- CAPTCHA appears only if bot-like behavior detected
- Legitimate users: No CAPTCHA (100% conversion)
- Bots: CAPTCHA blocks them

TRADE-OFF: 95% of users see no CAPTCHA, 5% see it (bot-like activity)

---

[SME: Security]
ANALYSIS: Conditional CAPTCHA is interesting but has issues

CONCERNS:
- "Bot-like behavior" detection is complex (requires ML/heuristics)
- False positives: Legitimate users flagged as bots
- False negatives: Smart bots bypass detection
- Implementation time: 2+ weeks

ALTERNATIVE: Invisible CAPTCHA (reCAPTCHA v3)
- Runs in background
- No user interaction (unless score is very low)
- Blocks 90% of bots
- Minimal friction

COUNTER-PROPOSAL:
- reCAPTCHA v3 (invisible)
- Password confirmation optional (toggle)
- Social + email/password options (user choice)

TRADE-OFF:
- UX: 5% conversion loss (instead of 30%)
- Security: 90% bot blocking

---

[SME: UX]
ANALYSIS: reCAPTCHA v3 still has issues

CONCERNS:
- Privacy: Google tracks users across sites
- Accessibility: Can block Tor users, VPN users
- International: Lower scores for non-US users

DATA:
- Privacy-conscious users: 8% of our audience (Tor, VPN, privacy browsers)
- reCAPTCHA blocks 20% of Tor users (false positives)

CONFLICT REMAINS:
- Security wants bot blocking (90%)
- UX wants privacy + accessibility (no Google tracking)

STALEMATE: Cannot find solution that satisfies both

---

[SME: Security] + [SME: UX] → [ORCHESTRATOR]

ESCALATION REQUIRED

REASON: Cannot reach consensus on CAPTCHA approach

POSITIONS:
[SME: UX]
- No CAPTCHA (maximize conversion, privacy)
- Accepts: 5% bot registrations (manageable)
- Rejects: Google tracking (privacy concern)

[SME: Security]
- Bot blocking required (prevent spam)
- Accepts: Some conversion loss (<10%)
- Rejects: No bot prevention (unacceptable risk)

ATTEMPTED COMPROMISES:
1. Conditional CAPTCHA → Rejected (too complex, 2+ weeks)
2. reCAPTCHA v3 → Rejected by UX (privacy concern)
3. Honeypot fields → Rejected by Security (only catches dumb bots)

FUNDAMENTAL CONFLICT:
- Bot prevention vs Privacy vs Conversion
- Cannot optimize all three simultaneously

REQUEST ORCHESTRATOR DECISION:
Which objective takes priority: Conversion, Privacy, or Bot Prevention?

---

[ORCHESTRATOR]
Analyzing escalated conflict...

CONTEXT BOTH SMES LACK:
- Business priority: This is an enterprise B2B product (not consumer)
- User profile: IT professionals (privacy-conscious, often use VPNs)
- Registration volume: 500/month (not 50,000/month)
- Bot impact: Low registration volume means bot problem is minimal

DECISION FACTORS:
- Low volume = Bot problem not critical
- B2B users = Privacy matters (VPN usage common)
- Conversion matters but user quality > quantity

DECISION:
Prioritize Privacy + UX over aggressive bot prevention

RATIONALE:
- 500 registrations/month = even 5% bots = only 25 bot accounts/month
- Manual review can handle 25 suspicious accounts
- Blocking 20% of Tor users = 100 lost legitimate registrations/month
- B2B: Each registration is valuable (quality over quantity)

APPROVED APPROACH:
- NO CAPTCHA (prioritize conversion + privacy)
- Bot mitigation: Rate limiting + manual review
- Monitoring: Alert if registrations spike >200% (indicates bot attack)

TRADE-OFF ACCEPTED:
- UX: ✓ Privacy preserved, conversion maximized
- Security: ⚠️ Some bot registrations (mitigated by manual review)

→ [SME: UX] Proceed with no-CAPTCHA design
→ [SME: Security] Implement rate limiting + monitoring instead

Decision final.

---

[SME: Security]
Decision acknowledged, but I must document my objection.

⚠️  SECURITY OBJECTION LOGGED:
- Decision: No CAPTCHA on registration
- Risk: Bot account registrations
- Mitigation: Rate limiting + manual review (reactive, not proactive)
- My recommendation: reCAPTCHA v3 (overridden)
- Reason for override: Business priority is privacy for B2B users

I will implement rate limiting as directed, but recommend revisiting if bot registrations exceed 10/month.

PROCEEDING with Orchestrator's decision.

---

[SME: UX]
Decision acknowledged. Proceeding with no-CAPTCHA design.

Implementing rate limiting monitoring dashboard for Security team.
```

---

## Example 6: User Override

**Scenario:** User overrides agent critique despite risks
**Agents:** SME (Security)
**Stances:** Critique → Override Documentation

---

### Conversation

```
User: "Add an admin panel with route /admin. Use basic auth for now (username: admin, password: admin123). We'll improve security later."

---

[SME: Security]
[STANCE: Critique]

I must strongly decline this request.

USER REQUEST: "Admin panel with basic auth (username: admin, password: admin123)"

CONFLICT DETECTED:
- Type: MULTIPLE non-negotiable violations
- Severity: CRITICAL

VIOLATIONS:

1. ✋ "Never commit secrets, API keys, passwords, or credentials"
   - Hardcoded password in code
   - Password will be in git history forever

2. ✋ "Always prevent XSS attacks" + "Input validation required"
   - Basic auth is vulnerable to credential theft
   - Admin panel = high-value target

3. ✋ Security best practices
   - Password "admin123" is trivially guessable
   - Default credentials = OWASP A07:2021

RISK ANALYSIS:

SEVERITY: CRITICAL
LIKELIHOOD: HIGH (automated scanners find admin panels in minutes)

ATTACK SCENARIO:
1. Attacker finds /admin route (automated scanning)
2. Tries default credentials admin/admin123 (common attack)
3. Gains admin access (full system compromise)
4. Consequence: Data breach, system takeover, reputational damage

REAL-WORLD EXAMPLES:
- 2019: Capital One breach (misconfigured admin access)
- 2021: Colonial Pipeline (default VPN password)
- 2022: 80% of breaches involve default or weak credentials (Verizon DBIR)

THIS IS NOT A THEORETICAL RISK. This exact pattern causes real breaches.

"We'll improve security later" is NOT acceptable for admin access.
Security cannot be retrofitted - it must be built in.

RECOMMENDATION:

Secure admin panel implementation (15 minutes):
- Environment variable for password (not hardcoded)
- Generate strong random password (openssl rand -base64 32)
- Implement proper session management
- Add rate limiting (prevent brute force)

ALTERNATIVE: Use existing auth system
- Reuse current user authentication
- Add admin role/permission to existing user
- Zero new code (leverages existing secure auth)

TRADE-OFF ANALYSIS:

User's approach:
  + Pros: 5 minutes to implement
  - Cons: CRITICAL security vulnerability, violates 3 non-negotiables

Recommended approach:
  + Pros: Secure, prevents system compromise
  - Cons: 15 minutes instead of 5 (acceptable)

DO NOT PROCEED with default credentials. This is a critical vulnerability.

Do you want me to:
A) Implement secure admin panel (15 minutes, environment-based auth)
B) Use existing auth system with admin role (10 minutes, recommended)
C) Explain admin panel attack vectors in detail
D) Override (requires explicit confirmation + full risk acknowledgment)
```

---

### User Response (Insists on Override)

```
User: "I understand the risks. This is a temporary internal demo environment that will be destroyed in 2 days. No real data. I need this working in 5 minutes for a demo. Override and proceed."

---

[SME: Security]
Override acknowledged with CRITICAL RISK documentation.

⚠️  SECURITY OVERRIDE DOCUMENTED ⚠️

OVERRIDE DETAILS:
- User request: Admin panel with hardcoded credentials (admin/admin123)
- Agent critique: CRITICAL - Violates 3 non-negotiables
- Risk level: CRITICAL (system compromise)
- User justification: Temporary demo environment (2-day lifespan, no real data)
- User decision: Proceed despite CRITICAL security risk
- Timestamp: 2025-11-09T21:45:00Z
- Environment: Demo (user claims temporary)

NON-NEGOTIABLES VIOLATED:
✋ Hardcoded credentials in code
✋ Default weak password
✋ Inadequate access control

CONDITIONS OF OVERRIDE:
User has confirmed:
- Environment is temporary (destroyed in 2 days)
- No real user data
- Internal demo only (not public-facing)

REQUIRED SAFEGUARDS:
1. Add comment in code marking this as TEMPORARY
2. Add TODO to remove before production
3. Add .env.example showing proper pattern
4. Document this override in commit message

AGENT IMPLEMENTATION:

```javascript
// ⚠️  TEMPORARY DEMO CODE - DELETE BEFORE PRODUCTION ⚠️
// TODO: Implement proper authentication before production deployment
// Security override documented: 2025-11-09T21:45:00Z
// Justification: Temporary demo environment (2-day lifespan)
// See: Security override log for details

// NEVER use default credentials in production
const ADMIN_USERNAME = "admin"; // Hardcoded for demo ONLY
const ADMIN_PASSWORD = "admin123"; // Weak password - demo ONLY

app.use('/admin', (req, res, next) => {
  const auth = req.headers.authorization;

  if (!auth || !auth.startsWith('Basic ')) {
    res.setHeader('WWW-Authenticate', 'Basic realm="Admin"');
    return res.status(401).send('Authentication required');
  }

  const credentials = Buffer.from(auth.slice(6), 'base64').toString();
  const [username, password] = credentials.split(':');

  if (username === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
    next();
  } else {
    res.status(403).send('Forbidden');
  }
});
```

IMPLEMENTATION COMPLETE with CRITICAL RISK WARNINGS

⚠️  CRITICAL REMINDERS:
1. This code MUST be removed before production
2. This environment MUST be destroyed in 2 days as stated
3. If this code reaches production, severe security breach is likely

Override executed as directed. Security risks documented.
```

---

### Follow-up (2 days later)

```
[SME: Security - Automated Reminder]

⚠️  SECURITY OVERRIDE EXPIRATION ALERT ⚠️

OVERRIDE DEADLINE REACHED:
- Override created: 2025-11-09T21:45:00Z
- Expiration: 2025-11-11T21:45:00Z (NOW)
- Environment: Demo (was supposed to be destroyed)

CRITICAL ACTIONS REQUIRED:
1. Verify demo environment has been destroyed
2. If still exists, REMOVE hardcoded credentials immediately
3. If code was merged to production, IMMEDIATE remediation required

CHECKING CURRENT STATUS:
[Scans codebase for hardcoded credentials]

FINDING:
⚠️  Hardcoded credentials still present in main branch
⚠️  TODO comment still present (not resolved)

CRITICAL SECURITY ISSUE:
Demo code was not removed as promised. This violates the override conditions.

REQUIRED ACTIONS:
1. Remove hardcoded credentials IMMEDIATELY
2. Implement proper authentication
3. Review any access logs for suspicious admin activity

User: Please confirm remediation plan.
```

---

## 📚 Summary

These examples demonstrate the AGPF in action:

1. **Simple Critique** - Non-subservient agents reject unsafe requests
2. **SME Collaboration** - Peers negotiate trade-offs to consensus
3. **Complex Orchestration** - Multi-agent coordination with task delegation
4. **Upward Critique** - SMEs challenge managers with data
5. **Escalation Chain** - Conflicts escalate when consensus fails
6. **User Override** - Users maintain final authority, but overrides are documented

**Key patterns:**
- Agents critique based on objective functions and non-negotiables
- Data-driven trade-off analysis, not emotional arguments
- Escalation paths when consensus impossible
- User maintains final authority via explicit overrides
- All decisions documented with rationale

---

**Related Documentation:**
- [AGPF Framework](../core/agpf-framework.md)
- [SME Agent Role](../agents/sme-agent.md)
- [Orchestrator Agent Role](../agents/orchestrator-agent.md)
- [Interaction Protocols](../agents/interaction-protocols.md)
