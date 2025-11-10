# Security Checklist

Essential security practices for web applications, APIs, and mobile apps.

---

## 🚨 Critical Security Rules (Never Break)

- ✋ **NEVER commit secrets, API keys, or passwords**
- ✋ **ALWAYS validate and sanitize user inputs**
- ✋ **ALWAYS use parameterized queries** (prevent SQL injection)
- ✋ **ALWAYS escape output** (prevent XSS)
- ✋ **ALWAYS require authentication** for protected resources
- ✋ **ALWAYS use HTTPS** in production

---

## 🔐 Authentication & Authorization

### Authentication
- [ ] Passwords hashed with bcrypt/argon2 (never plaintext)
- [ ] Minimum password requirements enforced (8+ characters)
- [ ] Session tokens/JWTs properly secured
- [ ] Tokens have reasonable expiration times
- [ ] Refresh token rotation implemented
- [ ] Failed login attempts rate-limited
- [ ] Account lockout after N failed attempts
- [ ] Multi-factor authentication available (if applicable)

**Example:**
```typescript
✅ Good: Hash passwords
import bcrypt from 'bcrypt';

const hashedPassword = await bcrypt.hash(password, 10);
await db.users.create({ email, password: hashedPassword });

❌ Bad: Plaintext passwords
await db.users.create({ email, password }); // NEVER!
```

### Authorization
- [ ] Users can only access their own data
- [ ] Role-based access control (RBAC) implemented
- [ ] Permission checks on all protected endpoints
- [ ] Authorization checked server-side (never trust client)

**Example:**
```typescript
✅ Good: Verify ownership
router.get('/api/posts/:id', authenticate, async (req, res) => {
  const post = await db.posts.findById(req.params.id);

  if (post.authorId !== req.user.id) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  res.json(post);
});

❌ Bad: No ownership check
router.get('/api/posts/:id', async (req, res) => {
  const post = await db.posts.findById(req.params.id);
  res.json(post); // Anyone can access any post!
});
```

---

## 💉 Injection Prevention

### SQL Injection
- [ ] Use parameterized queries or ORM
- [ ] Never concatenate user input into SQL
- [ ] Validate input types and formats

**Example:**
```typescript
❌ CRITICAL: SQL Injection vulnerability
const query = `SELECT * FROM users WHERE email = '${email}'`;
// Attacker can use: email = ' OR '1'='1

✅ Good: Parameterized query
const query = 'SELECT * FROM users WHERE email = ?';
const user = await db.query(query, [email]);

✅ Good: ORM
const user = await db.users.findOne({ where: { email } });
```

### NoSQL Injection
- [ ] Validate object structure
- [ ] Use schema validation (Joi, Zod)
- [ ] Sanitize inputs for MongoDB operators

**Example:**
```typescript
❌ Bad: NoSQL injection risk
const user = await db.users.findOne({ email: req.body.email });
// Attacker can send: { email: { $ne: null } }

✅ Good: Validate input
const schema = z.object({
  email: z.string().email()
});
const { email } = schema.parse(req.body);
const user = await db.users.findOne({ email });
```

### Command Injection
- [ ] Never execute shell commands with user input
- [ ] If unavoidable, use allowlists and strict validation
- [ ] Use libraries instead of shell commands when possible

---

## 🕸️ Cross-Site Scripting (XSS) Prevention

- [ ] Escape all user-generated content in HTML
- [ ] Use framework auto-escaping (React, Vue, etc.)
- [ ] Set Content-Security-Policy headers
- [ ] Sanitize HTML if user input allows formatting
- [ ] Never use `dangerouslySetInnerHTML` with user content

**Example:**
```tsx
❌ CRITICAL: XSS vulnerability
<div dangerouslySetInnerHTML={{ __html: userBio }} />
// Attacker can inject: <script>steal cookies</script>

✅ Good: Escaped by default
<div>{userBio}</div> // React escapes automatically

✅ Good: Sanitize if HTML needed
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userBio) }} />
```

---

## 🔑 Secrets Management

- [ ] All secrets in environment variables (never in code)
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` provided (without actual secrets)
- [ ] Production secrets in secure vault (AWS Secrets, Azure Key Vault)
- [ ] API keys rotated regularly
- [ ] No secrets in client-side code
- [ ] No secrets in logs

**Example:**
```typescript
❌ CRITICAL: Hardcoded secret
const apiKey = 'sk-1234567890abcdef';

✅ Good: Environment variable
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error('API_KEY not configured');

// .env.example (committed)
API_KEY=your_api_key_here

// .env (NOT committed)
API_KEY=sk-real-secret-key
```

---

## 🛡️ Input Validation

- [ ] Validate all user inputs server-side
- [ ] Check type, format, length, range
- [ ] Use schema validation libraries (Zod, Joi, Yup)
- [ ] Reject unexpected fields
- [ ] Validate file uploads (type, size, content)

**Example:**
```typescript
✅ Good: Comprehensive validation
import { z } from 'zod';

const schema = z.object({
  email: z.string().email().max(255),
  age: z.number().int().min(13).max(120),
  website: z.string().url().optional(),
});

