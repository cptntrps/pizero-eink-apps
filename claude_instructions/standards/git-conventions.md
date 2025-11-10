# Git Conventions

Standards for commits, branches, and pull requests.

---

## 🚨 Non-Negotiables

- ✋ **NEVER commit directly to main/master**
- ✋ **ALWAYS use conventional commit format**
- ✋ **COMMITS must be atomic** (single logical change)
- ✋ **NO secrets, credentials, or API keys** in commits

---

## 📝 Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (Required)

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **refactor**: Code restructuring (no behavior change)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, config)
- **perf**: Performance improvements
- **style**: Code style changes (formatting, semicolons)
- **ci**: CI/CD changes
- **revert**: Reverting a previous commit

### Scope (Optional)

The module/feature affected:
- `auth`, `api`, `ui`, `database`, `payment`, etc.

### Subject (Required)

- Use imperative mood: "add" not "added" or "adds"
- No capital first letter
- No period at the end
- Max 50 characters
- Describe WHAT changed

### Body (Optional)

- Explain WHY, not WHAT
- Wrap at 72 characters
- Separate from subject with blank line

### Footer (Optional)

- Breaking changes: `BREAKING CHANGE: description`
- Issue references: `Fixes #123`, `Closes #456`, `Refs #789`

---

## ✅ Good Examples

```
feat(auth): add email verification flow

Users must verify email before accessing full features.
Sends verification link via email service.

Closes #234
```

```
fix(api): prevent null pointer in user profile endpoint

Added null check for user.email before accessing toLowerCase().
This was causing 500 errors when email was not set.

Fixes #567
```

```
refactor(validation): extract duplicate email validation

Email validation was duplicated in 3 places.
Extracted to utils/validateEmail.ts for DRY.
```

```
test(auth): add edge cases for login flow

Added tests for:
- unverified email
- expired token
- rate limiting
```

```
chore(deps): update dependencies to fix vulnerabilities

Updates:
- express: 4.17.1 → 4.18.2
- jsonwebtoken: 8.5.1 → 9.0.0

Addresses security advisory GHSA-xyz123
```

---

## ❌ Bad Examples

```
❌ update code
   (vague, no type, no details)

❌ Fixed bug
   (no scope, vague, past tense)

❌ feat: Added new feature for users to upload profile pictures and also fixed some bugs and refactored the code
   (too long, multiple changes, not atomic)

❌ WIP
   (not descriptive, shouldn't commit WIP to shared branches)
```

---

## 🌿 Branch Naming

### Format

```
<type>/<description>
```

### Examples

```
feat/email-verification
fix/null-pointer-in-profile
refactor/extract-validation
test/add-auth-edge-cases
chore/update-dependencies
```

### Rules

- Lowercase only
- Use hyphens, not spaces or underscores
- Short but descriptive
- Match the feature/fix you're working on

---

## 🔄 Branching Strategy

### Main Branches

- **main** (or **master**): Production-ready code
- **develop** (optional): Integration branch for features

### Feature Branches

```
main
 └─ feat/new-feature → merge back to main
```

### Workflow

```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feat/email-verification

# Make changes and commit
git add src/auth/emailVerification.ts
git commit -m "feat(auth): add email verification service"

# Push feature branch
git push -u origin feat/email-verification

# Create pull request
# After approval, merge to main
# Delete feature branch
git branch -d feat/email-verification
```

---

## 🔀 Pull Requests

### PR Title

Same format as commit messages:
```
feat(auth): add email verification flow
fix(api): prevent null pointer in profile endpoint
```

### PR Description Template

```markdown
## Summary
Brief description of what this PR does.

## Changes
- Added email verification service
- Updated user model with emailVerified field
- Added verification email template
- Added tests for verification flow

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Refactoring
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for this change
- [ ] Manual testing completed

## Checklist
- [x] Code follows project conventions
- [x] Self-reviewed the code
- [x] Commented complex logic
- [x] Updated documentation
- [x] No linting errors
- [x] All tests passing
- [ ] Reviewed by team member
```

---

## 🎯 Commit Best Practices

### Atomic Commits

Each commit should represent ONE logical change.

**❌ Bad (multiple changes in one commit):**
```
git commit -m "fix: fixed login bug, added profile page, updated dependencies"
```

