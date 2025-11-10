# Refactoring Workflow

Framework for improving code structure without changing behavior.

---

## 🎯 Core Principle

**Behavior must remain unchanged.** Refactoring changes HOW code works internally, never WHAT it does externally.

---

## 🚨 Non-Negotiables

Before completing any refactoring:

- ✋ **All existing tests must still pass** (unchanged)
- ✋ **No new bugs introduced**
- ✋ **No linting errors**
- ✋ **Behavior is identical** to before refactoring
- ✋ **Tests run BEFORE and AFTER** to verify equivalence

---

## 🔄 Framework Heartbeat Integration

**This workflow integrates with the Framework Heartbeat Protocol to maintain quality throughout refactoring.**

### Context Anchors (Auto-triggered)

These checkpoints trigger framework validation at critical workflow points:

**[CONTEXT ANCHOR: Refactoring Start]**
- Re-read non-negotiables for refactoring
- Verify tests exist before refactoring begins
- Confirm: Tests pass before → Refactor → Tests still pass after

**[CONTEXT ANCHOR: Before Refactoring]**
- Run full test suite and confirm all tests pass
- Capture baseline (all tests green)
- This proves any failures after refactoring are regressions

**[CONTEXT ANCHOR: After Each Refactoring Step]**
- Run tests immediately after each small change
- Verify behavior unchanged
- Small steps prevent large debugging sessions

**[CONTEXT ANCHOR: Refactoring Complete]**
- Framework heartbeat if 20+ messages since last
- Run full test suite one final time
- Verify zero regressions introduced

### Manual Framework Commands

During refactoring, you can use:

- `SHOW SESSION STATUS` - Verify you're still in refactoring workflow
- `REFRESH FRAMEWORK` - If refactoring session is complex
- `FRAMEWORK DRIFT CHECK` - Before committing refactored code

**Purpose:** Refactoring can be risky. Context anchors ensure test-first safety net remains active throughout.

---

## 📋 Framework

### 1. Identify Need for Refactoring

**Valid reasons to refactor:**
- Code is difficult to understand
- Duplicated logic (DRY violation)
- Function/class is too large or complex
- Poor naming makes intent unclear
- Coupling is too tight
- Testing is difficult
- Performance can be improved without complexity

**Invalid reasons:**
- "I would have written it differently"
- Personal style preference
- Using different libraries for no benefit
- Premature optimization

**Questions to ask:**
- Does this improve maintainability?
- Does this reduce complexity?
- Does this make the code easier to test?
- Is this worth the risk of breaking something?

---

### 2. Establish Safety Net

**BEFORE any refactoring:**

**Run existing tests:**
```bash
npm test
```

**All must pass.** If tests are failing, fix them first.

**Check test coverage:**
```bash
npm run test:coverage
```

**If coverage is low (<50%), add tests BEFORE refactoring:**
```
Current coverage: 30%

1. Add tests to reach 70%+
2. Verify tests pass
3. THEN refactor
```

**Why:** Tests prove behavior doesn't change.

---

### 3. Plan the Refactoring

**Break into small steps:**

**❌ Bad plan:**
```
Refactor the entire user module
```

**✅ Good plan:**
```
1. Extract validation logic to separate function
2. Test - ensure behavior unchanged
3. Rename confusing variables
4. Test again
5. Extract duplicate code to utility
6. Test again
```

**Use TodoWrite for complex refactoring:**
```
- Extract user validation logic
- Rename userId → id for consistency
- Extract duplicate email logic
- Simplify nested conditionals
- Add JSDoc comments
```

**Each step should be:**
- Small enough to understand
- Independently testable
- Reversible if needed

---

### 4. Refactor Incrementally

**One change at a time:**

**Example: Extract function**

**Before:**
```typescript
async function createUser(data: CreateUserInput) {
  // Validation inline
  if (!data.email || !data.email.includes('@')) {
    throw new Error('Invalid email');
  }
  if (!data.password || data.password.length < 8) {
    throw new Error('Password too short');
  }
  if (data.age && (data.age < 13 || data.age > 120)) {
    throw new Error('Invalid age');
  }

  const user = await db.users.create(data);
  return user;
}
```

**After - Step 1: Extract validation**
```typescript
function validateUserInput(data: CreateUserInput) {
  if (!data.email || !data.email.includes('@')) {
    throw new ValidationError('Invalid email');
  }
  if (!data.password || data.password.length < 8) {
    throw new ValidationError('Password too short');
  }
  if (data.age && (data.age < 13 || data.age > 120)) {
    throw new ValidationError('Invalid age');
  }
}

async function createUser(data: CreateUserInput) {
  validateUserInput(data);
  const user = await db.users.create(data);
  return user;
}
```

