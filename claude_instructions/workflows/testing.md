# Testing Workflow

Framework for writing and maintaining tests.

---

## 🎯 Core Principle

**Tests prove code works.** Write tests that give confidence, catch bugs, and document behavior.

---

## 🚨 Non-Negotiables

- ✋ **All tests must pass** before committing
- ✋ **Minimum 70% code coverage** (80% for critical paths)
- ✋ **Tests must be deterministic** (no flaky tests)
- ✋ **Tests for all new features** and bug fixes
- ✋ **Critical paths must have tests** (auth, payments, data integrity)

---

## 🔄 Framework Heartbeat Integration

**This workflow integrates with the Framework Heartbeat Protocol and fights testing theater.**

### Context Anchors (Auto-triggered)

These checkpoints trigger framework validation at critical workflow points:

**[CONTEXT ANCHOR: Testing Workflow Start]**
- Re-read non-negotiables for testing
- **CRITICAL:** Re-read fail-first protocol (Phase 2 will add this)
- Confirm: Tests will fail first, then pass after implementation

**[CONTEXT ANCHOR: Before Writing Test]**
- Identify what behavior we're validating
- Determine what bug this test should catch
- Plan: Write test → Verify it fails → Implement → Verify it passes

**[CONTEXT ANCHOR: After Writing Test]**
- **CRITICAL:** Run test and verify it FAILS
- If test passes before implementation: Test is not testing anything (theater)
- If test doesn't fail: Revise test or implementation

**[CONTEXT ANCHOR: Testing Complete]**
- Framework heartbeat if 20+ messages since last
- Verify no weak assertions (toBeDefined, toBeTruthy)
- Check coverage meets minimums (≥70% overall, ≥80% critical)

### Manual Framework Commands

During testing, you can use:

- `SHOW SESSION STATUS` - Verify you're still in testing workflow
- `REFRESH FRAMEWORK` - If writing extensive test suites
- `FRAMEWORK DRIFT CHECK` - Before committing tests

**Purpose:** Testing workflow is where "testing theater" happens most often. Context anchors enforce fail-first protocol to ensure tests actually validate behavior.

### Anti-Theater Checklist

Before committing tests, verify:
- [ ] Every test failed before implementation
- [ ] No weak assertions (toBeDefined, toBeTruthy, expect(true))
- [ ] Coverage ≥ minimums
- [ ] Tests validate behavior, not just execute code
- [ ] Can explain what bug each test catches

---

## 📋 Test Types

### Unit Tests
**What:** Test individual functions/methods in isolation
**When:** Most code should have unit tests
**Coverage:** 70-90%

```typescript
// Unit test example
describe('calculateDiscount', () => {
  it('applies 10% discount for premium users', () => {
    const result = calculateDiscount(100, { isPremium: true });
    expect(result).toBe(90);
  });

  it('returns original price for regular users', () => {
    const result = calculateDiscount(100, { isPremium: false });
    expect(result).toBe(100);
  });
});
```

---

### Integration Tests
**What:** Test multiple components working together
**When:** API endpoints, database operations, service interactions
**Coverage:** Critical flows

```typescript
// Integration test example
describe('POST /api/users', () => {
  it('creates user and returns 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', password: 'password123' });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');

    // Verify in database
    const user = await db.users.findByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});
```

---

### End-to-End Tests
**What:** Test complete user workflows
**When:** Critical user journeys
**Coverage:** Key flows only (expensive to maintain)

```typescript
// E2E test example (Playwright, Cypress)
test('user can sign up and create a post', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('[name="email"]', 'user@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('/dashboard');

  await page.click('text=New Post');
  await page.fill('[name="title"]', 'My First Post');
  await page.click('button:has-text("Publish")');

  await expect(page.locator('text=My First Post')).toBeVisible();
});
```

---

## 📋 Framework

### 1. What to Test

**DO test:**
- Business logic and calculations
- Validation functions
- API endpoints
- Database operations
- Error handling
- Edge cases and boundary conditions
- Authentication/authorization
- Critical user workflows

**DON'T test:**
- Third-party libraries (they have their own tests)
- Framework internals
- Simple getters/setters with no logic
- Generated code

---

### 2. Writing Effective Tests

