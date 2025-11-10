# Dependency Management

Managing package updates, security patches, and version conflicts.

---

## 🚨 Security First

- ✋ **Always run security audits** before deploying
- ✋ **Address high/critical vulnerabilities immediately**
- ✋ **Never use dependencies with known exploits**
- ✋ **Keep dependencies reasonably up-to-date**

---

## 🔍 Checking Dependencies

### Security Audits

**Node.js:**
```bash
# Check for vulnerabilities
npm audit

# Show only high/critical
npm audit --audit-level=high

# Attempt automatic fixes
npm audit fix

# Force fix (may include breaking changes)
npm audit fix --force
```

**Python:**
```bash
# Check with safety
pip install safety
safety check

# Check with pip-audit
pip install pip-audit
pip-audit
```

**Automated scanning:**
- Dependabot (GitHub)
- Snyk
- WhiteSource
- Renovate

---

### Outdated Dependencies

**Node.js:**
```bash
# Check outdated packages
npm outdated

# Interactive update tool
npx npm-check-updates -i
```

**Python:**
```bash
pip list --outdated

# With pip-review
pip install pip-review
pip-review --local --interactive
```

---

## 📦 Update Strategies

### Patch Updates (1.2.3 → 1.2.4)

**Safe to auto-update** - bug fixes only, no breaking changes

```bash
# Update all patch versions
npm update
```

**Policy:** Update regularly (weekly/monthly)

---

### Minor Updates (1.2.0 → 1.3.0)

**Generally safe** - new features, backward compatible

```bash
# Update specific package to minor version
npm update lodash

# Or manually
npm install lodash@^1.3.0
```

**Policy:** Review changelog, update monthly, test thoroughly

---

### Major Updates (1.x → 2.x)

**Breaking changes** - requires code changes

```bash
# Update to specific major version
npm install express@5

# Check what breaks
npm test
```

**Policy:**
1. Read migration guide
2. Review breaking changes
3. Update in dev branch
4. Test extensively
5. Deploy to staging first
6. Monitor carefully in production

---

## 🎯 Update Process

### Step 1: Check Current State

```bash
# 1. Ensure all tests pass
npm test

# 2. Check current dependencies
npm list --depth=0

# 3. Check for vulnerabilities
npm audit

# 4. Check for outdated
npm outdated
```

---

### Step 2: Plan Updates

**Categorize updates:**
```
Critical (security vulnerabilities):
- jsonwebtoken: 8.5.1 → 9.0.0 (CVE-2022-xxxx)
- Update immediately

High Priority (major dependencies):
- react: 17.0.2 → 18.2.0
- Review migration guide, plan carefully

Medium Priority (minor/patch):
- axios: 0.27.0 → 0.28.0
- lodash: 4.17.20 → 4.17.21
- Safe to update, test

Low Priority (dev dependencies):
- @types/node: 16.x → 18.x
- Update when convenient
```

---

### Step 3: Update Incrementally

**Don't update everything at once!**

```bash
# Bad: Update everything
npm update  # Chaos!

# Good: Update one at a time
npm install axios@latest
npm test  # Verify works

npm install lodash@latest
npm test  # Verify works

npm install react@latest react-dom@latest
npm test  # Fix any breaking changes
```

---

### Step 4: Test Thoroughly

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Build
npm run build

# Run locally
npm start
# Manual smoke testing
```

---

### Step 5: Deploy Safely

```bash
# 1. Create branch
git checkout -b chore/update-dependencies

# 2. Commit
git commit -m "chore(deps): update axios to 0.28.0"

# 3. Deploy to staging
# Verify in staging environment

# 4. Create PR, get reviewed
# 5. Deploy to production
# 6. Monitor for issues
```

---

## ⚠️ Handling Breaking Changes

### Read the Changelog

```
Before: axios@0.x
After: axios@1.x

Breaking changes:
- Removed deprecated APIs
- Changed error format
- New TypeScript types
```

### Follow Migration Guide

Most popular libraries provide migration guides:
- React: https://react.dev/blog/2022/03/08/react-18-upgrade-guide
- Next.js: https://nextjs.org/docs/upgrading
- Express: https://expressjs.com/en/guide/migrating-5.html

### Update Code Gradually

```typescript
// Before (axios 0.x)
axios.get(url, { params })
  .then(response => response.data)
  .catch(error => error.response.data);

