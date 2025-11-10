# Data Validation & Sanitization

Protecting against invalid and malicious input.

---

## 🚨 Critical Rules

- ✋ **ALWAYS validate user input server-side** (never trust client)
- ✋ **ALWAYS sanitize before storing or displaying**
- ✋ **ALWAYS validate type, format, length, and range**
- ✋ **REJECT unknown fields** (prevent injection)

---

## 📋 Validation Layers

### 1. Schema Validation

Use validation libraries to enforce data structure:

**TypeScript + Zod:**
```typescript
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8).max(100),
  age: z.number().int().min(13).max(120),
  website: z.string().url().optional(),
  role: z.enum(['user', 'admin', 'moderator']),
});

// Validate and parse
try {
  const data = userSchema.parse(req.body);
  // data is now typed and validated
} catch (error) {
  if (error instanceof z.ZodError) {
    return res.status(400).json({ errors: error.errors });
  }
}
```

**Python + Pydantic:**
```python
from pydantic import BaseModel, EmailStr, validator

class User(BaseModel):
    email: EmailStr
    password: str
    age: int
    website: Optional[str] = None

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('age')
    def age_range(cls, v):
        if not 13 <= v <= 120:
            raise ValueError('Age must be between 13 and 120')
        return v

# Usage
try:
    user = User(**request_data)
except ValidationError as e:
    return {'errors': e.errors()}, 400
```

---

### 2. Input Sanitization

**Remove dangerous characters:**

```typescript
import validator from 'validator';

// Email
const email = validator.normalizeEmail(input.email);
const isValidEmail = validator.isEmail(email);

// URL
const url = validator.trim(input.url);
const isValidUrl = validator.isURL(url);

// String
const name = validator.escape(input.name);  // Escapes HTML
const cleanName = validator.trim(name);
```

**HTML Sanitization:**
```typescript
import DOMPurify from 'isomorphic-dompurify';

// User-generated HTML (dangerous!)
const userHtml = '<img src=x onerror=alert(1)>';

// Sanitized (safe)
const safeHtml = DOMPurify.sanitize(userHtml);
// Result: '<img src="x">'
```

---

### 3. Type Validation

**JavaScript (runtime checking):**
```typescript
function validateUser(data: unknown) {
  if (typeof data !== 'object' || data === null) {
    throw new Error('Invalid input: must be an object');
  }

  if (!('email' in data) || typeof data.email !== 'string') {
    throw new Error('Invalid email');
  }

  if (!('age' in data) || typeof data.age !== 'number') {
    throw new Error('Invalid age');
  }

  return data as User;
}
```

**Better: Use Zod or similar for runtime type checking**

---

## 🛡️ Common Validation Patterns

### Email Validation

```typescript
const emailSchema = z
  .string()
  .email('Invalid email format')
  .max(255, 'Email too long')
  .toLowerCase()
  .transform(email => email.trim());

// Usage
const email = emailSchema.parse('  User@Example.COM  ');
// Result: 'user@example.com'
```

---

### Password Validation

```typescript
const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(100, 'Password too long')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^A-Za-z0-9]/, 'Must contain special character');
```

---

### URL Validation

```typescript
const urlSchema = z
  .string()
  .url('Invalid URL')
  .regex(/^https:/, 'Must use HTTPS')
  .max(2048, 'URL too long');
```

---

### Date Validation

```typescript
const dateSchema = z
  .string()
  .or(z.date())
  .transform(val => new Date(val))
  .refine(date => !isNaN(date.getTime()), 'Invalid date')
  .refine(date => date <= new Date(), 'Date cannot be in future');
```

---

### File Upload Validation

```typescript
const fileSchema = z.object({
  filename: z.string().max(255),
  mimetype: z.enum(['image/jpeg', 'image/png', 'image/webp']),
  size: z.number().max(5 * 1024 * 1024, 'File must be under 5MB'),
});

// Additional validation
function validateFileContent(file: Buffer): boolean {
  // Check magic bytes (file signature)
  const jpegSignature = Buffer.from([0xFF, 0xD8, 0xFF]);
  const pngSignature = Buffer.from([0x89, 0x50, 0x4E, 0x47]);

  return file.subarray(0, 3).equals(jpegSignature) ||
         file.subarray(0, 4).equals(pngSignature);
}
```

---

## 🔍 Advanced Validation Patterns

### Conditional Validation

```typescript
const orderSchema = z.object({
  type: z.enum(['pickup', 'delivery']),
  address: z.string().optional(),
}).refine(
  data => {
    // Address required for delivery
    if (data.type === 'delivery') {
      return data.address && data.address.length > 0;
    }
    return true;
  },
  { message: 'Address required for delivery orders' }
);
```

---

### Cross-Field Validation

```typescript
const passwordChangeSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(
  data => data.password === data.confirmPassword,
  { message: 'Passwords do not match', path: ['confirmPassword'] }
);
```

---

### Custom Validators

