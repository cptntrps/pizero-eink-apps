# Core Development Principles

These principles guide all development decisions. When faced with ambiguity, return to these fundamentals.

---

## 🎯 Understand Before Acting

**Principle:** Never make changes without understanding the context and impact.

**In Practice:**
- Read the issue/bug report completely
- Explore the codebase to understand existing patterns
- Identify what other code depends on what you're changing
- Ask questions when requirements are unclear
- Consider edge cases and user impact

**Example:**
```
❌ Bad: User reports "login is broken" → immediately edit login.js
✅ Good: Read error details → check logs → explore auth flow → identify root cause → then fix
```

---

## 🧪 Test-Driven Mindset

**Principle:** Tests are not optional—they're how you prove your code works.

**In Practice:**
- Write tests for new features before or during development
- Create reproduction tests for bugs before fixing
- Run tests before committing
- Don't reduce coverage to make tests pass
- Test edge cases, not just happy paths

**Example:**
```
Feature: Add user email validation

1. Write test: expect(validateEmail("invalid")).toBe(false)
2. Write test: expect(validateEmail("user@example.com")).toBe(true)
3. Implement validateEmail() to make tests pass
4. Add edge case tests (empty string, null, special chars)
```

---

## 🔒 Security By Default

**Principle:** Assume all inputs are malicious, all outputs are dangerous.

**In Practice:**
- Validate all user inputs (type, format, length, range)
- Sanitize outputs to prevent XSS
- Use parameterized queries to prevent SQL injection
- Never trust client-side validation alone
- Never log sensitive data
- Use HTTPS in production

**Example:**
```javascript
❌ Bad:
const query = `SELECT * FROM users WHERE id = ${req.params.id}`;

✅ Good:
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [req.params.id]);

❌ Bad:
res.send(`<h1>Welcome ${userName}</h1>`);

✅ Good:
res.send(`<h1>Welcome ${escapeHtml(userName)}</h1>`);
```

---

## 📦 Minimal Scope Changes

**Principle:** Change only what's necessary to accomplish the goal.

**In Practice:**
- Fix the specific bug, don't refactor unrelated code
- Add the requested feature, don't redesign the module
- If you notice other issues, create separate tasks
- Keep commits focused on single logical changes
- Resist the urge to "improve everything while you're there"

**Example:**
```
Task: Fix bug in user profile update

✅ Do: Fix the specific validation issue in updateProfile()
❌ Don't: Also refactor the entire UserController, rename variables,
         reorganize imports, update unrelated functions

(Create separate issues for those improvements)
```

---

## 🔁 Reversible Changes

**Principle:** All changes should be easily undoable if they cause problems.

**In Practice:**
- Use feature flags for risky new features
- Make database migrations reversible (include DOWN migration)
- Keep commits atomic so they can be reverted cleanly
- Deploy incrementally, not all at once
- Keep rollback procedures ready

**Example:**
```javascript
// Migration file
export async function up(db) {
  await db.schema.table('users', (table) => {
    table.string('email_verified_at').nullable();
  });
}

export async function down(db) {
  await db.schema.table('users', (table) => {
    table.dropColumn('email_verified_at');
  });
}
```

---

## 📚 Code is Communication

**Principle:** Write code for humans first, computers second.

**In Practice:**
- Use descriptive variable and function names
- Write comments for "why", not "what"
- Keep functions small and focused
- Maintain consistent style with the codebase
- Prefer clarity over cleverness

**Example:**
```javascript
❌ Bad:
const d = new Date();
const x = d.getTime() + 86400000;

✅ Good:
const now = new Date();
const ONE_DAY_IN_MS = 24 * 60 * 60 * 1000;
const tomorrow = now.getTime() + ONE_DAY_IN_MS;

❌ Bad:
// Increment counter
counter++;

✅ Good:
// Track failed login attempts for rate limiting
failedLoginAttempts++;
```

---

## ⚡ Performance Matters (But Measure First)

**Principle:** Don't optimize prematurely, but don't ignore performance.

**In Practice:**
- Write clear code first, optimize if needed
- Measure before optimizing (profiling, metrics)
- Focus on algorithmic improvements (O(n²) → O(n))
- Avoid obvious anti-patterns (N+1 queries)
- Consider user experience (loading states, pagination)

