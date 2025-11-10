# Meta Modes

Operational modes that modify Claude's behavior for specific contexts.

---

## 🎯 What Are Meta Modes?

Meta modes are **session-level configurations** that adjust how Claude applies the instruction system. Activate a mode at the start of a session to change behavior, verbosity, and decision-making patterns.

**Default:** If no mode is specified, Claude operates in **Standard Mode** - balanced approach following all instructions normally.

---

## 📋 Available Modes

### 🔍 EVALUATION MODE

**Purpose:** Testing and validating the instruction system itself

**When to use:**
- Testing the instruction system
- Validating compliance with standards
- Training new team members on the system
- Debugging unexpected behavior
- Auditing Claude's decision-making

**Activation:**
```
Activate EVALUATION MODE.

Follow all instructions from claude_instructions.md and provide detailed reporting on:
- Which workflow/principle you're following
- Why you made each autonomy decision
- Compliance with non-negotiables
- Citations to specific instruction sections
```

**Behavior Changes:**

| Aspect | Standard Mode | Evaluation Mode |
|--------|---------------|-----------------|
| Verbosity | Concise | Detailed with citations |
| Workflow reporting | Implicit | Explicit references |
| Autonomy decisions | Executed | Explained before execution |
| Non-negotiable checks | Silent unless violated | Always reported |
| Metrics | On request | Automatic reporting |

**Example Output:**
```
[EVAL] Workflow: workflows/bug-fix.md
[EVAL] Step 2: "Locate the Issue" - Using Grep to find error message
[EVAL] Autonomy: MEDIUM - Refactoring (will explain approach first)
[EVAL] Non-Negotiable Check:
  ✓ Tests passing (23/23)
  ✓ Coverage: 78% (min: 70%)
  ✓ No secrets detected
  ✓ Linting: 0 errors
[EVAL] Citation: standards/testing-standards.md - "Minimum 70% coverage"
[EVAL] Proceeding with fix...
```

**Deactivation:**
```
Deactivate EVALUATION MODE. Return to standard mode.
```

---

### 🐛 DEBUG MODE

**Purpose:** Understanding Claude's reasoning and troubleshooting

**When to use:**
- Investigating why Claude made a specific decision
- Learning how Claude interprets instructions
- Troubleshooting unexpected behavior
- Understanding tool selection rationale

**Activation:**
```
Activate DEBUG MODE.
Show your reasoning and explain your decisions.
```

**Behavior Changes:**
- Shows internal reasoning process
- Explains why specific tools were chosen
- Surfaces alternative approaches considered
- More verbose error messages with context
- Explains why certain steps were skipped or modified

**Example Output:**
```
[DEBUG] Analyzing request: "Fix the login bug"
[DEBUG] Decision tree:
  - Type: Bug fix → workflows/bug-fix.md
  - Severity: Unknown → Ask for reproduction steps
  - Tool choice: Need to find code → Grep vs Task
  - Chose Grep because: Specific function name known
[DEBUG] Autonomy level: HIGH (bug fixes are well-defined)
[DEBUG] Proceeding with Grep search for "login" function...
```

---

### 📚 LEARNING MODE

**Purpose:** Educational explanations and mentoring

**When to use:**
- Training new developers
- Learning best practices
- Understanding design patterns
- Building knowledge of the codebase

**Activation:**
```
Activate LEARNING MODE.
Explain the WHY behind your decisions, not just the WHAT.
```

**Behavior Changes:**
- Explains principles behind decisions
- References documentation and resources
- Points out common pitfalls
- Suggests learning resources
- More patient with basic questions
- Provides examples and analogies

**Example Output:**
```
I'm using parameterized queries here to prevent SQL injection attacks.

Why this matters:
When you concatenate user input into SQL strings, attackers can insert
malicious SQL code. For example:

email = "'; DROP TABLE users; --"
query = f"SELECT * FROM users WHERE email = '{email}'"
// Executes: SELECT * FROM users WHERE email = ''; DROP TABLE users; --'

By using parameterized queries, the database treats user input as DATA,
not CODE, making injection impossible.

Learn more: OWASP SQL Injection Prevention Cheat Sheet
Reference: standards/security-checklist.md - "Always use parameterized queries"
```

---

### ⚡ SPEED MODE

**Purpose:** Maximum efficiency for production work

**When to use:**
- Time-sensitive fixes
- Routine maintenance
- Well-understood tasks
- Production emergencies (with caution)

**Activation:**
```
Activate SPEED MODE.
Minimize communication, maximize efficiency.
```

**Behavior Changes:**
- Minimal explanations (results-focused)
- Batch operations when possible
- Terse but complete communication
- Skip optional verbose steps
- Still enforce all non-negotiables
- Parallel tool usage maximized

**Example Output:**
```
Fixed 12 linting errors in 4 files.
Removed 8 console.logs.
Tests: 45/45 passing.
Coverage: 82%.
Committed: chore: code cleanup
```

---

### 🔒 REVIEW MODE

**Purpose:** Extra caution for critical systems

**When to use:**
- Production database changes
- Security-sensitive code
- Financial/payment systems
- Healthcare/regulated systems
- Compliance-required changes

**Activation:**
```
Activate REVIEW MODE.
Maximum caution - ask before all changes, show full context.
```

**Behavior Changes:**
- Asks before ALL changes (even linting)
- Shows full diffs before committing
- Extra security validation passes
- Requires explicit approval for destructive operations
- Documents all assumptions and edge cases
- Suggests peer review for all changes

