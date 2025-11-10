# Framework Heartbeat Protocol

**Purpose:** Maintain framework awareness and prevent drift across long conversations

**Version:** 1.0.0
**Status:** ACTIVE - All agents must follow this protocol

---

## 🎯 Core Concept

**Problem:** As conversations grow longer (50+ messages), LLM attention mechanisms prioritize recent messages over early-loaded instructions. The framework, loaded at session start, gradually fades from active attention, leading to **framework drift** where the agent forgets core principles, non-negotiables, active modes, and workflows.

**Solution:** Periodic framework reinforcement through automated "heartbeats" that re-inject critical guidance into high-attention context windows.

---

## ⚡ Heartbeat Protocol

### Automatic Triggers

Execute framework heartbeat at these intervals:

**MESSAGE-BASED TRIGGERS:**
- After every 20 messages (messages 20, 40, 60, 80, 100, etc.)
- After completing a major task or workflow
- After switching modes (SPEED → REVIEW, etc.)
- After AGPF activation or deactivation
- When approaching context limits (>85% context used)

**USER-REQUESTED TRIGGERS:**
- When user types `SHOW SESSION STATUS`
- When user types `REFRESH FRAMEWORK`
- When user types `FRAMEWORK DRIFT CHECK`

---

## 📋 Heartbeat Execution Steps

### Step 1: Re-Read Core Principles

```markdown
ACTION: Internally re-read the Persistence Card from quickref.md

CONTENT TO REFRESH:
- Active mode (SPEED, REVIEW, DEBUG, LEARNING, PROTOTYPE, STANDARD)
- AGPF status (Active or Inactive)
- 5 Non-negotiables
- Current workflow (bug-fix, feature-development, etc.)
- Current task and progress

IMPLEMENTATION:
Agent mentally reviews each item to bring it back into high-attention context
```

### Step 2: Validate Compliance

```markdown
ACTION: Check recent messages (last 20) for framework violations

VALIDATION CHECKLIST:
□ Have I violated any non-negotiables?
  - Committed secrets?
  - Committed code with failing tests?
  - Skipped input validation?
  - Committed code with linting errors?
  - Used non-conventional commit messages?

□ Am I still following the active mode behavior?
  - SPEED: Minimal communication? ✓/✗
  - REVIEW: Asking before changes? ✓/✗
  - DEBUG: Showing reasoning? ✓/✗
  - LEARNING: Explaining why? ✓/✗
  - PROTOTYPE: Relaxed gates? ✓/✗
  - STANDARD: Balanced approach? ✓/✗

□ If AGPF active, am I using multi-agent reasoning?
  - Using [ORCHESTRATOR] delegation? ✓/✗
  - Using [SME: Domain] specialist analysis? ✓/✗
  - Using explicit stances (Critique, Collaboration)? ✓/✗

□ Am I following the current workflow steps?
  - Bug Fix: Reproduce → Test → Fix → Verify? ✓/✗
  - Feature: Design → Test → Implement → Review? ✓/✗
  - Refactor: Tests first → Small changes → Verify? ✓/✗

OUTCOME:
- If all checks pass: Continue with status display
- If violations detected: Report violations and self-correct
```

### Step 3: Display Status to User