**✅ Good (separate commits):**
```
git commit -m "fix(auth): add null check in login flow"
git commit -m "feat(profile): add user profile page"
git commit -m "chore(deps): update dependencies"
```

---

### Commit Often

**Don't wait to commit:**
```
✅ Implemented feature → test → commit
✅ Fixed bug → test → commit
✅ Refactored function → test → commit

❌ Worked all day → 50 files changed → one giant commit
```

---

### Test Before Committing

**ALWAYS verify before committing:**
```bash
# Run tests
npm test

# Run linting
npm run lint

# Run type checking
npm run typecheck

# Only commit if all pass
git commit -m "feat(api): add new endpoint"
```

---

### Clean History

**Before pushing, clean up local commits if needed:**

**❌ Messy history:**
```
fix typo
fix another typo
wip
wip 2
actually fix bug
```

**✅ Clean history (after squashing/rebasing):**
```
fix(auth): resolve login validation issue
```

**Interactive rebase:**
```bash
git rebase -i HEAD~5  # Squash last 5 commits
```

**But only rewrite history on local branches, NEVER on shared branches!**

---

## 🔐 Security

### Never Commit Secrets

**❌ NEVER commit:**
- API keys
- Passwords
- Access tokens
- Private keys
- `.env` files with secrets

**✅ Use environment variables:**
```javascript
// ❌ Bad
const apiKey = 'sk-1234567890abcdef';

// ✅ Good
const apiKey = process.env.API_KEY;
```

**✅ Document in `.env.example`:**
```bash
# .env.example (committed)
API_KEY=your_api_key_here
DATABASE_URL=postgresql://localhost/myapp

# .env (NOT committed, in .gitignore)
API_KEY=sk-real-key-here
DATABASE_URL=postgresql://real-server/myapp
```

---

### Check Before Committing

```bash
# Review what you're about to commit
git diff --staged

# Look for secrets
git diff --staged | grep -i "api_key\|password\|secret\|token"

# If found, remove them!
```

---

## 📊 Git Workflow Checklist

### Before Starting Work
- [ ] Pull latest from main: `git pull origin main`
- [ ] Create feature branch: `git checkout -b feat/my-feature`

### During Development
- [ ] Make focused changes
- [ ] Test frequently
- [ ] Commit atomically with conventional messages
- [ ] Write descriptive commit bodies for complex changes

### Before Pushing
- [ ] All tests pass
- [ ] No linting errors
- [ ] No secrets in code
- [ ] Commits are atomic and well-named
- [ ] History is clean (squash if needed)

### Creating PR
- [ ] Descriptive PR title (conventional format)
- [ ] Complete PR description
- [ ] Link related issues
- [ ] Request reviewers
- [ ] CI checks passing

### After Merge
- [ ] Delete feature branch
- [ ] Pull updated main
- [ ] Celebrate! 🎉

---

## 💡 Examples

### Example 1: Feature Development

```bash
# Start
git checkout main
git pull origin main
git checkout -b feat/profile-upload

# Work and commit atomically
git add src/services/imageUpload.ts
git commit -m "feat(profile): add image upload service"

git add src/api/routes/profile.ts
git commit -m "feat(profile): add image upload endpoint"

git add tests/imageUpload.test.ts
git commit -m "test(profile): add image upload tests"

# Push
git push -u origin feat/profile-upload

# Create PR
gh pr create --title "feat(profile): add profile image upload" \
  --body "Adds ability to upload profile pictures. Validates size and type."
```

---

### Example 2: Bug Fix

```bash
# Start
git checkout main
git pull origin main
git checkout -b fix/login-null-check

# Fix and test
git add src/auth/login.ts src/auth/login.test.ts
git commit -m "$(cat <<'EOF'
fix(auth): add null check before email access

Fixed crash when user.email is null.
Added optional chaining and test case.

Fixes #456
EOF
)"

# Push and create PR
git push -u origin fix/login-null-check
gh pr create --title "fix(auth): add null check in login" \
  --body "Fixes #456 - prevents crash when email is null"
```

---

**Remember:** Good git hygiene makes code review easier, debugging faster, and collaboration smoother.
