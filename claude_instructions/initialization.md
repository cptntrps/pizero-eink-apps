# Claude Code Initialization Script

**Version:** 1.1.0

This is an interactive initialization script that guides you through configuring Claude for your development session.

---

## 🚀 Activation Command

When you see this command, execute this initialization sequence:

```
INITIATE CLAUDE CODE INSTRUCTIONS
```

---

## 📋 Initialization Sequence

### Step 1: Welcome & Load Instructions

**Display:**
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🤖 Claude Code Development Assistant v1.3.0          ║
║                                                              ║
║   Principle-Oriented + Multi-Agent Reasoning (AGPF)         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Loading instruction system...
✓ Core principles loaded
✓ Workflows loaded (6)
✓ Quality standards loaded
✓ Project type detection loaded
✓ Advanced guides loaded
✓ Meta modes loaded (6)
✓ AGPF agents loaded (SME, Orchestrator)

Ready to configure your session.
```

---

### Step 2: Detect Project Type

**Actions:**
1. Scan current directory for project indicators
2. Detect project type
3. Report findings

**Display:**
```
🔍 Detecting project type...

Found:
├─ package.json (✓)
├─ next.config.js (✓)
├─ tsconfig.json (✓)
└─ .git directory (✓)

📦 Detected: Next.js Web Application (TypeScript)

Default Commands:
  Test: npm test
  Lint: npm run lint
  Build: npm run build
  Type Check: tsc --noEmit

Quality Gates:
  ✓ Test Coverage: ≥70%
  ✓ Linting: Zero errors
  ✓ Type Checking: Required
  ✓ Security: Full enforcement

Is this correct? [Y/n]
```

**If user says No or provides correction:**
```
What type of project is this?
1. Next.js Web App
2. Express API
3. React Native Mobile
4. Flutter Mobile
5. FastAPI Python
6. Other (specify)

Enter number or description:
```

---

### Step 3: Check for Project Config Override

**Actions:**
1. Look for `.claude/config.json`
2. If found, load and display
3. If not found, offer to create

**Display (if found):**
```
📄 Found project configuration: .claude/config.json

Custom Settings:
✓ Test command: npm run test:ci
✓ Min coverage: 80%
✓ Enforce no warnings: true
✓ Custom instructions: "Check API design guide at docs/api-patterns.md"

Using project-specific configuration.
```

**Display (if not found):**
```
No project configuration found (.claude/config.json).

Using default settings for Next.js projects.

Would you like to create a custom configuration? [y/N]
```

---

### Step 4: Mode Selection

**Display:**
```
🎛️  Select operational mode for this session:

Available Modes:
─────────────────────────────────────────────────────────────

1. 🔍 EVALUATION MODE - Test/validate instruction system
   • Detailed reporting with citations
   • Shows which workflow/principle being followed
   • Reports non-negotiable compliance
   • Perfect for: Testing, validation, auditing

2. ⚡ SPEED MODE - Maximum efficiency
   • Minimal communication, maximum action
   • Enforces all non-negotiables
   • Perfect for: Production work, routine tasks

3. 🔒 REVIEW MODE - Extra caution for critical systems
   • Asks before ALL changes
   • Shows full diffs and impact analysis
   • Perfect for: Production databases, financial systems

4. 📚 LEARNING MODE - Educational explanations
   • Explains WHY, not just WHAT
   • References documentation
   • Perfect for: Training, knowledge building

5. 🐛 DEBUG MODE - Troubleshooting
   • Shows reasoning and decision-making
   • Explains tool choices
   • Perfect for: Understanding Claude's behavior

6. 🚀 PROTOTYPE MODE - Fast exploration
   • Relaxed quality gates (50% coverage OK)
   • Still enforces security
   • Perfect for: POCs, spike work

7. ⚙️  STANDARD MODE - Balanced approach (default)
   • Normal operation, no special mode
   • Adaptive autonomy
   • Perfect for: General development

Enter mode number [1-7] or press Enter for Standard Mode:
```

**After selection:**
```
✓ Mode selected: [MODE NAME]

[Brief description of what this mode does]
```

---

### Step 5: Introduce AGPF (Optional)

**Display:**
```
🤖 Advanced Feature: Multi-Agent Reasoning (AGPF)

You have access to the Asymmetrical Governance & Personality Framework.

AGPF enables multi-agent reasoning where Claude adopts specialized
expert roles (Security SME, Performance SME, Database SME, etc.) that:
• Provide deep technical analysis from multiple perspectives
• Critique and challenge approaches (even yours!)
• Collaborate to find optimal solutions
• Coordinate complex multi-domain tasks