**Test after each step:**
```bash
npm test -- user.test.ts
```

**Continue only if tests pass.**

---

### 5. Common Refactoring Patterns

#### Extract Function

**When:** Function does multiple things, or has duplicated code

```typescript
// Before
function processOrder(order: Order) {
  // Validate
  if (!order.items.length) throw new Error('No items');
  if (order.total < 0) throw new Error('Invalid total');

  // Calculate tax
  const taxRate = order.state === 'CA' ? 0.0725 : 0.06;
  const tax = order.subtotal * taxRate;

  // Save
  return db.orders.create({ ...order, tax });
}

// After
function validateOrder(order: Order) {
  if (!order.items.length) throw new ValidationError('No items');
  if (order.total < 0) throw new ValidationError('Invalid total');
}

function calculateTax(subtotal: number, state: string): number {
  const taxRate = state === 'CA' ? 0.0725 : 0.06;
  return subtotal * taxRate;
}

function processOrder(order: Order) {
  validateOrder(order);
  const tax = calculateTax(order.subtotal, order.state);
  return db.orders.create({ ...order, tax });
}
```

---

#### Rename for Clarity

**When:** Names don't reflect purpose

```typescript
// Before
function getData(x: string) {
  const d = new Date();
  const r = await db.query('SELECT * FROM users WHERE id = ?', [x]);
  return r;
}

// After
function getUserById(userId: string): Promise<User> {
  return db.users.findById(userId);
}
```

---

#### Reduce Nesting

**When:** Deeply nested conditionals are hard to follow

```typescript
// Before
function canAccess(user: User, resource: Resource) {
  if (user) {
    if (user.isActive) {
      if (resource.isPublic) {
        return true;
      } else {
        if (resource.ownerId === user.id) {
          return true;
        } else {
          return false;
        }
      }
    } else {
      return false;
    }
  } else {
    return false;
  }
}

// After
function canAccess(user: User | null, resource: Resource): boolean {
  if (!user || !user.isActive) {
    return false;
  }

  if (resource.isPublic) {
    return true;
  }

  return resource.ownerId === user.id;
}
```

---

#### Remove Duplication

**When:** Same logic exists in multiple places

```typescript
// Before
async function updateUserEmail(userId: string, email: string) {
  if (!email || !email.includes('@')) {
    throw new Error('Invalid email');
  }
  return db.users.update(userId, { email });
}

async function updateUserProfile(userId: string, data: ProfileData) {
  if (data.email && (!data.email || !data.email.includes('@'))) {
    throw new Error('Invalid email');
  }
  return db.users.update(userId, data);
}

// After
function validateEmail(email: string) {
  if (!email || !email.includes('@')) {
    throw new ValidationError('Invalid email');
  }
}

async function updateUserEmail(userId: string, email: string) {
  validateEmail(email);
  return db.users.update(userId, { email });
}

async function updateUserProfile(userId: string, data: ProfileData) {
  if (data.email) {
    validateEmail(data.email);
  }
  return db.users.update(userId, data);
}
```

---

#### Simplify Conditionals

**When:** Complex boolean logic is confusing

```typescript
// Before
if (user.role === 'admin' || user.role === 'moderator' || user.permissions.includes('delete')) {
  // ...
}

// After
function canDelete(user: User): boolean {
  return user.role === 'admin'
    || user.role === 'moderator'
    || user.permissions.includes('delete');
}

if (canDelete(user)) {
  // ...
}
```

---

### 6. Verify Behavior Unchanged

**After each refactoring step:**

```bash
# Run full test suite
npm test

# Verify all tests still pass
# If any fail, revert and investigate
```

**Additional verification:**
- Run linting: `npm run lint`
- Run type checking: `npm run typecheck`
- Check coverage didn't decrease: `npm run test:coverage`

**Manual testing (if no automated tests):**
- Test the same scenarios as before
- Verify output is identical
- Check edge cases

---

### 7. Commit Incrementally

**Commit after each successful refactoring step:**

```bash
git add src/services/user.ts
git commit -m "refactor(user): extract validation to separate function"

# Continue with next step
# Commit again after next successful refactoring
```

**Why:** Small commits are easier to review and revert if needed.

---

## 🎚️ Adaptive Approach

### Small Refactoring (single function, < 50 lines)

```
1. Read function
2. Run tests (verify pass)
3. Make change
4. Run tests (verify still pass)
5. Commit
```

---

### Medium Refactoring (module, 50-200 lines)

```
1. Read module
2. Run tests
3. Create task breakdown
4. Refactor incrementally (one change at a time)
5. Test after each change
6. Commit after each successful step
```

---

### Large Refactoring (multiple modules, > 200 lines)