**Follow AAA pattern:**
- **Arrange:** Set up test data
- **Act:** Execute the code being tested
- **Assert:** Verify the result

```typescript
describe('User validation', () => {
  it('rejects emails without @ symbol', () => {
    // Arrange
    const invalidEmail = 'notanemail.com';

    // Act
    const result = () => validateEmail(invalidEmail);

    // Assert
    expect(result).toThrow('Invalid email format');
  });
});
```

---

**Test behavior, not implementation:**

```typescript
❌ Bad: Tests implementation details
it('calls database.query with correct SQL', () => {
  const spy = jest.spyOn(database, 'query');
  getUser('123');
  expect(spy).toHaveBeenCalledWith('SELECT * FROM users WHERE id = ?', ['123']);
});

✅ Good: Tests behavior
it('returns user when found', async () => {
  const user = await getUser('123');
  expect(user).toEqual({ id: '123', name: 'John' });
});
```

---

**Test edge cases:**

```typescript
describe('calculateAge', () => {
  // Happy path
  it('calculates age correctly', () => {
    expect(calculateAge('1990-01-01')).toBe(35);
  });

  // Edge cases
  it('handles birthday today', () => {
    const today = new Date().toISOString().split('T')[0];
    expect(calculateAge(today)).toBe(0);
  });

  it('handles future dates', () => {
    expect(() => calculateAge('2030-01-01')).toThrow();
  });

  it('handles invalid dates', () => {
    expect(() => calculateAge('invalid')).toThrow();
  });

  it('handles null/undefined', () => {
    expect(() => calculateAge(null)).toThrow();
  });
});
```

---

### 3. Test Organization

**Structure:**
```
tests/
├── unit/
│   ├── services/
│   │   ├── userService.test.ts
│   │   └── orderService.test.ts
│   └── utils/
│       └── validation.test.ts
├── integration/
│   └── api/
│       ├── users.test.ts
│       └── orders.test.ts
└── e2e/
    ├── signup.spec.ts
    └── checkout.spec.ts
```

**Or co-located:**
```
src/
├── services/
│   ├── userService.ts
│   └── userService.test.ts
└── utils/
    ├── validation.ts
    └── validation.test.ts
```

---

### 4. Test Data Management

**Use factories/builders:**

```typescript
// testUtils.ts
export function createMockUser(overrides = {}) {
  return {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    isActive: true,
    ...overrides,
  };
}

// In tests
const user = createMockUser({ isActive: false });
```

**Use database fixtures for integration tests:**

```typescript
beforeEach(async () => {
  await db.seed('users', [
    { id: '1', email: 'user1@example.com' },
    { id: '2', email: 'user2@example.com' },
  ]);
});

afterEach(async () => {
  await db.truncate('users');
});
```

---

### 5. Running Tests

**Full suite:**
```bash
npm test
```

**Specific file:**
```bash
npm test -- userService.test.ts
```

**Watch mode (during development):**
```bash
npm test -- --watch
```

**Coverage:**
```bash
npm run test:coverage
```

**By pattern:**
```bash
npm test -- --grep "user validation"
```

---

### 6. Debugging Failing Tests

**Process:**
```
1. Read the error message carefully
2. Identify which assertion failed
3. Add console.log to see actual values
4. Run just that one test
5. Fix the issue (code or test)
6. Remove console.logs
7. Run full suite to check for regressions
```

**Example:**
```typescript
it('calculates total correctly', () => {
  const order = { items: [{ price: 10 }, { price: 20 }] };
  const total = calculateTotal(order);

  // Debug: See what we're actually getting
  console.log('Total:', total);
  console.log('Order:', JSON.stringify(order, null, 2));

  expect(total).toBe(30);
});
```

---

### 7. Handling Flaky Tests

**Flaky test:** Passes sometimes, fails sometimes

**Common causes:**
- Race conditions (async timing)
- Shared state between tests
- Depending on external services
- Time-dependent logic
- Random data

**Solutions:**

