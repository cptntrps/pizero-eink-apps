# Bug Fix Workflow Example

**Scenario:** Login button crashes when email field is empty
**Project Type:** Next.js Web Application
**Mode:** Standard
**Estimated Time:** 30 minutes

---

## Context

A user reported: *"When I try to login without entering an email, the whole page crashes with a white screen."*

---

## Step-by-Step Walkthrough

### Step 1: Understand the Bug

**Read the bug report:**
```
User Report:
- Action: Click "Login" button without entering email
- Expected: Show validation error "Email is required"
- Actual: Page crashes (white screen)
- Browser: Chrome 118
- Environment: Production
```

**Ask clarifying questions (if needed):**
- Can you reproduce this consistently? **Yes**
- Does it happen with other empty fields? **Only email**
- Any error in browser console? **Yes, TypeError**

**Initial assessment:**
- **Severity:** HIGH (crashes user experience)
- **Impact:** All users trying to login
- **Root cause hypothesis:** Missing null check on email field

---

### Step 2: Locate the Issue

**Search for login-related code:**

```bash
# Search for login component
Grep: "login" in src/ (files_with_matches)

Found:
- src/components/LoginForm.tsx
- src/pages/login.tsx
- src/utils/auth.ts
```

**Read the LoginForm component:**

```typescript
// src/components/LoginForm.tsx (lines 15-30)

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // BUG: No validation before accessing email.toLowerCase()
  const normalizedEmail = email.toLowerCase();

  const result = await signIn({
    email: normalizedEmail,
    password,
  });

  if (result.error) {
    setError(result.error);
  }
};
```

**Found the bug!**
- Line 19: `email.toLowerCase()` called without checking if `email` is empty
- When email is empty string, `toLowerCase()` itself works, but something downstream crashes
- Need to check what happens in `signIn()`

**Check signIn function:**

```typescript
// src/utils/auth.ts (lines 45-50)

export async function signIn({ email, password }: SignInParams) {
  // BUG: Assumes email is valid
  const user = await db.users.findOne({
    email: email  // This query fails if email is empty
  });

  // ... rest of code
}
```

**Root cause identified:**
- Empty email passes through to database query
- Database throws uncaught error
- Error crashes the React component tree (no error boundary)

---

### Step 3: Write a Failing Test

**Create test that reproduces the bug:**

```typescript
// src/components/LoginForm.test.tsx

describe('LoginForm', () => {
  it('should show validation error when email is empty', async () => {
    render(<LoginForm />);

    // Leave email empty
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    // Should show validation error, not crash
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });

    // Should not call signIn
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it('should handle empty email without crashing', async () => {
    // This test currently fails (reproduces the bug)
    render(<LoginForm />);

    const submitButton = screen.getByRole('button', { name: /login/i });

    // Click submit with empty email
    fireEvent.click(submitButton);

    // Component should not crash
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
});
```

**Run the test:**

```bash
npm test -- LoginForm.test.tsx

FAIL src/components/LoginForm.test.tsx
  ✗ should show validation error when email is empty (250ms)
  ✗ should handle empty email without crashing (180ms)

  TypeError: Cannot read property 'findOne' of undefined
```

**Good! Test reproduces the bug.** ✅

---

### Step 4: Fix the Implementation

**Implement input validation:**

```typescript
// src/components/LoginForm.tsx

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  // FIX: Validate email before proceeding
  if (!email || email.trim() === '') {
    setError('Email is required');
    return;
  }

  if (!password || password.trim() === '') {
    setError('Password is required');
    return;
  }

  const normalizedEmail = email.toLowerCase().trim();

  const result = await signIn({
    email: normalizedEmail,
    password,
  });

  if (result.error) {
    setError(result.error);
  }
};
```

**Also add error boundary (defense in depth):**

```typescript
// src/components/LoginForm.tsx

export default function LoginFormWithErrorBoundary() {
  return (
    <ErrorBoundary fallback={<LoginErrorFallback />}>
      <LoginForm />
    </ErrorBoundary>
  );
}

function LoginErrorFallback() {
  return (
    <div className="error">
      <p>Something went wrong. Please refresh and try again.</p>
    </div>
  );
}
```

---

### Step 5: Verify the Solution

**Run the tests:**

```bash
npm test -- LoginForm.test.tsx

PASS src/components/LoginForm.test.tsx
  ✓ should show validation error when email is empty (120ms)
  ✓ should handle empty email without crashing (85ms)
  ✓ should submit successfully with valid credentials (150ms)
```

**All tests passing!** ✅

**Run full test suite:**

```bash
npm test

Test Suites: 23 passed, 23 total
Tests:       187 passed, 187 total
Coverage:    78.5% (above 70% minimum) ✓
```

**Manual verification:**

1. Start dev server: `npm run dev`
2. Navigate to http://localhost:3000/login
3. Click "Login" without entering email
4. **Result:** ✅ Shows "Email is required" error (no crash)
5. Enter valid email, click login
6. **Result:** ✅ Login works correctly

**Check linting and types:**

```bash
npm run lint
✓ 0 errors, 0 warnings

npm run typecheck
✓ No type errors
```

---

### Step 6: Commit with Proper Message

**Stage changes:**

```bash
git add src/components/LoginForm.tsx
git add src/components/LoginForm.test.tsx
git status

Changes to be committed:
  modified:   src/components/LoginForm.tsx
  modified:   src/components/LoginForm.test.tsx
```

**Commit with conventional format:**

```bash
git commit -m "fix(auth): prevent crash when email field is empty

Add input validation before calling signIn() to prevent TypeError
when user submits login form with empty email.

Changes:
- Add email/password validation in LoginForm.handleSubmit
- Trim whitespace from email input
- Add error boundary for additional safety
- Add tests for empty email scenarios

Fixes: #247 (Login crashes with empty email)

Tests:
- All existing tests pass
- New tests cover empty email validation
- Manual testing confirms fix"
```

**Push to feature branch:**

```bash
git push origin fix/login-empty-email-crash
```

---

## Summary

### What We Did

1. ✅ Reproduced the bug
2. ✅ Located root cause (missing validation)
3. ✅ Wrote failing tests
4. ✅ Fixed the implementation
5. ✅ Verified tests pass
6. ✅ Manual testing confirms fix
7. ✅ Committed with proper message

### Time Taken

- Understand bug: 5 minutes
- Locate issue: 8 minutes
- Write tests: 10 minutes
- Implement fix: 5 minutes
- Verify solution: 7 minutes
- Commit: 2 minutes

**Total: 37 minutes** (estimated 30 min)

### Non-Negotiables Verified

- ✅ All tests pass
- ✅ Coverage maintained (78.5% > 70%)
- ✅ Zero linting errors
- ✅ Type checking passed
- ✅ Conventional commit format
- ✅ Not committed to main (feature branch)

### Key Learnings

1. **Always write the test first** - Test confirmed the bug and verified the fix
2. **Validate inputs early** - Prevent errors from propagating downstream
3. **Defense in depth** - Error boundary provides backup if validation fails
4. **Clear commit message** - Documents the fix for future developers

---

## Related Documentation

- **[Bug Fix Workflow](../workflows/bug-fix.md)** - Full workflow guide
- **[Testing Standards](../standards/testing-standards.md)** - Test coverage requirements
- **[Git Conventions](../standards/git-conventions.md)** - Commit message format

---

**This example demonstrates:** Principle-oriented approach (understand → test → fix → verify) while maintaining all non-negotiable quality gates.