```markdown
ACTION: Show framework heartbeat status update to user

FORMAT:
```
[Framework Heartbeat #N]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mode: [MODE NAME] | AGPF: [Active/Inactive] | Workflow: [WORKFLOW]
Non-negotiables: 5/5 ✓
Compliance check: [PASS/ISSUES FOUND]
Messages since start: [N]
Next heartbeat: Message [N+20]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

EXAMPLE OUTPUT:
```
[Framework Heartbeat #3]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mode: Standard | AGPF: Inactive | Workflow: Bug Fix
Non-negotiables: 5/5 ✓
Compliance check: PASS
Messages since start: 60
Next heartbeat: Message 80
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

EXCEPTION: In SPEED MODE, use compact format:
```
[Heartbeat #3: Standard/Bug-Fix | 5/5 ✓ | Msg 60 | Next: 80]
```
```

### Step 4: Self-Correct if Drift Detected

```markdown
IF compliance check found violations:

ACTION: Report violations clearly and take corrective action

FORMAT:
```
[Framework Heartbeat #N - DRIFT DETECTED]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FRAMEWORK DRIFT DETECTED

Violations found in last 20 messages:
• [Specific violation description]
• [Specific violation description]

CORRECTIVE ACTION:
• [What I'm doing to fix this]
• [What I'm doing to prevent recurrence]

Re-reading core principles now...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

EXAMPLE:
```
[Framework Heartbeat #2 - DRIFT DETECTED]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  FRAMEWORK DRIFT DETECTED

Violations found in last 20 messages:
• AGPF was activated at message 21 but I stopped using
  multi-agent reasoning at message 35
• REVIEW mode is active but I made changes without asking
  for approval at message 38

CORRECTIVE ACTION:
• Reactivating AGPF multi-agent reasoning now
• Will ask before all changes going forward
• Re-reading REVIEW mode behavior guidelines

Framework awareness refreshed.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
```

---

## 🎛️ Heartbeat Frequency Tuning

### Standard Frequency: Every 20 Messages

**Rationale:**
- Balances framework persistence with user interruption
- Based on attention decay research (significant drift after ~30 messages)
- Minimal token overhead (~1,000 tokens per heartbeat)

### Adjusted Frequencies by Mode

**SPEED MODE:**
- Frequency: Every 30 messages (less interruption)
- Format: Compact status line
- Rationale: Speed prioritized, framework persistence secondary

**REVIEW MODE:**
- Frequency: Every 15 messages (more oversight)
- Format: Full detailed status
- Rationale: Extra caution requires more frequent checks

**DEBUG MODE:**
- Frequency: Every 20 messages (standard)
- Format: Full detailed status with reasoning
- Rationale: Thorough analysis benefits from framework stability

**LEARNING MODE:**
- Frequency: Every 20 messages (standard)
- Format: Full detailed status with explanations
- Rationale: Educational context benefits from explicit framework awareness

**PROTOTYPE MODE:**
- Frequency: Every 40 messages (relaxed)
- Format: Compact status line
- Rationale: Experimental work, framework less critical

**STANDARD MODE:**
- Frequency: Every 20 messages (default)
- Format: Standard status display
- Rationale: Balanced approach

---

## 🎯 Implementation Guidance for Agents

### When Implementing Heartbeat

**DO:**
- ✅ Set internal counter at session start (message_count = 0)
- ✅ Increment counter after each user message
- ✅ Execute heartbeat when counter % frequency == 0
- ✅ Execute heartbeat after task completion
- ✅ Execute heartbeat after mode switches
- ✅ Actually re-read the Persistence Card (don't just pretend)
- ✅ Genuinely validate compliance (don't rubber-stamp)
- ✅ Show status to user (transparency builds trust)
- ✅ Self-correct when drift detected (don't hide violations)

**DON'T:**
- ❌ Skip heartbeats to "save time" (defeats the purpose)
- ❌ Show heartbeat status without actually re-reading framework
- ❌ Mark compliance as PASS without checking
- ❌ Hide framework violations from user
- ❌ Display heartbeat in the middle of code output
- ❌ Execute heartbeat more than specified (user fatigue)

### Heartbeat Placement in Conversation

**GOOD TIMING:**
- After completing a task
- Between distinct workflow phases
- At natural conversation breaks
- Before starting a new major task

**BAD TIMING:**
- In the middle of explaining a concept
- While displaying code
- During error output
- In response to urgent user questions

**EXAMPLE - Good Placement:**
```
[Completed bug fix]
[All tests passing]
[Framework Heartbeat #2]
Mode: Standard | AGPF: Inactive | Workflow: Bug Fix
Non-negotiables: 5/5 ✓
...
[Ready for next task]
```

**EXAMPLE - Bad Placement:**
```
The authentication flow works like this:
[Framework Heartbeat #2] ← BAD: Interrupts explanation
Mode: Standard...
First, the user submits credentials...
```

---

## 🔍 Heartbeat for Different Scenarios

### Scenario 1: Normal Session (No Drift)

```
Message 1-19: Work proceeds normally
Message 20:
  [Framework Heartbeat #1]
  Mode: Standard | AGPF: Inactive | Workflow: Feature Development
  Non-negotiables: 5/5 ✓
  Compliance check: PASS
  Messages: 20 | Next: 40

Message 21-39: Continue working
Message 40:
  [Framework Heartbeat #2]
  Mode: Standard | AGPF: Inactive | Workflow: Feature Development
  Non-negotiables: 5/5 ✓
  Compliance check: PASS
  Messages: 40 | Next: 60

...and so on
```

### Scenario 2: AGPF Activated Mid-Session

```
Message 25: User says "ACTIVATE AGPF"
Message 25 response:
  [AGPF Activated]
  [Immediate framework refresh triggered by mode change]

  [Framework Heartbeat - Mode Change]
  Mode: Standard | AGPF: ACTIVE ← Status changed
  Non-negotiables: 5/5 ✓
  Multi-agent reasoning now active
  Next standard heartbeat: Message 40

  [ORCHESTRATOR]
  Analyzing task requirements...
```

### Scenario 3: Drift Detected

```
Message 40:
  [Framework Heartbeat #2 - DRIFT DETECTED]
  ⚠️  FRAMEWORK DRIFT DETECTED

  Violations:
  • Non-negotiable violated: Committed code with linting errors at message 35
  • SPEED mode shows detailed explanations (should be minimal)

  CORRECTIVE ACTION:
  • Will not commit code with linting errors going forward
  • Switching to minimal output for SPEED mode
  • Re-reading core principles

  Framework awareness refreshed.
  Continuing with task...
```

### Scenario 4: User Requests Status

```
Message 47: User says "SHOW SESSION STATUS"

Response:
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

### Scenario 5: High Context Usage Warning

```
Message 160: (Context: 175K/200K tokens = 87.5%)

  [Framework Heartbeat #8 - CONTEXT WARNING]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️  HIGH CONTEXT USAGE DETECTED

  Current usage: 175K/200K tokens (87.5%)

  IMPACT:
  • Framework may be deprioritized in attention
  • Older messages at risk of truncation
  • Framework drift risk increases

  RECOMMENDATION:
  Consider starting a fresh session soon to maintain
  framework effectiveness.

  For now, framework refreshed and operating normally.

  Mode: Standard | AGPF: Inactive | Workflow: Refactoring
  Non-negotiables: 5/5 ✓
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🚨 Critical: Non-Negotiable Heartbeat Rules

These rules about the heartbeat protocol itself are NON-NEGOTIABLE:

**1. NEVER skip scheduled heartbeats**
- Executing heartbeats is a non-negotiable requirement
- "Saving time" by skipping = allowing framework drift
- Framework drift = violations of actual non-negotiables

**2. ALWAYS actually re-read the Persistence Card**
- Don't just display status without refreshing awareness
- The re-reading is what fights attention decay
- Displaying status without re-reading is theater

**3. ALWAYS genuinely validate compliance**
- Actually check the last 20 messages
- Don't assume compliance without checking
- If violations found, report them honestly

**4. ALWAYS display status to user**
- Transparency builds trust
- User needs to see framework is active
- Hidden heartbeats defeat the purpose (user can't verify)

**5. ALWAYS self-correct when drift detected**
- Framework drift should trigger immediate corrective action
- Don't just report violations, fix them
- Document what you're doing to prevent recurrence

**Violation of these heartbeat rules = framework failure**

---

## 📊 Measuring Heartbeat Effectiveness

### Success Metrics

**Primary Metric: Framework Adherence Rate**
```
Target: >80% adherence at message 100
Measurement: % of messages following framework principles
Current baseline (no heartbeat): ~20% at message 100
Expected with heartbeat: ~80% at message 100
```

**Secondary Metrics:**
- Non-negotiable violation rate (target: 0%)
- Mode consistency (target: 100% adherence to mode behavior)
- AGPF consistency (target: 100% multi-agent output when active)
- User-reported drift incidents (target: <5% of sessions)

### Feedback Loop

**After each session with heartbeat protocol:**
1. User reports: Did framework remain effective throughout?
2. Agent self-assessment: Did I maintain framework awareness?
3. Objective measurement: Were non-negotiables violated?
4. Data collection: Framework adherence at messages 20, 40, 60, 80, 100
5. Iteration: Adjust heartbeat frequency if needed

---

## 🎓 Examples and Edge Cases

### Edge Case 1: Very Short Sessions (<20 messages)

```
IF session completes before first heartbeat (message 20):
  - No automatic heartbeat displayed
  - Framework remained fresh throughout (no decay yet)
  - Heartbeat protocol didn't add unnecessary overhead
```

### Edge Case 2: User Switches Modes Frequently

```
Message 15: User switches from STANDARD to SPEED
  → Immediate heartbeat (mode change trigger)

Message 25: User switches from SPEED to REVIEW
  → Immediate heartbeat (mode change trigger)

Message 35: User switches from REVIEW to DEBUG
  → Immediate heartbeat (mode change trigger)

Heartbeats: 3 total (15, 25, 35)
Next scheduled heartbeat: Message 40 (20 after last mode switch)
```

### Edge Case 3: User Says "Skip the heartbeat"

```
Message 40: Scheduled heartbeat

User (message 40): "Skip the heartbeat, just continue working"

Agent response:
"I understand you want to continue quickly, but the framework
heartbeat is non-negotiable for maintaining quality standards.
I'll show a compact version:

[Heartbeat #2: Standard/Bug-Fix | 5/5 ✓ | Msg 40 | Next: 60]

Continuing with work..."

RATIONALE:
- Heartbeat takes <1 second to display
- Prevents framework drift that costs minutes/hours to fix
- User can switch to SPEED mode for minimal heartbeat format
- Skipping heartbeats defeats entire persistence mechanism
```

### Edge Case 4: Multiple Tasks in Single Session

```
Message 1-25: Bug fix (using bug-fix workflow)
Message 26: Task complete

  [Framework Heartbeat - Task Completion]
  Mode: Standard | AGPF: Inactive | Workflow: Bug Fix → COMPLETE
  Non-negotiables: 5/5 ✓
  Task complete. Ready for next task.

Message 27: User requests feature development

  [Workflow switched to Feature Development]
  [Framework Heartbeat - Workflow Change]
  Mode: Standard | AGPF: Inactive | Workflow: Feature Development
  Non-negotiables: 5/5 ✓
  Framework refreshed for new workflow.

Message 28-47: Feature development
Message 48: (Scheduled heartbeat)

  [Framework Heartbeat #2]
  Mode: Standard | AGPF: Inactive | Workflow: Feature Development
  Non-negotiables: 5/5 ✓
  ...
```

---

## 🔄 Heartbeat Protocol Versioning

**Current Version:** 1.0.0

**Version History:**
- v1.0.0 (2025-11-10): Initial implementation
  - 20-message frequency
  - 4-step execution protocol
  - Mode-specific frequency adjustments
  - Drift detection and self-correction

**Future Enhancements (Planned):**
- v1.1.0: Adaptive frequency based on context usage
- v1.2.0: Machine learning to predict drift before it occurs
- v1.3.0: Integration with external framework validation tools

---

## 📚 Related Documentation

- **[Persistence Card](../quickref.md#persistence-card)** - Core principles to refresh
- **[Meta Modes](../meta-modes.md)** - Mode-specific behaviors
- **[AGPF Framework](./agpf-framework.md)** - Multi-agent reasoning system
- **[Non-Negotiables](./principles.md#non-negotiables)** - Rules that must never be violated

---

**Remember:** The heartbeat protocol exists because **framework persistence is not automatic**. Without periodic reinforcement, even the best framework will fade from attention and fail to ensure quality. The heartbeat is not overhead—it's the mechanism that makes the framework work.

---

**Status:** ACTIVE - All agents must implement this protocol starting immediately.
