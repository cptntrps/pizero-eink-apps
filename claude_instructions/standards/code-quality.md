# Code Quality Standards

Standards for maintainable, readable, and high-quality code.

---

## 🚨 Non-Negotiables

- ✋ **Zero linting errors** (warnings can be justified)
- ✋ **Type checking must pass** (TypeScript strict mode, mypy, etc.)
- ✋ **No debug code in commits** (console.log, debugger, print statements)
- ✋ **Follow existing code style** (consistency over personal preference)

---

## 🎨 Code Style

### Linting

**Always pass linting:**
```bash
npm run lint

# Auto-fix when possible
npm run lint -- --fix
```

**Common linters:**
- **JavaScript/TypeScript:** ESLint
- **Python:** Pylint, Flake8, Black
- **Go:** golint, gofmt
- **Rust:** cargo clippy

**Configuration:**
```json
// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

---

### Formatting

**Use automated formatters:**
- **JavaScript/TypeScript:** Prettier
- **Python:** Black
- **Go:** gofmt
- **Rust:** rustfmt

**Let tools handle formatting:**
```bash
# Format all files
npm run format

# Check formatting without changing
npm run format -- --check
```

---

## 📝 Naming Conventions

### Variables and Functions

**Use descriptive names:**
```typescript
❌ Bad: Unclear
const d = new Date();
const x = getUserData(123);
function process(a, b) { }

✅ Good: Clear intent
const currentDate = new Date();
const userData = getUserData(userId);
function calculateTotalPrice(items, discountRate) { }
```

**Naming patterns:**
- **Boolean:** `isActive`, `hasPermission`, `canEdit`
- **Functions:** Verb-noun: `getUser`, `calculateTotal`, `validateEmail`
- **Constants:** `UPPER_SNAKE_CASE` or `camelCase` (follow project style)

---

### Files and Modules

```
✅ Good naming:
userService.ts
emailValidation.ts
OrderController.ts
useAuth.tsx (React hook)

❌ Bad naming:
utils.ts (too vague)
stuff.ts
temp.ts
```

---

## 🏗️ Code Organization

### Function Size

**Keep functions focused and small:**
```typescript
❌ Bad: Too long (50+ lines)
function processOrder(order) {
  // Validation (10 lines)
  // Calculation (15 lines)
  // Database operations (10 lines)
  // Email sending (10 lines)
  // Logging (5 lines)
}

✅ Good: Focused functions
function processOrder(order) {
  validateOrder(order);
  const total = calculateOrderTotal(order);
  await saveOrder(order, total);
  await sendOrderConfirmation(order);
  logOrderProcessed(order);
}
```

**Rule of thumb:** If function doesn't fit on screen, it's probably too long.

---

### Complexity

**Keep cyclomatic complexity low (< 10):**

```typescript
❌ Bad: High complexity (15)
function calculatePrice(item, user) {
  if (item.onSale) {
    if (user.isPremium) {
      if (item.category === 'electronics') {
        if (user.hasDiscount) {
          // Nested logic continues...
        }
      }
    }
  }
}

✅ Good: Lower complexity (5)
function calculatePrice(item, user) {
  let price = item.basePrice;

  if (item.onSale) price *= 0.8;
  if (user.isPremium) price *= 0.9;
  if (isEligibleForElectronicsDiscount(item, user)) price *= 0.85;

  return price;
}

function isEligibleForElectronicsDiscount(item, user) {
  return item.category === 'electronics' && user.hasDiscount;
}
```

---

### DRY Principle (Don't Repeat Yourself)

**Extract duplicate logic:**

```typescript
❌ Bad: Duplication
function sendWelcomeEmail(user) {
  if (!user.email || !user.email.includes('@')) {
    throw new Error('Invalid email');
  }
  // send email
}

function sendResetEmail(user) {
  if (!user.email || !user.email.includes('@')) {
    throw new Error('Invalid email');
  }
  // send email
}

✅ Good: Extract common logic
function validateEmail(email) {
  if (!email || !email.includes('@')) {
    throw new ValidationError('Invalid email');
  }
}

function sendWelcomeEmail(user) {
  validateEmail(user.email);
  // send email
}

function sendResetEmail(user) {
  validateEmail(user.email);
  // send email
}
```

---

## 📖 Comments and Documentation

### When to Comment

**DO comment:**
- **Why**, not what: Explain reasoning
- Complex algorithms
- Non-obvious workarounds
- Business rules
- Public APIs

**DON'T comment:**
- Obvious code
- Instead of good naming
- Instead of refactoring bad code

**Examples:**

```typescript
❌ Bad: Stating the obvious
// Increment counter
counter++;

// Get user by ID
const user = getUserById(id);

✅ Good: Explaining why
// Retry up to 3 times due to API rate limiting
for (let i = 0; i < 3; i++) {
  try {
    return await externalAPI.call();
  } catch (error) {
    if (i === 2) throw error;
    await sleep(1000 * (i + 1));
  }
}