When to use AGPF:
✓ Complex tasks spanning multiple domains (security + performance + UX)
✓ Architectural decisions requiring trade-off analysis
✓ When you want explicit validation from expert perspectives
✓ Critical decisions that need multiple viewpoints

When NOT to use AGPF:
✗ Simple, single-domain tasks
✗ Time-critical work (AGPF is more verbose)
✗ Tasks where speed > thoroughness

Example usage:
  User: "ACTIVATE AGPF"
  User: "Build a secure file upload feature with performance optimization"

  Claude: [ORCHESTRATOR] Activating specialists...
          → [SME: Security] Security requirements
          → [SME: Performance] Optimization strategy
          → [SME: Backend] Implementation

          [Agents collaborate and provide multi-perspective analysis]

Would you like to learn more about AGPF? [y/N]
```

**If user says Yes:**
```
📚 AGPF Overview

AGPF provides two main agent roles:

1. SME (Subject Matter Expert)
   • Deep domain expertise (Security, Performance, Database, etc.)
   • Very low compliance (will critique your requests if problematic)
   • Objective: Technical correctness over convenience
   • Use for: Domain-specific analysis and validation

2. Orchestrator (Task Manager)
   • Coordinates complex multi-domain tasks
   • Delegates to specialized SMEs
   • Manages dependencies and resources
   • Use for: Breaking down complex features

Three Interaction Stances:
• CRITIQUE - Agents challenge unsafe/infeasible requests
• COLLABORATION - Agents negotiate trade-offs together
• ORCHESTRATE - Manager delegates to specialists

Key Principle: Non-Subservient Critique
All agents can push back on requests, even from you. This creates
productive tension leading to better technical decisions.

Activation:
  Simply say "ACTIVATE AGPF" when you need multi-expert analysis.
  Can combine with modes: "ACTIVATE AGPF + REVIEW MODE"

Full documentation: claude_instructions/core/agpf-framework.md

Note: AGPF is completely optional. Standard mode works great for
most tasks. Use AGPF when you specifically want multiple expert
perspectives analyzing your problem.

Press Enter to continue...
```

**If user says No or Enter:**
```
✓ AGPF available if needed (say "ACTIVATE AGPF" anytime)

Continuing with session setup...
```

---

### Step 6: Validate Environment

**Actions:**
1. Check if tests can run
2. Check if linting is configured
3. Check for common issues

**Display:**
```
🔍 Validating development environment...

Checking:
├─ ✓ Node.js installed (v18.17.0)
├─ ✓ npm available
├─ ✓ package.json valid
├─ ✓ Dependencies installed (node_modules exists)
├─ ✓ Test script configured
├─ ✓ Linting configured (ESLint)
├─ ✓ TypeScript configured
└─ ✓ Git repository initialized

Environment: Ready ✓
```

**If issues found:**
```
⚠️  Issues detected:

├─ ✗ node_modules not found
│   Run: npm install
│
└─ ✗ ESLint not configured
    Recommendation: Add ESLint to devDependencies

Would you like me to fix these issues? [Y/n]
```

---

### Step 7: Quick Start Menu

**Display:**
```
🎯 What would you like to do?

Common Tasks:
─────────────────────────────────────────────────────────────