```typescript
const usernameSchema = z
  .string()
  .min(3)
  .max(20)
  .regex(/^[a-zA-Z0-9_]+$/, 'Only letters, numbers, and underscores')
  .refine(
    async (username) => {
      // Check if username is available
      const exists = await db.users.exists({ username });
      return !exists;
    },
    { message: 'Username already taken' }
  );
```

---

### Array Validation

```typescript
const tagsSchema = z
  .array(z.string())
  .min(1, 'At least one tag required')
  .max(5, 'Maximum 5 tags allowed')
  .refine(
    tags => new Set(tags).size === tags.length,
    { message: 'Duplicate tags not allowed' }
  );
```

---

## 🚫 Reject Unknown Fields

**Prevent parameter pollution:**

```typescript
// ❌ Bad: Accepts any fields
const user = await db.users.create(req.body);
// Attacker can send: { email: '...', role: 'admin' }

// ✅ Good: Only accept known fields
const schema = z.object({
  email: z.string().email(),
  password: z.string(),
}).strict();  // Reject unknown fields

const data = schema.parse(req.body);
const user = await db.users.create(data);
```

---

## 📊 Validation in Different Layers

### 1. API Route Level

```typescript
// routes/users.ts
import { validateRequest } from '../middleware/validation';
import { userSchema } from '../schemas/user';

router.post(
  '/users',
  validateRequest(userSchema),  // Validation middleware
  async (req, res) => {
    // req.body is now validated
    const user = await userService.create(req.body);
    res.status(201).json(user);
  }
);
```

---

### 2. Middleware

```typescript
// middleware/validation.ts
import { AnyZodObject } from 'zod';

export function validateRequest(schema: AnyZodObject) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = await schema.parseAsync(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        });
      }
      next(error);
    }
  };
}
```

---

### 3. Service Level

```typescript
// services/userService.ts
export async function createUser(data: unknown) {
  // Validate at service level too (defense in depth)
  const validatedData = userSchema.parse(data);

  // Business logic validation
  const existingUser = await db.users.findByEmail(validatedData.email);
  if (existingUser) {
    throw new Error('Email already registered');
  }

  return db.users.create(validatedData);
}
```

---

## ⚠️ Common Validation Mistakes

### Trusting Client-Side Validation

```typescript
// ❌ Bad: Only client-side validation
// Client can bypass this!

// ✅ Good: Server-side validation required
router.post('/users', validateRequest(userSchema), handler);
```

---

### Not Validating Length

```typescript
// ❌ Bad: No length limit
const name = z.string();

// Attacker sends 10MB string → DoS

// ✅ Good: Reasonable limits
const name = z.string().min(1).max(100);
```

---

### Not Checking Data Types

```typescript
// ❌ Bad: Type coercion issues
const age = parseInt(req.body.age);  // NaN if invalid

// ✅ Good: Type validation
const age = z.number().int().min(0).max(120).parse(req.body.age);
```

---

### Weak Regex Patterns

```typescript
// ❌ Bad: ReDoS vulnerability
const emailRegex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z]{2,4})+$/;
// Input: "a@" + "a" * 50000 → hangs

// ✅ Good: Use tested library
import validator from 'validator';
validator.isEmail(email);

// Or use Zod
z.string().email();
```

---

## 📋 Validation Checklist

### For Every User Input
- [ ] Type validated (string, number, boolean, etc.)
- [ ] Format validated (email, URL, date, etc.)
- [ ] Length/size validated (min/max)
- [ ] Range validated (for numbers)
- [ ] Allowed values validated (enums)
- [ ] Required fields enforced
- [ ] Unknown fields rejected
- [ ] Sanitized before use/storage

### Security Checks
- [ ] No SQL injection vectors
- [ ] No XSS vectors
- [ ] No path traversal characters
- [ ] No command injection vectors
- [ ] File uploads checked (type, size, content)
- [ ] Rate limiting applied

### Business Logic
- [ ] Cross-field validation
- [ ] Business rules enforced
- [ ] Uniqueness constraints checked
- [ ] Permissions verified

---

## 🎯 Example: Complete API Endpoint

```typescript
import { z } from 'zod';
import { Router } from 'express';
import { authenticate } from '../middleware/auth';

const router = Router();

// Schema definition
const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  body: z.string().min(1).max(10000),
  tags: z.array(z.string()).max(5).optional(),
  published: z.boolean().default(false),
});

// Route with validation
router.post(
  '/posts',
  authenticate,  // Must be authenticated
  async (req, res, next) => {
    try {
      // Validate input
      const data = createPostSchema.parse(req.body);

      // Sanitize HTML content
      const safeBody = DOMPurify.sanitize(data.body);

      // Create post
      const post = await db.posts.create({
        ...data,
        body: safeBody,
        authorId: req.user.id,
      });

      res.status(201).json(post);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ errors: error.errors });
      }
      next(error);
    }
  }
);

export default router;
```

---

**Remember:** Validation is your first line of defense. Validate early, validate thoroughly, and never trust user input.