// Using legacy endpoint because v2 doesn't support bulk operations yet
// TODO: Migrate to v2 API when bulk support is added (Q2 2024)
const response = await api.v1.bulkUpdate(items);
```

---

### JSDoc / Function Documentation

**Document public APIs:**

```typescript
/**
 * Uploads a file to cloud storage and returns the URL.
 *
 * @param file - The file to upload
 * @param path - Storage path (e.g., "uploads/images")
 * @param options - Upload options
 * @returns Promise resolving to the file URL
 * @throws {ValidationError} If file type is invalid
 * @throws {StorageError} If upload fails
 *
 * @example
 * const url = await uploadFile(file, 'uploads/avatars', { public: true });
 */
async function uploadFile(
  file: File,
  path: string,
  options: UploadOptions = {}
): Promise<string> {
  // Implementation
}
```

---

## 🔧 TypeScript Best Practices

### Use Strict Mode

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

### Avoid `any`

```typescript
❌ Bad: Using any
function processData(data: any) {
  return data.map(item => item.value);
}

✅ Good: Proper types
interface DataItem {
  value: number;
  label: string;
}

function processData(data: DataItem[]): number[] {
  return data.map(item => item.value);
}
```

### Use Type Inference

```typescript
❌ Unnecessary: Type already inferred
const count: number = 5;
const name: string = 'John';

✅ Good: Let TypeScript infer
const count = 5;
const name = 'John';

✅ Explicit when helpful:
const users: User[] = []; // Empty array needs type
const result: Promise<User> = fetchUser(); // Clarifies async return
```

---

## ⚡ Performance Considerations

### Avoid Obvious Inefficiencies

```typescript
❌ Bad: N+1 query
const users = await db.users.findAll();
for (const user of users) {
  user.posts = await db.posts.findByUserId(user.id); // N queries!
}

✅ Good: Single query with join
const users = await db.users.findAll({
  include: [{ model: Post }]
});

❌ Bad: Unnecessary re-renders
function Component({ items }) {
  const processed = items.map(expensiveOperation); // Every render!
  return <List data={processed} />;
}

✅ Good: Memoize expensive operations
function Component({ items }) {
  const processed = useMemo(
    () => items.map(expensiveOperation),
    [items]
  );
  return <List data={processed} />;
}
```

---

## 🛡️ Error Handling

### Fail Fast and Explicitly

```typescript
❌ Bad: Silent failures
function getUser(id) {
  const user = db.users.find(id);
  return user; // Returns undefined if not found
}

✅ Good: Explicit errors
function getUser(id: string): User {
  const user = db.users.find(id);
  if (!user) {
    throw new NotFoundError(`User ${id} not found`);
  }
  return user;
}
```

### Provide Helpful Error Messages

```typescript
❌ Bad: Generic errors
throw new Error('Invalid input');

✅ Good: Specific errors
throw new ValidationError('Email must be in format: user@example.com');

❌ Bad: No context
logger.error('Failed');

✅ Good: Context for debugging
logger.error('Failed to create user', {
  email: user.email,
  error: error.message,
  stack: error.stack
});
```

---

## 📊 Code Quality Checklist

### Before Committing
- [ ] Linting passes (`npm run lint`)
- [ ] Type checking passes (`npm run typecheck`)
- [ ] No console.log or debug code
- [ ] No commented-out code
- [ ] No unused imports/variables
- [ ] Functions are focused (< 50 lines)
- [ ] Complexity is reasonable (< 10)
- [ ] No code duplication
- [ ] Meaningful variable names
- [ ] Helpful comments where needed
- [ ] Public APIs documented

### Code Review Self-Check
- [ ] Would I understand this in 6 months?
- [ ] Is it consistent with the codebase?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Is performance acceptable?
- [ ] Are there security implications?

---

## 🎯 Examples

### Example 1: Refactoring for Quality

**Before:**
```typescript
function p(d) {
  let t = 0;
  for (let i = 0; i < d.length; i++) {
    if (d[i].t === 'a') {
      t += d[i].p * 0.9;
    } else {
      t += d[i].p;
    }
  }
  return t;
}
```

**After:**
```typescript
/**
 * Calculates total price with discounts applied.
 * Type 'a' items receive 10% discount.
 */
function calculateTotalPrice(items: OrderItem[]): number {
  return items.reduce((total, item) => {
    const discount = item.type === 'a' ? 0.9 : 1;
    return total + (item.price * discount);
  }, 0);
}
```

**Improvements:**
- Descriptive names
- Type annotations
- Documentation
- Modern array methods
- Clear logic

---

### Example 2: Simplifying Complexity

**Before:**
```typescript
function canAccess(user, resource) {
  if (user) {
    if (user.isActive) {
      if (resource.isPublic) {
        return true;
      } else {
        if (user.role === 'admin') {
          return true;
        } else if (resource.ownerId === user.id) {
          return true;
        } else {
          return false;
        }
      }
    }
  }
  return false;
}
```

**After:**
```typescript
function canAccess(user: User | null, resource: Resource): boolean {
  // No user or inactive user can't access anything
  if (!user || !user.isActive) {
    return false;
  }

  // Public resources are accessible to all active users
  if (resource.isPublic) {
    return true;
  }

  // Private resources accessible to admins or owners
  return user.role === 'admin' || resource.ownerId === user.id;
}
```

**Improvements:**
- Reduced nesting (easier to read)
- Comments explain logic
- Early returns simplify flow
- Type safety

---

**Remember:** Code is read far more than it's written. Optimize for readability and maintainability.