1. 🐛 Fix a bug
2. ✨ Build a new feature
3. 🔧 Refactor code
4. 📝 Review code
5. 🧪 Write tests
6. 🚀 Prepare for deployment
7. 📊 Check code quality
8. 🔍 Explore codebase
9. 💬 Ask me anything
0. 🆓 Free form (I'll describe what I need)

Enter number [0-9] or describe your task:
```

**Based on selection, activate appropriate workflow:**

```
✓ Task selected: Fix a bug

Activating: Bug Fix Workflow (workflows/bug-fix.md)

This workflow will guide you through:
1. Understanding the bug
2. Locating the issue
3. Creating a reproduction test
4. Implementing the fix
5. Verifying the solution
6. Committing with proper message

Non-Negotiable Reminders for Bug Fixes:
✓ Create test that fails before fix
✓ Ensure all tests pass after fix
✓ Maintain test coverage ≥70%
✓ Use conventional commit: "fix(scope): description"

Ready to proceed. What's the bug?
```

---

### Step 8: Session Summary

**Display:**
```
╔══════════════════════════════════════════════════════════════╗
║                    Session Configured                        ║
╚══════════════════════════════════════════════════════════════╝

Configuration Summary:
─────────────────────────────────────────────────────────────

Project Type:    Next.js Web Application
Mode:            EVALUATION MODE
Workflow:        Bug Fix
Environment:     ✓ Ready

Non-Negotiable Rules Active:
✓ No secrets in code
✓ All tests must pass
✓ 70% minimum coverage
✓ Zero linting errors
✓ Type checking required
✓ Conventional commits
✓ No commits to main

Quality Gates:
✓ Tests: npm test
✓ Lint: npm run lint
✓ Build: npm run build
✓ Types: tsc --noEmit

I'm ready to help. What's the bug you'd like me to fix?
```

---

## 🔄 Re-initialization During Session

If you need to change configuration mid-session:

```
RECONFIGURE SESSION
```

This will re-run Steps 4-7 (mode selection, validation, task selection).

---

## 🎛️ Mode Switching During Session

Quick mode switches without full reinitialization:

```
SWITCH MODE: [MODE NAME]
```

Example:
```
SWITCH MODE: DEBUG MODE
```

**Response:**
```
✓ Switched to DEBUG MODE

Now showing:
• Detailed reasoning
• Tool choice explanations
• Alternative approaches considered
• Decision-making process

Previous mode: EVALUATION MODE
```

---

## 📊 Session Status

To check current configuration anytime:

```
SHOW SESSION STATUS
```

**Response:**
```
╔══════════════════════════════════════════════════════════════╗
║                    Current Session Status                    ║
╚══════════════════════════════════════════════════════════════╝

Project:         Next.js Web Application
Mode:            EVALUATION MODE
Active Workflow: Bug Fix (Step 3/6)
Last Action:     Created reproduction test

Non-Negotiables: ✓ All passing
Test Coverage:   78% (✓ above 70%)
Linting:         0 errors, 2 warnings
Type Checking:   ✓ Passing
```

---

## ⚡ Quick Start Commands

For experienced users who don't want the full initialization:

### Quick Standard Mode
```
QUICK START
```
Loads instructions, detects project, uses standard mode, no menu.

### Quick Mode-Specific Start
```
QUICK START: SPEED MODE
```
Loads instructions, detects project, activates specified mode, no menu.

---

## 🛠️ Troubleshooting

### If initialization fails:

```
⚠️  Initialization failed at Step [X]

Error: [Description]

Options:
1. Retry initialization
2. Skip to manual configuration
3. Use default settings

What would you like to do?
```

### If project type can't be detected:

```
⚠️  Could not auto-detect project type

Please specify:
1. Next.js Web App
2. Express API
3. React Native Mobile
4. Flutter Mobile
5. FastAPI Python
6. Custom (I'll configure manually)

Enter number:
```

---

## 📝 Initialization Script Template

**For Claude to execute:**

When user says `INITIATE CLAUDE CODE INSTRUCTIONS`, execute this sequence:

```markdown
1. Display welcome message
2. Load and confirm instruction system loaded
3. Detect project type (scan for indicators)
4. Ask user to confirm or correct
5. Check for .claude/config.json
6. Display available modes
7. Ask user to select mode
8. Introduce AGPF (optional - ask if user wants to learn more)
9. Validate environment (check node, npm, dependencies)
10. Display task menu
11. Ask user what they want to do
12. Activate appropriate workflow
13. Display session summary
14. Begin work
```

**Each step must:**
- Display clear output
- Wait for user confirmation when needed
- Handle errors gracefully
- Provide escape options

---

## 🎯 Success Criteria

Initialization is successful when:

✓ Instructions loaded
✓ Project type identified
✓ Mode selected
✓ Environment validated
✓ User knows what's happening next
✓ Appropriate workflow activated
✓ All non-negotiables confirmed

**Then:** Begin executing user's task with selected mode and workflow.

---

## 🎮 User Control Commands (Session Management)

These commands give users control over framework state during active sessions.

### SHOW SESSION STATUS

**Purpose:** Display complete framework state and compliance status

**When user types:** `SHOW SESSION STATUS`

**Agent executes:**

```markdown
[Framework Status - User Requested]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPLETE FRAMEWORK STATUS

Mode: [CURRENT MODE NAME]
AGPF: [Active/Inactive]
Workflow: [CURRENT WORKFLOW]

Non-Negotiables Status:
✅ Never commit secrets
✅ All tests must pass before commit
✅ Always validate inputs
✅ Zero linting errors before commit
✅ Conventional commits required

Session Progress:
• Messages: [N]
• Tasks completed: [N]
• Last heartbeat: Message [N]
• Next heartbeat: Message [N]

Compliance: [All checks passing ✓ | Issues detected ⚠️]

[IF AGPF Active]
Active AGPF Agents:
• [List of active SME agents and their domains]
• [ORCHESTRATOR status]

[IF Issues Detected]
⚠️  Issues Found:
• [List specific violations or concerns]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Example Output:**

```
[Framework Status - User Requested]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPLETE FRAMEWORK STATUS

Mode: REVIEW MODE
AGPF: Active (3 SMEs + Orchestrator)
Workflow: Database Migration

Non-Negotiables Status:
✅ Never commit secrets
✅ All tests must pass before commit
✅ Always validate inputs
✅ Zero linting errors before commit
✅ Conventional commits required

Session Progress:
• Messages: 47
• Tasks completed: 2
• Last heartbeat: Message 40
• Next heartbeat: Message 60

Compliance: All checks passing ✓

Active AGPF Agents:
• [SME: Database] - Schema validation
• [SME: Security] - Migration safety review
• [SME: Performance] - Query optimization
• [ORCHESTRATOR] - Coordinating migration phases
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### REFRESH FRAMEWORK

**Purpose:** Reload core principles and reactivate current workflow (fights drift)

**When user types:** `REFRESH FRAMEWORK`

**Agent executes:**

```markdown
1. Re-read core/principles.md (non-negotiables)
2. Re-read quickref.md (Persistence Card)
3. Re-read active workflow file (if one is active)
4. Re-read active mode behavior (if non-standard mode)
5. If AGPF active, re-read agent definitions
6. Reset internal state to match loaded framework
7. Display confirmation
```

**Display:**

```
[Framework Refresh Initiated]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reloading framework...

✓ Core principles reloaded
✓ Non-negotiables verified (5 rules)
✓ [MODE NAME] behavior reloaded
✓ [WORKFLOW NAME] workflow reactivated
[IF AGPF] ✓ AGPF agent definitions reloaded

Framework awareness restored to 100%.

Current State:
• Mode: [MODE]
• AGPF: [Active/Inactive]
• Workflow: [WORKFLOW]
• Non-negotiables: All active ✓

Ready to continue. Framework fully refreshed.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When to use:**
- Agent behavior seems inconsistent with selected mode
- Long session (>80 messages) and quality seems degraded
- After complex debugging session
- User notices agent forgetting framework principles
- Preventative: Before starting critical work

**Note:** Unlike automatic heartbeats (every 20 messages), REFRESH FRAMEWORK can be triggered anytime by the user to force an immediate, complete framework reload.

---

### FRAMEWORK DRIFT CHECK

**Purpose:** Validate last 20 messages (or all messages if <20) for framework violations

**When user types:** `FRAMEWORK DRIFT CHECK`

**Agent executes:**

```markdown
1. Review last 20 messages (user + agent messages)
2. Check for non-negotiable violations
3. Check for mode behavior inconsistencies
4. Check for workflow step violations
5. Check AGPF consistency (if active)
6. Generate detailed report
7. If violations found, explain and propose corrections
```

**Display (No Violations):**

```
[Framework Drift Check - Last 20 Messages]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analyzing messages [N-20] through [N]...

Non-Negotiables Check:
✓ No secrets committed
✓ All commits had passing tests
✓ Input validation applied
✓ No linting errors committed
✓ Conventional commits used

Mode Consistency ([MODE NAME]):
✓ Output verbosity appropriate for mode
✓ Autonomy levels followed
✓ User interactions match mode behavior

Workflow Adherence ([WORKFLOW NAME]):
✓ Following workflow steps correctly
✓ No skipped critical steps
✓ Test-driven approach maintained

[IF AGPF Active]
AGPF Consistency:
✓ Multi-agent formatting maintained
✓ Explicit stance declarations used
✓ [ORCHESTRATOR] coordinating properly
✓ [SME: Domain] analysis consistent

RESULT: ✅ NO DRIFT DETECTED

Framework adherence: Excellent
Continue current approach.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Display (Violations Found):**

```
[Framework Drift Check - Last 20 Messages]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analyzing messages [N-20] through [N]...

⚠️  DRIFT DETECTED - Issues Found:

Non-Negotiable Violations:
❌ Message 35: Committed code with linting errors
   Location: src/components/Button.tsx
   Violation: "Zero linting errors before commit"

Mode Consistency Issues:
⚠️  Message 38-42: REVIEW mode but made changes without asking
   Expected: Ask before all changes
   Actual: Auto-executed 3 changes
   Severity: MEDIUM

AGPF Consistency Issues:
⚠️  Message 45-50: AGPF active but using single-agent output
   Expected: [ORCHESTRATOR] or [SME: Domain] format
   Actual: Standard output without agent tags
   Severity: HIGH

CORRECTIVE ACTIONS NEEDED:

1. Revert commit with linting errors (message 35)
   - Fix linting issues
   - Re-commit with clean code

2. For future changes in REVIEW mode:
   - Always ask before implementing
   - Show proposed changes first
   - Wait for approval

3. If AGPF should remain active:
   - Resume multi-agent formatting immediately
   - OR: User can deactivate AGPF if single-agent preferred

Would you like me to:
A) Apply corrective actions automatically
B) Explain each issue in detail
C) Deactivate AGPF and continue single-agent
D) Other (specify)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**When to use:**
- Suspecting framework not being followed
- After receiving unexpected behavior
- Before critical operations (deploy, schema changes)
- Periodically during long sessions (user discretion)
- When you want explicit validation of framework adherence