**Example:**
```javascript
❌ Bad (N+1 query):
const users = await User.findAll();
for (const user of users) {
  user.posts = await Post.findByUserId(user.id);
}

✅ Good (single query):
const users = await User.findAll({
  include: [{ model: Post }]
});
```

---

## 🛡️ Fail Gracefully

**Principle:** Expect failures and handle them elegantly.

**In Practice:**
- Wrap external calls in try-catch
- Validate inputs before processing
- Provide meaningful error messages
- Log errors with context for debugging
- Don't expose internal errors to users
- Have fallback strategies

**Example:**
```javascript
❌ Bad:
async function getUser(id) {
  const user = await db.users.findById(id);
  return user;
}

✅ Good:
async function getUser(id) {
  try {
    if (!id || typeof id !== 'string') {
      throw new ValidationError('Invalid user ID');
    }

    const user = await db.users.findById(id);

    if (!user) {
      throw new NotFoundError(`User ${id} not found`);
    }

    return user;
  } catch (error) {
    logger.error('Failed to fetch user', { id, error });
    throw error;
  }
}
```

---

## 🔄 Follow Existing Patterns

**Principle:** Consistency is more important than personal preference.

**In Practice:**
- Match the existing code style
- Use the same libraries/patterns as the rest of the codebase
- If the project uses TypeScript strictly, don't use `any`
- If APIs use camelCase, don't introduce snake_case
- When in doubt, find similar code and follow that pattern

**Example:**
```
Project uses:
- React functional components with hooks
- CSS Modules for styling
- React Query for data fetching

❌ Don't introduce: Class components, styled-components, custom fetch hooks
✅ Do: Follow existing patterns for consistency
```

---

## 🎓 Leave Code Better Than You Found It

**Principle:** Make small improvements as you work.

**In Practice:**
- Fix obvious typos you encounter
- Add missing type definitions
- Remove unused imports/variables
- Add missing error handling
- Improve naming when obvious
- BUT: Keep improvements minimal and relevant

**Example:**
```
Task: Fix bug in calculateTotal()

While fixing, you notice:
✅ Do: Remove unused 'discount' variable in same function
✅ Do: Fix typo in comment
✅ Do: Add missing type for parameter
❌ Don't: Refactor entire pricing module
❌ Don't: Rename all variables in the file
```

---

## 🤝 Collaborate, Don't Dictate

**Principle:** You're a team member, not the sole decision-maker.

**In Practice:**
- Ask questions when requirements are unclear
- Present options with trade-offs, not just your preference
- Respect existing architectural decisions
- Explain your reasoning when suggesting changes
- Be open to feedback and alternative approaches

**Example:**
```
"I found 3 approaches to fix the performance issue:

1. Add database index (fast, but increases storage)
2. Add caching layer (fast reads, complex invalidation)
3. Optimize query (no infra change, but might not be enough)

I recommend Option 1 for this use case because...
What do you think?"
```

---

## 🎯 Done Means Tested and Documented

**Principle:** A feature isn't done until it's tested, documented, and deployed.

**In Practice:**
- Write tests before marking work complete
- Update relevant documentation
- Ensure CI passes
- Verify the feature works end-to-end
- Update changelog if needed
- Don't consider partial implementations "done"

**Checklist:**
```
✅ Feature implemented
✅ Tests written and passing
✅ Documentation updated
✅ Code reviewed (or ready for review)
✅ No linting errors
✅ No security vulnerabilities introduced
✅ Deployed to staging/preview
```

---

## 📊 Summary: The Principle Hierarchy

When principles conflict, use this priority order:

1. **Security** - Never compromise user safety
2. **Correctness** - Code must work as specified
3. **Reversibility** - Must be able to undo changes
4. **Testability** - Must be verifiable
5. **Clarity** - Must be understandable
6. **Performance** - Must be acceptably fast
7. **Elegance** - Nice to have, but not at the cost of above

**Remember:** Principles are guidelines for judgment, not rigid rules. The non-negotiable rules in the main instructions take absolute precedence.
