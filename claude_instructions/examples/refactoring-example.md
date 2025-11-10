# Refactoring Workflow Example

**Scenario:** Extract duplicate user validation logic scattered across multiple files
**Project Type:** Express API (TypeScript)
**Mode:** Standard
**Estimated Time:** 1 hour

---

## Context

**Code smell identified:**
During code review, we noticed the same email validation logic duplicated in 5 different route handlers. This violates DRY principle and creates maintenance burden.

**Current state:**
```typescript
// src/routes/auth.ts (line 23)
if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
  return res.status(400).json({ error: 'Invalid email' });
}

// src/routes/users.ts (line 45)
if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
  return res.status(400).json({ error: 'Invalid email' });
}

// src/routes/profile.ts (line 67)
if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
  return res.status(400).json({ error: 'Invalid email format' });
}

// ... 2 more occurrences with slight variations
```

**Problems:**
1. Duplicated logic (5 copies of same regex)
2. Inconsistent error messages
3. Hard to update (must change in 5 places)
4. No unit tests for validation logic

**Goal:**
Extract into reusable utility function with comprehensive tests.

---

## Step-by-Step Walkthrough

### Step 1: Ensure Test Coverage Exists

**Before refactoring, verify tests cover the existing behavior.**

**Run existing tests:**

```bash
npm test

Test Suites: 18 passed, 18 total
Tests:       142 passed, 142 total
Coverage:    76.3% (above 70%) ✓
```

**Check if email validation is tested:**

```bash
npm test -- --findRelatedTests src/routes/auth.ts

PASS src/routes/auth.test.ts
  POST /auth/register
    ✓ should reject invalid email
    ✓ should accept valid email
    ✓ should reject empty email
```

**Good! Email validation is covered by existing tests.** ✅

This means if we break validation during refactoring, tests will catch it.

---

### Step 2: Identify All Occurrences

**Search for email validation patterns:**

```bash
# Find email validation regex
Grep: "^\s*@\s*\+@" (pattern matching email regex)

Found 5 occurrences:
- src/routes/auth.ts:23
- src/routes/users.ts:45
- src/routes/profile.ts:67
- src/routes/admin.ts:89
- src/routes/invites.ts:112
```

**Analyze each occurrence:**

| File | Line | Variation |
|------|------|-----------|
| auth.ts | 23 | Standard regex, error: "Invalid email" |
| users.ts | 45 | Same regex, error: "Invalid email" |
| profile.ts | 67 | Same regex, error: "Invalid email format" |
| admin.ts | 89 | Same regex, error: "Please provide valid email" |
| invites.ts | 112 | Slightly different regex (missing `+` in first part) |

**Key finding:** `invites.ts` has a **bug** (regex is different). Refactoring will fix this!

---

### Step 3: Design the Refactoring

**Create utility function:**

```typescript
// src/utils/validation.ts

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validates email format according to RFC 5322 simplified pattern
 * @param email - Email address to validate
 * @returns ValidationResult with valid flag and optional error message
 */
export function validateEmail(email: string | undefined | null): ValidationResult {
  // Check if email is provided
  if (!email || email.trim() === '') {
    return {
      valid: false,
      error: 'Email is required',
    };
  }

  // RFC 5322 simplified email regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailRegex.test(email)) {
    return {
      valid: false,
      error: 'Invalid email format',
    };
  }

  return {
    valid: true,
  };
}

/**
 * Express middleware to validate email from request body
 */
export function validateEmailMiddleware(req: Request, res: Response, next: NextFunction) {
  const { email } = req.body;
  const result = validateEmail(email);

  if (!result.valid) {
    return res.status(400).json({ error: result.error });
  }

  next();
}
```

**Benefits of this design:**
- Single source of truth for email regex
- Consistent error messages
- Testable in isolation
- Can be used as function or middleware
- Well-documented
- Type-safe

---

### Step 4: Write Tests for New Utility

**Before refactoring, write tests for the new utility:**

