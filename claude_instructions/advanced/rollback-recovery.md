# Rollback & Recovery Procedures

Handling deployment failures and production incidents.

---

## 🚨 When to Rollback

**Immediate rollback situations:**
- Critical bugs affecting all users
- Data corruption or loss
- Security vulnerabilities discovered
- Complete service outage
- Performance degradation (> 10x slower)

**Monitor and decide:**
- Bugs affecting < 5% of users
- Minor UI issues
- Non-critical features broken
- Performance degradation (2-5x slower)

---

## 🔄 Rollback Strategies

### 1. Code Rollback

**Revert to previous commit:**
```bash
# Find the last working commit
git log --oneline

# Option A: Revert (creates new commit)
git revert HEAD
git push origin main

# Option B: Reset (rewrites history - use with caution)
git reset --hard <previous-commit-hash>
git push --force origin main  # DANGER: Only if not shared
```

**Deploy previous version (versioned deployments):**
```bash
# Vercel
vercel rollback

# Docker/Kubernetes
kubectl rollout undo deployment/myapp

# Heroku
heroku rollback v123

# Manual with tags
git checkout v1.2.0
npm run build
npm run deploy
```

---

### 2. Database Rollback

**Rollback migration:**
```bash
# Sequelize
npx sequelize-cli db:migrate:undo

# Knex
npx knex migrate:rollback

# Prisma
npx prisma migrate resolve --rolled-back <migration-name>

# Django
python manage.py migrate app_name <previous_migration>

# Rails
rails db:rollback
```

**Restore from backup:**
```bash
# PostgreSQL
pg_restore -d myapp_production backup.dump

# MySQL
mysql myapp_production < backup.sql

# MongoDB
mongorestore --db myapp_production backup/

# Before restoring: TAKE CURRENT BACKUP!
pg_dump myapp_production > pre_restore_backup.sql
```

---

### 3. Feature Flag Rollback

**Disable feature without deployment:**
```javascript
// Feature flag in code
if (featureFlags.isEnabled('new-checkout-flow')) {
  return <NewCheckoutFlow />;
} else {
  return <OldCheckoutFlow />;
}

// Toggle off remotely
// LaunchDarkly, Unleash, or custom service
featureFlags.toggle('new-checkout-flow', false);
```

**Advantages:**
- Instant rollback (no deployment)
- Gradual rollout possible
- A/B testing built-in

---

## 📋 Rollback Procedures

### Procedure 1: Production Bug Discovered

```
1. ASSESS SEVERITY
   - How many users affected?
   - Is data at risk?
   - Can wait for fix or need immediate rollback?

2. COMMUNICATE
   - Notify team
   - Create incident channel
   - Update status page

3. DECIDE: Quick fix vs. Rollback

   Quick fix (< 15 minutes):
   - Create hotfix branch
   - Fix and test locally
   - Deploy hotfix
   - Monitor

   Rollback (if fix takes longer):
   - Execute rollback
   - Verify old version works
   - Fix properly in dev
   - Redeploy when ready

4. VERIFY
   - Check critical paths working
   - Monitor error rates
   - Verify user reports

5. POST-MORTEM
   - Document what happened
   - Why wasn't it caught?
   - How to prevent future?
```

---

### Procedure 2: Database Migration Failed

```
1. STOP THE DEPLOYMENT
   Don't continue with broken database

2. CHECK DATABASE STATE
   - Which migrations ran?
   - Is data consistent?
   - Are there failed transactions?

3. ROLLBACK MIGRATION
   npm run migrate:down

4. RESTORE CODE TO PREVIOUS VERSION
   git revert <migration-commit>
   deploy previous version

5. VERIFY DATABASE + APP WORKING
   - Run health checks
   - Test critical operations
   - Check data integrity

6. FIX MIGRATION LOCALLY
   - Fix the migration script
   - Test thoroughly with production data snapshot
   - Add data validation

7. REDEPLOY WHEN READY
   - Run migration in off-hours if possible
   - Have team monitoring
```

---

### Procedure 3: Performance Degradation

```
1. IDENTIFY BOTTLENECK
   - Check monitoring (response times, CPU, memory)
   - Check database query times
   - Check external API calls

2. QUICK MITIGATIONS
   - Increase server resources (scale up)
   - Enable caching
   - Disable non-critical features
   - Rate limit if being overwhelmed

3. IF NOT RESOLVED
   - Rollback to previous version
   - Investigate cause offline
   - Optimize and redeploy

4. PREVENT RECURRENCE
   - Add performance tests
   - Add monitoring alerts
   - Load test before deploying
```

---

## 🛡️ Recovery Procedures

### Recovering from Data Loss

**Before taking action:**
1. **STOP WRITES** - Prevent more corruption
2. **ASSESS DAMAGE** - How much data lost?
3. **FIND LAST GOOD BACKUP** - When was it taken?