**Example Output:**
```
⚠️  REVIEW MODE ACTIVE ⚠️

Proposed change: Add 'verified_at' column to users table

Migration preview:
```sql
ALTER TABLE users ADD COLUMN verified_at TIMESTAMP NULL;
UPDATE users SET verified_at = created_at WHERE email_verified = true;
```

Impact analysis:
- Affects: 1.2M rows
- Downtime: None (nullable column)
- Rollback: Available (DOWN migration included)
- Risk: LOW (additive change)

Security check: ✓ No sensitive data exposed
Data integrity: ✓ Preserves existing data
Performance: ✓ No locks required (nullable)

Approve migration? [Y/n]
```

---

### 🚀 PROTOTYPE MODE

**Purpose:** Fast iteration during exploration

**When to use:**
- Prototyping new features
- Exploring architectural options
- Proof of concepts
- Spike work
- A/B testing approaches

**Activation:**
```
Activate PROTOTYPE MODE.
Prioritize speed and exploration over perfection.
```

**Behavior Changes:**
- Relaxed quality gates:
  - Coverage: 50% minimum (vs 70%)
  - Linting warnings: Allowed
  - Type checking: Best effort
- Focus on working code over perfect code
- Mark TODOs for improvements
- **Still enforces:** Security rules, no secrets
- Faster iterations, less ceremony

**Example Output:**
```
[PROTOTYPE] Quick implementation of user search feature

Created:
- API endpoint: /api/search/users (basic implementation)
- Tests: 3 core scenarios (55% coverage - prototype threshold)
- TODO: Add pagination
- TODO: Optimize query performance
- TODO: Add fuzzy matching

⚠️  Prototype quality - not production ready
Ready for review and iteration.
```

---

## 🔄 Mode Combinations

**Can modes be combined?** Yes, selectively:

**Compatible combinations:**
- EVALUATION + LEARNING (detailed explanations with citations)
- DEBUG + REVIEW (understand decisions in critical context)
- SPEED + PROTOTYPE (maximum velocity for exploration)

**Incompatible combinations:**
- SPEED + LEARNING (conflicting verbosity)
- SPEED + DEBUG (conflicting verbosity)
- REVIEW + PROTOTYPE (conflicting rigor)
- REVIEW + SPEED (conflicting caution)

**Example:**
```
Activate EVALUATION MODE and LEARNING MODE.
Explain what you're doing and cite which instructions you're following.
```

---

## 📊 Mode Comparison Matrix

| Feature | Standard | Evaluation | Debug | Learning | Speed | Review | Prototype |
|---------|----------|------------|-------|----------|-------|--------|-----------|
| Verbosity | Medium | High | High | Very High | Low | High | Low |
| Citations | No | Yes | No | Yes | No | Yes | No |
| Explanations | Basic | Detailed | Technical | Educational | Minimal | Detailed | Basic |
| Quality Gates | Full | Full | Full | Full | Full | Extra | Relaxed |
| Autonomy | Adaptive | Explained | Explained | Explained | High | Low | High |
| Min Coverage | 70% | 70% | 70% | 70% | 70% | 80% | 50% |
| Security | Full | Full | Full | Full | Full | Extra | Full |

---

## 🎯 Quick Reference

### Activate a Mode
```
Activate [MODE NAME] MODE.
[Optional: specific instructions]
```

### Deactivate a Mode
```
Deactivate [MODE NAME] MODE.
Return to standard mode.
```

### Check Current Mode
```
What mode are you in?
```

### Switch Modes
```
Deactivate [OLD MODE] MODE.
Activate [NEW MODE] MODE.
```

---

## 📝 Mode Selection Guide

**Choose based on context:**

```
Need to...                          → Use Mode
────────────────────────────────────────────────
Test the instruction system         → EVALUATION
Understand Claude's decisions       → DEBUG
Learn best practices                → LEARNING
Get things done quickly             → SPEED
Work on critical systems            → REVIEW
Explore ideas rapidly               → PROTOTYPE
Normal development work             → STANDARD (default)
```

---

## ⚠️ Important Notes

### Non-Negotiables Always Apply

**Even in PROTOTYPE or SPEED mode, these are NEVER relaxed:**
- ✋ No secrets in code
- ✋ No SQL injection vulnerabilities
- ✋ No XSS vulnerabilities
- ✋ Input validation required
- ✋ All tests must pass before commit
- ✋ Conventional commit format

### Security is Non-Negotiable

All modes maintain full security standards. Prototype mode relaxes *quality* gates (coverage, linting) but NOT security gates.

### Mode Persistence

Modes are **session-scoped**:
- Active for the current conversation only
- Need to be reactivated in new sessions
- Can be changed mid-session

---

## 🧪 Testing Meta Modes

### Evaluation Mode Test
```
Activate EVALUATION MODE.
Fix the linting errors in test.js

Expected: Should cite linting standards and report compliance
```

### Speed Mode Test
```
Activate SPEED MODE.
Fix the linting errors in test.js

Expected: Should fix quickly with minimal explanation
```

### Review Mode Test
```
Activate REVIEW MODE.
Add a new column to the users table

Expected: Should ask for approval and show full migration plan
```

---

**Remember:** Meta modes are tools to optimize Claude's behavior for your specific context. Choose the right mode for the task at hand.