// After (axios 1.x)
axios.get(url, { params })
  .then(response => response.data)
  .catch(error => {
    if (axios.isAxiosError(error)) {
      return error.response?.data;
    }
    throw error;
  });
```

---

## 🔒 Dependency Locking

### Lock Files

**Always commit lock files:**
- `package-lock.json` (npm)
- `yarn.lock` (yarn)
- `pnpm-lock.yaml` (pnpm)
- `Pipfile.lock` (Python/pipenv)
- `poetry.lock` (Python/poetry)

**Why:** Ensures consistent installs across environments

---

### Using Lock Files

```bash
# Install exact versions from lock file
npm ci  # Faster, more reliable than npm install

# Update lock file after changes
npm install
git add package-lock.json
git commit -m "chore: update lock file"
```

---

## 📊 Dependency Best Practices

### Keep Dependencies Minimal

```
Before: 150 dependencies (many unused)
After: 50 dependencies (only what's needed)

Benefits:
- Smaller bundle size
- Fewer security vulnerabilities
- Faster installs
- Less breaking changes
```

**Audit regularly:**
```bash
# Find unused dependencies
npx depcheck
```

---

### Pin Versions in Production

```json
// Development: Allow minor updates
{
  "dependencies": {
    "express": "^4.18.0"  // Allows 4.x updates
  }
}

// Production/Library: Exact versions
{
  "dependencies": {
    "express": "4.18.2"  // Exact version only
  }
}
```

---

### Separate Dev and Prod Dependencies

```json
{
  "dependencies": {
    "express": "^4.18.0",  // Needed in production
    "react": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^18.0.0",  // Only for development
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
```

---

## 🚨 Vulnerability Response

### When Critical Vulnerability Found

```
1. ASSESS IMPACT
   - Are we using the vulnerable function?
   - Is it reachable from user input?
   - What's the exploit risk?

2. UPDATE IMMEDIATELY if exploitable
   npm audit fix
   npm test
   Deploy ASAP

3. If auto-fix not possible
   - Find manual fix in changelog
   - Apply fix
   - Test
   - Deploy

4. If no fix available
   - Find alternative package
   - Or implement mitigation
   - Or disable feature temporarily
```

---

### Example: jsonwebtoken Vulnerability

```
Alert: jsonwebtoken@8.5.1 has vulnerability CVE-2022-23529

Impact: Can forge tokens with algorithm confusion

Fix available: Update to 9.0.0

Breaking changes:
- Requires Node.js 12+
- Some deprecated options removed

Action:
1. npm install jsonwebtoken@9.0.0
2. Check deprecation warnings
3. Update code if needed
4. npm test
5. Deploy immediately
```

---

## 📋 Dependency Update Checklist

### Before Updating
- [ ] All tests passing
- [ ] No uncommitted changes
- [ ] Create feature branch

### During Update
- [ ] Read changelog
- [ ] Review breaking changes
- [ ] Update one dependency at a time
- [ ] Run tests after each update
- [ ] Fix any breaking changes
- [ ] Update lock file

### After Update
- [ ] All tests pass
- [ ] Build succeeds
- [ ] No new linting errors
- [ ] Smoke test locally
- [ ] Deploy to staging
- [ ] Monitor staging
- [ ] Create PR
- [ ] Deploy to production
- [ ] Monitor production

---

## 🎯 Maintenance Schedule

### Weekly
- [ ] Check security advisories
- [ ] Run `npm audit`
- [ ] Address critical/high vulnerabilities

### Monthly
- [ ] Check for outdated dependencies (`npm outdated`)
- [ ] Update patch versions (`npm update`)
- [ ] Review and plan minor/major updates
- [ ] Remove unused dependencies

### Quarterly
- [ ] Major version updates for core dependencies
- [ ] Comprehensive dependency audit
- [ ] Review and update dev dependencies
- [ ] Update project to latest Node.js LTS

---

**Remember:** Dependencies are a security responsibility. Keep them updated, but test changes thoroughly before deploying.