**Note:** This is a diagnostic tool. It doesn't change framework state, just reports on compliance.

---

### Power User: QUICK START with Workflow

**Enhanced QUICK START command for experienced users**

**Format:** `QUICK START: [MODE], [WORKFLOW]`

**Examples:**

```
QUICK START: SPEED MODE, BUG FIX
QUICK START: REVIEW MODE, DATABASE MIGRATION
QUICK START: DEBUG MODE, PERFORMANCE OPTIMIZATION
```

**Agent executes:**

```markdown
1. Load framework silently (no menus)
2. Detect project type
3. Activate specified mode
4. Activate specified workflow
5. Display compact status
6. Ready for work immediately
```

**Display:**

```
✓ Framework loaded
✓ Project: Next.js Web Application
✓ Mode: SPEED MODE
✓ Workflow: Bug Fix
✓ Environment: Ready

What's the bug?
```

**Benefits:**
- One-line initialization
- No interactive menus
- Instant activation
- Power user efficiency

**Available Workflows:**
- `BUG FIX`
- `FEATURE DEVELOPMENT`
- `REFACTORING`
- `CODE REVIEW`
- `TESTING`
- `DEPLOYMENT`
- `DATABASE MIGRATION`
- `PERFORMANCE OPTIMIZATION`

---