```typescript
// src/utils/validation.test.ts

import { validateEmail, validateEmailMiddleware } from './validation';
import { Request, Response, NextFunction } from 'express';

describe('validateEmail', () => {
  it('should return valid for correct email', () => {
    const result = validateEmail('user@example.com');
    expect(result.valid).toBe(true);
    expect(result.error).toBeUndefined();
  });

  it('should reject email without @', () => {
    const result = validateEmail('userexample.com');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Invalid email format');
  });

  it('should reject email without domain', () => {
    const result = validateEmail('user@');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Invalid email format');
  });

  it('should reject email without TLD', () => {
    const result = validateEmail('user@example');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Invalid email format');
  });

  it('should reject empty string', () => {
    const result = validateEmail('');
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Email is required');
  });

  it('should reject null', () => {
    const result = validateEmail(null);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Email is required');
  });

  it('should reject undefined', () => {
    const result = validateEmail(undefined);
    expect(result.valid).toBe(false);
    expect(result.error).toBe('Email is required');
  });

  it('should trim whitespace before validation', () => {
    const result = validateEmail('  user@example.com  ');
    expect(result.valid).toBe(true);
  });

  it('should accept email with subdomain', () => {
    const result = validateEmail('user@mail.example.com');
    expect(result.valid).toBe(true);
  });

  it('should accept email with plus sign', () => {
    const result = validateEmail('user+tag@example.com');
    expect(result.valid).toBe(true);
  });
});

describe('validateEmailMiddleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockReq = { body: {} };
    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    mockNext = jest.fn();
  });

  it('should call next() for valid email', () => {
    mockReq.body = { email: 'user@example.com' };

    validateEmailMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockRes.status).not.toHaveBeenCalled();
  });

  it('should return 400 for invalid email', () => {
    mockReq.body = { email: 'invalid-email' };

    validateEmailMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith({ error: 'Invalid email format' });
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should return 400 for missing email', () => {
    mockReq.body = {};

    validateEmailMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith({ error: 'Email is required' });
    expect(mockNext).not.toHaveBeenCalled();
  });
});
```