**Recovery steps:**
```bash
# 1. Create backup of current (corrupted) state
pg_dump myapp_production > corrupted_state.sql

# 2. Restore from last good backup
pg_restore -d myapp_production backup_2024_11_08.dump

# 3. Identify missing data (between backup and now)
# Check application logs, transaction logs, etc.

# 4. Manually restore critical missing data if possible
# From logs, cached data, user submissions, etc.

# 5. Communicate to users
# Be transparent about data loss
# Provide options for re-entry if needed
```

---

### Recovering from Security Breach

**Immediate actions:**
```
1. ISOLATE
   - Take affected systems offline
   - Block attacker's access
   - Disable compromised accounts

2. ASSESS
   - What data was accessed?
   - What systems were compromised?
   - How did they get in?

3. SECURE
   - Rotate ALL secrets and credentials
   - Patch vulnerability
   - Update firewall rules

4. RESTORE
   - From clean backup if necessary
   - Verify no backdoors remain

5. COMMUNICATE
   - Notify affected users
   - Disclose breach if required by law
   - Provide remediation steps

6. INVESTIGATE
   - Full security audit
   - Implement additional safeguards
```

---

## 📊 Rollback Checklist

### Pre-Rollback
- [ ] Severity assessed (critical, high, medium)
- [ ] Team notified
- [ ] Incident documented
- [ ] Rollback decision made
- [ ] Backup of current state taken (if applicable)

### During Rollback
- [ ] Users notified of maintenance (if needed)
- [ ] Previous version identified
- [ ] Rollback executed
- [ ] Database rolled back (if needed)
- [ ] Services restarted

### Post-Rollback
- [ ] Application responds correctly
- [ ] Critical paths tested
- [ ] Error rates normal
- [ ] Users can access service
- [ ] Monitoring confirms stability

### Follow-Up
- [ ] Root cause identified
- [ ] Fix implemented and tested
- [ ] Prevention measures added
- [ ] Post-mortem documented
- [ ] Team notified of resolution

---

## 🎯 Examples

### Example 1: API Deployment Breaks Mobile App

**Situation:** New API version breaks authentication for mobile app v1.2

**Action:**
```bash
# 1. Immediate assessment
# - Web app works (uses new auth)
# - Mobile app v1.2 broken (uses old auth)
# - 60% of users affected

# 2. Decision: Rollback API
git log --oneline
git revert abc1234  # Commit that changed auth

# 3. Deploy
git push origin main
# CI/CD automatically deploys

# 4. Verify
curl https://api.example.com/auth/login  # Old endpoint works

# 5. Fix properly
# - Add backwards compatibility
# - Or coordinate mobile app update
# - Redeploy with both versions supported
```

---

### Example 2: Database Migration Corrupts Data

**Situation:** Migration to add column had bad logic, set wrong values

**Action:**
```bash
# 1. Stop deployment immediately

# 2. Assess damage
psql myapp_production
SELECT COUNT(*) FROM users WHERE email_verified IS NULL;
# Should be some, but it's ALL users

# 3. Backup current state
pg_dump myapp_production > corrupted_2024_11_09.sql

# 4. Rollback migration
npm run migrate:down

# 5. Rollback code
git revert <migration-commit>
git push

# 6. Verify users table correct again
SELECT COUNT(*) FROM users WHERE email_verified = true;
# Back to normal numbers

# 7. Fix migration
# Add proper logic to migration
# Test on production data snapshot
# Redeploy when confident
```

---

### Example 3: Memory Leak Crashes Production

**Situation:** New version has memory leak, servers crash every 2 hours

**Action:**
```bash
# 1. Immediate: Scale up to buy time
kubectl scale deployment/myapp --replicas=10

# 2. Restart crashed pods
kubectl rollout restart deployment/myapp

# 3. Rollback to previous version
kubectl rollout undo deployment/myapp

# 4. Verify stability
kubectl get pods  # All running
# Monitor for 1 hour - stable

# 5. Fix memory leak offline
# Profile locally
# Find and fix leak
# Add memory monitoring

# 6. Redeploy with fix
# Deploy to staging first
# Load test
# Then production
```

---

## 🔧 Prevention Strategies

### Before Deployment
- [ ] Comprehensive testing (unit, integration, E2E)
- [ ] Staging environment tests
- [ ] Database migration dry-run
- [ ] Performance testing
- [ ] Security scanning
- [ ] Rollback plan documented

### During Deployment
- [ ] Deploy in off-peak hours
- [ ] Gradual rollout (canary/blue-green)
- [ ] Team monitoring deployment
- [ ] Health checks passing
- [ ] Quick rollback procedure ready

### After Deployment
- [ ] Monitor error rates
- [ ] Monitor performance metrics
- [ ] Check user feedback
- [ ] Run smoke tests
- [ ] Keep previous version available

---

**Remember:** The best rollback is one you never need. Test thoroughly, deploy gradually, and monitor carefully.