router.post('/api/profile', async (req, res) => {
  try {
    const data = schema.parse(req.body);
    // Process validated data
  } catch (error) {
    return res.status(400).json({ error: error.errors });
  }
});
```

---

## 🌐 API Security

- [ ] Rate limiting implemented
- [ ] CORS configured properly (not `*` in production)
- [ ] CSRF protection for state-changing operations
- [ ] API keys/tokens in headers (not in URL)
- [ ] Sensitive data not in URL parameters
- [ ] Proper HTTP status codes for errors
- [ ] Error messages don't leak internal info

**Example:**
```typescript
// Rate limiting
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests, please try again later'
});

app.use('/api/', limiter);

// CORS
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true
}));
```

---

## 📁 File Upload Security

- [ ] Validate file type (check magic bytes, not just extension)
- [ ] Limit file size
- [ ] Store files outside web root
- [ ] Generate random filenames (prevent path traversal)
- [ ] Scan uploads for malware (if possible)
- [ ] Set restrictive file permissions

**Example:**
```typescript
const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});
```

---

## 🔒 Data Protection

- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (HTTPS/TLS)
- [ ] Personal data minimized (collect only what's needed)
- [ ] Passwords never logged
- [ ] PII (Personally Identifiable Information) protected
- [ ] Data retention policies implemented
- [ ] Secure data deletion procedures

**Example:**
```typescript
// Don't log sensitive data
❌ Bad:
logger.info('User login', { email, password }); // NEVER!

✅ Good:
logger.info('User login attempt', { email }); // OK, but not password

// Don't return sensitive data
❌ Bad:
res.json(user); // Includes password hash!

✅ Good:
const { password, ...safeUser } = user;
res.json(safeUser);
```

---

## 🌐 HTTPS/TLS

- [ ] HTTPS enforced in production
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header set
- [ ] Valid SSL certificate
- [ ] TLS 1.2+ only (no SSLv3, TLS 1.0/1.1)
- [ ] Secure cookies: `Secure` and `HttpOnly` flags

**Example:**
```typescript
// Secure cookies
res.cookie('sessionId', token, {
  httpOnly: true,    // Prevent JavaScript access
  secure: true,      // HTTPS only
  sameSite: 'strict', // CSRF protection
  maxAge: 3600000    // 1 hour
});

// HSTS header
app.use((req, res, next) => {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  next();
});
```

---

## 🚨 Error Handling

- [ ] Errors logged with sufficient context
- [ ] Error messages don't leak internal info
- [ ] Stack traces not exposed to users
- [ ] Generic error messages to users
- [ ] Detailed errors in logs only

**Example:**
```typescript
❌ Bad: Exposes internal details
catch (error) {
  res.status(500).json({
    error: error.message,
    stack: error.stack,
    query: sqlQuery
  });
}

✅ Good: Generic to user, detailed in logs
catch (error) {
  logger.error('Database query failed', {
    error: error.message,
    stack: error.stack,
    userId: req.user?.id
  });

  res.status(500).json({
    error: 'An error occurred. Please try again later.'
  });
}
```

---

## 📦 Dependencies

- [ ] Dependencies kept up-to-date
- [ ] Security advisories monitored
- [ ] `npm audit` run regularly
- [ ] Known vulnerabilities addressed
- [ ] Minimal dependencies (reduce attack surface)
- [ ] Dependencies from trusted sources only

**Example:**
```bash
# Check for vulnerabilities
npm audit

# Fix automatically (if possible)
npm audit fix

# For high/critical only
npm audit fix --audit-level=high
```

---

## 🔍 Security Headers

```typescript
// Security headers middleware
app.use((req, res, next) => {
  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');

  // Prevent MIME sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // XSS protection (legacy browsers)
  res.setHeader('X-XSS-Protection', '1; mode=block');

  // Content Security Policy
  res.setHeader('Content-Security-Policy', "default-src 'self'");

  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  next();
});
```

---

## 📋 Pre-Deployment Security Checklist

- [ ] All secrets in environment variables
- [ ] No hardcoded credentials in code
- [ ] HTTPS enforced
- [ ] Authentication required on protected routes
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified
- [ ] XSS prevention verified
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Security headers set
- [ ] Dependencies scanned for vulnerabilities
- [ ] Error messages don't leak info
- [ ] Logging doesn't include sensitive data

---

## 🎯 OWASP Top 10 (2021)

1. **Broken Access Control** ✓ Implement proper authorization
2. **Cryptographic Failures** ✓ Encrypt sensitive data, use HTTPS
3. **Injection** ✓ Use parameterized queries, validate inputs
4. **Insecure Design** ✓ Security requirements in design phase
5. **Security Misconfiguration** ✓ Secure defaults, remove unnecessary features
6. **Vulnerable Components** ✓ Keep dependencies updated
7. **Identification & Auth Failures** ✓ Strong authentication, rate limiting
8. **Software & Data Integrity Failures** ✓ Verify integrity of updates/data
9. **Security Logging & Monitoring** ✓ Log security events, monitor for attacks
10. **Server-Side Request Forgery (SSRF)** ✓ Validate and sanitize URLs

---

**Remember:** Security is not optional. Every feature must be built with security in mind from the start.