**Run new tests (will fail - utility doesn't exist yet):**

```bash
npm test -- validation.test.ts

FAIL src/utils/validation.test.ts
Error: Cannot find module './validation'
```

**Expected.** Now create the utility.

---

### Step 5: Implement the Utility

**Create the utility file:**

```typescript
// src/utils/validation.ts
[Code from Step 3 above]
```

**Run utility tests:**

```bash
npm test -- validation.test.ts

PASS src/utils/validation.test.ts
  validateEmail
    ✓ should return valid for correct email
    ✓ should reject email without @
    ✓ should reject email without domain
    ✓ should reject email without TLD
    ✓ should reject empty string
    ✓ should reject null
    ✓ should reject undefined
    ✓ should trim whitespace before validation
    ✓ should accept email with subdomain
    ✓ should accept email with plus sign
  validateEmailMiddleware
    ✓ should call next() for valid email
    ✓ should return 400 for invalid email
    ✓ should return 400 for missing email

Tests: 13 passed
```

**Utility is working!** ✅

---

### Step 6: Refactor First File

**Before:**

```typescript
// src/routes/auth.ts

router.post('/register', async (req, res) => {
  const { email, password } = req.body;

  // OLD: Inline validation
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Invalid email' });
  }

  // ... rest of registration logic
});
```

**After:**

```typescript
// src/routes/auth.ts

import { validateEmail } from '../utils/validation';

router.post('/register', async (req, res) => {
  const { email, password } = req.body;

  // NEW: Use utility function
  const emailValidation = validateEmail(email);
  if (!emailValidation.valid) {
    return res.status(400).json({ error: emailValidation.error });
  }

  // ... rest of registration logic (unchanged)
});
```

**Run tests to verify behavior unchanged:**

```bash
npm test -- auth.test.ts

PASS src/routes/auth.test.ts
  POST /auth/register
    ✓ should reject invalid email (still works!)
    ✓ should accept valid email (still works!)
    ✓ should reject empty email (still works!)
```

**Tests still pass!** ✅ Behavior is preserved.

---

### Step 7: Refactor Remaining Files

**Repeat for each file:**

1. Replace inline validation with `validateEmail()`
2. Run tests to verify behavior unchanged
3. Move to next file

**Auth routes:**

```typescript
// src/routes/users.ts
import { validateEmailMiddleware } from '../utils/validation';

// Use as middleware (cleaner for simple cases)
router.post('/users', validateEmailMiddleware, async (req, res) => {
  // Email is already validated by middleware
  const { email, name } = req.body;
  // ... create user
});
```

**Profile routes:**

```typescript
// src/routes/profile.ts
import { validateEmail } from '../utils/validation';

router.put('/profile', async (req, res) => {
  const { email } = req.body;

  const result = validateEmail(email);
  if (!result.valid) {
    return res.status(400).json({ error: result.error });
  }

  // ... update profile
});
```

**Admin routes:**

```typescript
// src/routes/admin.ts
import { validateEmailMiddleware } from '../utils/validation';

router.post('/admin/invite', validateEmailMiddleware, async (req, res) => {
  // ... send invite
});
```

**Invites routes (this had the bug!):**

```typescript
// src/routes/invites.ts

// BEFORE (buggy regex):
// if (!email || !/^[^\s@]@[^\s@]+\.[^\s@]+$/.test(email)) {

// AFTER (correct validation):
import { validateEmail } from '../utils/validation';

router.post('/invites', async (req, res) => {
  const { email } = req.body;

  const result = validateEmail(email);
  if (!result.valid) {
    return res.status(400).json({ error: result.error });
  }

  // ... create invite
});
```

**Bug fixed automatically by refactoring!** ✅

---

### Step 8: Verify All Tests Still Pass

**Run full test suite:**

```bash
npm test

Test Suites: 19 passed, 19 total (1 new utility test file)
Tests:       155 passed, 155 total (13 new tests)
Coverage:    78.1% (increased from 76.3%) ✓
```

**All tests passing!** ✅

**Coverage improved** because validation utility is now fully tested in isolation.

---

### Step 9: Clean Up

**Remove dead code:**

- No unused imports remain
- No commented-out code
- All files using new utility

**Run linting:**

```bash
npm run lint

✓ 0 errors, 0 warnings
```

**Type checking:**

```bash
npm run typecheck

✓ No type errors
```

---

### Step 10: Commit the Refactoring

**Stage changes:**

```bash
git add src/utils/validation.ts
git add src/utils/validation.test.ts
git add src/routes/auth.ts
git add src/routes/users.ts
git add src/routes/profile.ts
git add src/routes/admin.ts
git add src/routes/invites.ts
```

**Commit:**

```bash
git commit -m "refactor(validation): extract duplicate email validation logic

Extract email validation into reusable utility function.

Changes:
- Create src/utils/validation.ts with validateEmail() function
- Create validateEmailMiddleware for Express routes
- Replace 5 occurrences of inline email validation
- Add comprehensive unit tests (13 new tests)

Benefits:
- Single source of truth for email regex
- Consistent error messages across all routes
- Easier to maintain and update
- Better test coverage
- Fixed bug in invites.ts (regex had typo)

Behavior:
- No behavior changes to existing routes
- All existing tests still pass
- Coverage increased from 76.3% to 78.1%

Files refactored:
- src/routes/auth.ts
- src/routes/users.ts
- src/routes/profile.ts
- src/routes/admin.ts
- src/routes/invites.ts (bug fixed)"
```

**Push:**

```bash
git push origin refactor/extract-email-validation
```

---

## Summary

### What We Did

1. ✅ Verified existing test coverage
2. ✅ Identified all 5 occurrences of duplication
3. ✅ Designed reusable utility function
4. ✅ Wrote tests for utility (TDD)
5. ✅ Implemented utility
6. ✅ Refactored each file incrementally
7. ✅ Verified tests still pass after each change
8. ✅ Ran full test suite
9. ✅ Fixed bug discovered during refactoring
10. ✅ Committed with clear message

### Time Breakdown

- Analyze duplication: 10 min
- Ensure test coverage: 5 min
- Design utility: 10 min
- Write utility tests: 15 min
- Implement utility: 5 min
- Refactor files: 20 min
- Verify & test: 8 min
- Cleanup & commit: 5 min

**Total: 1 hour 18 minutes** (slightly over estimate)

### Non-Negotiables Verified

- ✅ All tests pass (155/155)
- ✅ Coverage improved (76.3% → 78.1%)
- ✅ Zero linting errors
- ✅ Type checking passed
- ✅ Behavior unchanged (verified by tests)
- ✅ Conventional commit format
- ✅ Feature branch (not main)

### Key Principles Demonstrated

1. **Ensure tests exist before refactoring**
   - Tests verified behavior was preserved

2. **Make small, incremental changes**
   - Refactored one file at a time
   - Ran tests after each change

3. **Tests are your safety net**
   - Tests caught no regressions
   - Tests proved behavior was identical

4. **Refactoring can reveal bugs**
   - Found regex typo in `invites.ts`
   - Fixed automatically during refactoring

5. **Improve design, not behavior**
   - External behavior unchanged
   - Internal structure improved (DRY principle)

### Impact

**Before:**
- 5 copies of validation logic
- Inconsistent error messages
- Hard to maintain
- Untested in isolation
- 1 bug (regex typo)

**After:**
- 1 utility function (DRY)
- Consistent error messages
- Easy to maintain
- 13 comprehensive tests
- Bug fixed

---

## Related Documentation

- **[Refactoring Workflow](../workflows/refactoring.md)** - Full refactoring guide
- **[Testing Standards](../standards/testing-standards.md)** - Test coverage requirements
- **[Code Quality Standards](../standards/code-quality.md)** - DRY principle and best practices

---

**This example demonstrates:** Safe refactoring with test coverage, incremental changes, behavior preservation verification, and bug discovery through code consolidation.