```typescript
❌ Flaky: Race condition
it('updates user after delay', async () => {
  updateUserAsync(user);
  await new Promise(resolve => setTimeout(resolve, 100)); // Brittle
  expect(user.updated).toBe(true);
});

✅ Fixed: Properly await
it('updates user after delay', async () => {
  await updateUserAsync(user);
  expect(user.updated).toBe(true);
});

❌ Flaky: Shared state
let user;
beforeEach(() => {
  user = { name: 'John' }; // Same object shared
});

✅ Fixed: Fresh state
beforeEach(() => {
  user = createMockUser(); // New object each time
});
```

---

### 8. Mocking

**When to mock:**
- External APIs
- Database in unit tests
- Time/dates
- Random values
- File system operations

```typescript
// Mock external API
jest.mock('../services/emailService', () => ({
  sendEmail: jest.fn().mockResolvedValue(true),
}));

it('sends welcome email on signup', async () => {
  await signupUser({ email: 'test@example.com' });
  expect(emailService.sendEmail).toHaveBeenCalledWith(
    'test@example.com',
    'Welcome!'
  );
});

// Mock time
jest.useFakeTimers();
jest.setSystemTime(new Date('2024-01-01'));

it('creates timestamp', () => {
  const timestamp = getCurrentTimestamp();
  expect(timestamp).toBe('2024-01-01T00:00:00.000Z');
});

jest.useRealTimers();
```

---

## 📊 Testing Checklist

### Before Committing
- [ ] All tests pass (`npm test`)
- [ ] Coverage ≥ 70% (`npm run test:coverage`)
- [ ] No skipped/disabled tests without reason
- [ ] No console.logs in tests
- [ ] Tests are deterministic (run multiple times)

### Test Quality
- [ ] Tests follow AAA pattern
- [ ] Test names are descriptive
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] No test interdependencies
- [ ] Mocks used appropriately

### Coverage
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Critical paths well tested
- [ ] Happy paths tested
- [ ] Error paths tested

---

## 💡 Examples

### Example: Testing an API Endpoint

```typescript
describe('POST /api/login', () => {
  // Happy path
  it('returns token for valid credentials', async () => {
    await db.users.create({
      email: 'user@example.com',
      password: await hash('password123'),
    });

    const response = await request(app)
      .post('/api/login')
      .send({ email: 'user@example.com', password: 'password123' });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('token');
  });

  // Error cases
  it('returns 401 for invalid password', async () => {
    await db.users.create({
      email: 'user@example.com',
      password: await hash('password123'),
    });

    const response = await request(app)
      .post('/api/login')
      .send({ email: 'user@example.com', password: 'wrongpassword' });

    expect(response.status).toBe(401);
    expect(response.body.error).toMatch(/invalid credentials/i);
  });

  it('returns 401 for non-existent user', async () => {
    const response = await request(app)
      .post('/api/login')
      .send({ email: 'nonexistent@example.com', password: 'password123' });

    expect(response.status).toBe(401);
  });

  // Validation
  it('returns 400 for missing email', async () => {
    const response = await request(app)
      .post('/api/login')
      .send({ password: 'password123' });

    expect(response.status).toBe(400);
  });

  // Security
  it('rate limits failed login attempts', async () => {
    for (let i = 0; i < 5; i++) {
      await request(app)
        .post('/api/login')
        .send({ email: 'user@example.com', password: 'wrong' });
    }

    const response = await request(app)
      .post('/api/login')
      .send({ email: 'user@example.com', password: 'wrong' });

    expect(response.status).toBe(429); // Too Many Requests
  });
});
```

---

### Example: Testing with Database

```typescript
describe('UserRepository', () => {
  beforeEach(async () => {
    await db.migrate.latest();
    await db.seed.run();
  });

  afterEach(async () => {
    await db.migrate.rollback();
  });

  it('finds user by email', async () => {
    const user = await userRepo.findByEmail('test@example.com');
    expect(user).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });

  it('returns null for non-existent email', async () => {
    const user = await userRepo.findByEmail('nonexistent@example.com');
    expect(user).toBeNull();
  });

  it('creates user with hashed password', async () => {
    const user = await userRepo.create({
      email: 'new@example.com',
      password: 'password123',
    });

    expect(user.password).not.toBe('password123');
    expect(user.password).toMatch(/^\$2[aby]\$/); // bcrypt hash
  });
});
```

---

**Remember:** Good tests catch bugs before users do. Invest in comprehensive testing to move fast with confidence.