```
1. Discuss approach with user first
2. Add tests if coverage is low
3. Break into phases
4. Refactor Phase 1
5. Test thoroughly
6. Deploy and monitor
7. Continue with Phase 2 only if Phase 1 is stable
```

---

## ⚠️ Common Pitfalls

### Changing Behavior

**❌ Bad:**
```typescript
// Before: Returns null if not found
function getUser(id: string): User | null {
  return db.users.find(id) || null;
}

// After: Now throws error (BEHAVIOR CHANGE!)
function getUser(id: string): User {
  const user = db.users.find(id);
  if (!user) throw new Error('Not found');
  return user;
}
```

**✅ Good:**
```typescript
// Keep same return type and behavior
function getUser(id: string): User | null {
  return db.users.findById(id);
}
```

---

### Refactoring Without Tests

**❌ Bad:**
```
No tests exist → Refactor anyway → Hope it works
```

**✅ Good:**
```
No tests exist → Add tests first → Verify pass → Then refactor
```

---

### Too Many Changes at Once

**❌ Bad:**
```
git commit -m "refactor: rewrite entire module, rename everything, change structure"
```

**✅ Good:**
```
git commit -m "refactor: extract validation logic"
git commit -m "refactor: rename userId to id for consistency"
git commit -m "refactor: simplify nested conditionals"
```

---

## 📊 Refactoring Checklist

Before starting:
- [ ] Understand why refactoring is needed
- [ ] All existing tests pass
- [ ] Test coverage is adequate (≥70%)
- [ ] Plan broken into small steps

During refactoring:
- [ ] One change at a time
- [ ] Tests run after each change
- [ ] All tests still pass
- [ ] Behavior is unchanged
- [ ] Commit after each successful step

After refactoring:
- [ ] All tests pass
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Coverage hasn't decreased
- [ ] Code is more maintainable
- [ ] Committed with descriptive messages

---

## 💡 Examples

### Example 1: Reduce Complexity

**Before (cyclomatic complexity: 12):**
```typescript
function calculatePrice(item: Item, user: User) {
  let price = item.basePrice;

  if (user.isPremium) {
    price *= 0.9;
  }

  if (item.category === 'electronics') {
    if (user.hasElectronicsDiscount) {
      price *= 0.85;
    }
  }

  if (item.onSale) {
    price *= 0.8;
  }

  if (user.firstPurchase) {
    price *= 0.95;
  }

  return price;
}
```

**After (complexity: 4):**
```typescript
function calculateDiscount(item: Item, user: User): number {
  let discount = 1.0;

  if (user.isPremium) discount *= 0.9;
  if (user.firstPurchase) discount *= 0.95;
  if (item.onSale) discount *= 0.8;
  if (canApplyElectronicsDiscount(item, user)) discount *= 0.85;

  return discount;
}

function canApplyElectronicsDiscount(item: Item, user: User): boolean {
  return item.category === 'electronics' && user.hasElectronicsDiscount;
}

function calculatePrice(item: Item, user: User): number {
  const discount = calculateDiscount(item, user);
  return item.basePrice * discount;
}
```

---

### Example 2: Remove Duplication

**Before:**
```typescript
async function sendWelcomeEmail(userId: string) {
  const user = await db.users.findById(userId);
  if (!user) throw new Error('User not found');
  if (!user.email) throw new Error('No email');

  await emailService.send({
    to: user.email,
    subject: 'Welcome!',
    body: 'Thanks for signing up!',
  });
}

async function sendPasswordResetEmail(userId: string, token: string) {
  const user = await db.users.findById(userId);
  if (!user) throw new Error('User not found');
  if (!user.email) throw new Error('No email');

  await emailService.send({
    to: user.email,
    subject: 'Reset Password',
    body: `Reset link: ${token}`,
  });
}
```

**After:**
```typescript
async function getUserWithEmail(userId: string): Promise<User> {
  const user = await db.users.findById(userId);
  if (!user) throw new NotFoundError('User not found');
  if (!user.email) throw new ValidationError('User has no email');
  return user;
}

async function sendWelcomeEmail(userId: string) {
  const user = await getUserWithEmail(userId);

  await emailService.send({
    to: user.email,
    subject: 'Welcome!',
    body: 'Thanks for signing up!',
  });
}

async function sendPasswordResetEmail(userId: string, token: string) {
  const user = await getUserWithEmail(userId);

  await emailService.send({
    to: user.email,
    subject: 'Reset Password',
    body: `Reset link: ${token}`,
  });
}
```

---

## 📖 Complete Example

**See:** [Refactoring Example](../examples/refactoring-example.md) - Complete walkthrough of extracting duplicate email validation logic into a reusable utility.

---

**Remember:** Refactoring is about improving structure, not changing behavior. Test continuously and commit incrementally.