## 🔄 Command Usage Tips

**For new sessions:**
- Use `INITIATE CLAUDE CODE INSTRUCTIONS` for guided setup
- Use `QUICK START` for fast standard mode
- Use `QUICK START: MODE, WORKFLOW` for power users

**During active sessions:**
- Use `SHOW SESSION STATUS` when uncertain about framework state
- Use `REFRESH FRAMEWORK` when behavior seems inconsistent
- Use `FRAMEWORK DRIFT CHECK` before critical operations

**Automatic vs. Manual:**
- Framework heartbeats run automatically every 20 messages
- User commands can be triggered anytime for immediate action
- User commands override automatic scheduling

**In different modes:**
- SPEED: Commands show compact output
- REVIEW: Commands show full detailed output
- DEBUG: Commands include reasoning and analysis
- All modes: Commands always execute (non-negotiable)

---

## 💡 Examples

### Example 1: Full Initialization

```
User: INITIATE CLAUDE CODE INSTRUCTIONS

Claude: [Welcome message]
        [Loads instructions]
        [Detects Next.js project]
        Is this correct? [Y/n]

User: y

Claude: [Shows mode selection menu]
        Enter mode number [1-7]:

User: 1

Claude: ✓ Mode selected: EVALUATION MODE
        [Validates environment]
        [Shows task menu]
        What would you like to do?

User: 1

Claude: ✓ Task selected: Fix a bug
        [Shows session summary]
        Ready to proceed. What's the bug?

User: Login crashes when email is null

Claude: [EVAL] Workflow: workflows/bug-fix.md
        [EVAL] Starting Step 1: Understanding the bug
        [Begins bug fix workflow]
```

### Example 2: Quick Start

```
User: QUICK START: SPEED MODE

Claude: ✓ Instructions loaded
        ✓ Detected: Next.js Web Application
        ✓ Mode: SPEED MODE
        ✓ Environment: Ready

        What do you need?

User: Fix linting errors

Claude: [Executes with minimal output]
        Fixed 12 errors.
        Committed: chore: fix linting
```

---

**Remember:** This initialization ensures every session starts properly configured, with the right mode for the context, and clear understanding of what's happening.
