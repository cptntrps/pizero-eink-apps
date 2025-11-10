# Tool Usage Guide

How and when to use Claude Code's tools effectively.

---

## 🎯 General Principles

1. **Use specialized tools over bash** - Read tool instead of `cat`, Edit instead of `sed`
2. **Parallelize independent operations** - Multiple Reads, Greps, or Globs in one message
3. **Sequential for dependencies** - If operation B needs result from A, run sequentially
4. **Use Task tool for complex exploration** - Don't manually Grep multiple times

---

## 📁 File Operations

### Read - Reading Files

**When to use:**
- You need to see file contents
- You want to understand existing code
- You need to check configuration

**Best practices:**
```
✅ Read multiple files in parallel if all are needed
✅ Read entire file unless it's huge (thousands of lines)
❌ Don't use bash `cat` or `head` - use Read tool
❌ Don't read one file, then another - read both in parallel
```

**Example:**
```
Task: Understand authentication flow

Do this:
Read [
  src/auth/login.ts,
  src/auth/middleware.ts,
  src/auth/types.ts
] in parallel in one message
```

---

### Edit - Modifying Existing Files

**When to use:**
- Making targeted changes to existing files
- Fixing bugs in specific locations
- Updating configurations

**Best practices:**
```
✅ Read file first before editing (required)
✅ Provide enough context in old_string to be unique
✅ Preserve exact indentation
✅ Use replace_all for renaming variables
❌ Don't include line numbers in old_string/new_string
❌ Don't use bash `sed` or `awk` - use Edit tool
```

**Example:**
```javascript
// File has been read, now editing
Edit:
  old_string: "if (user.email) {\n    sendEmail(user.email);\n  }"
  new_string: "if (user.email && user.emailVerified) {\n    sendEmail(user.email);\n  }"
```

---

### Write - Creating New Files

**When to use:**
- Creating genuinely new files
- First time writing a test file
- Adding new configuration

**Best practices:**
```
⚠️  AVOID writing new files unless necessary
✅ Prefer editing existing files
✅ Read existing similar files for consistency
❌ Don't create README.md unless requested
❌ Don't create new files when editing would work
```

**Example:**
```
✅ Good reason: Creating new feature module
❌ Bad reason: Want to refactor - edit existing instead
```

---

## 🔍 Search Operations

### Glob - Finding Files by Pattern

**When to use:**
- Finding files by name or extension
- Locating configuration files
- Discovering test files

**Best practices:**
```
✅ Use specific patterns: "**/*test.ts" not "**/*"
✅ Parallel Glob for multiple patterns
❌ Don't use bash `find` - use Glob
❌ Don't Glob with overly broad patterns
```

**Example:**
```
Find all React components and their tests:
Glob patterns in parallel:
  - "src/components/**/*.tsx"
  - "src/components/**/*.test.tsx"
```

---

### Grep - Searching Code Content

**When to use:**
- Finding where a function is used
- Searching for specific patterns
- Locating error messages

**Best practices:**
```
✅ Use output_mode: "files_with_matches" first (default)
✅ Then use output_mode: "content" to see details
✅ Use -i for case-insensitive search
✅ Use glob parameter to filter file types
❌ Don't use bash `grep` or `rg` - use Grep tool
❌ Don't grep multiple times manually - use Task tool
```

**Example:**
```
Find usage of authenticateUser function:

Step 1 - Find files:
Grep:
  pattern: "authenticateUser"
  output_mode: "files_with_matches"

Step 2 - See context:
Grep:
  pattern: "authenticateUser"
  output_mode: "content"
  -B: 2
  -A: 2
```

---

### Task - Complex Exploration

**When to use:**
- Open-ended searches ("where is error handling?")
- Multi-step codebase exploration
- Understanding unfamiliar codebases
- Repeated search attempts needed

**Best practices:**
```
✅ Use for questions about codebase structure
✅ Specify thoroughness: "quick", "medium", "very thorough"
✅ Use Explore subagent for codebase questions
❌ Don't use for simple file reads (use Read)
❌ Don't use for specific class search (use Glob)
```

**Example:**
```
❌ Bad: Search for "class UserController" → use Glob instead
✅ Good: "Where are API errors handled?" → use Task/Explore
✅ Good: "How does authentication work?" → use Task/Explore
```

---

## 🖥️ Bash - Terminal Commands

**When to use:**
- Running tests: `npm test`, `pytest`
- Building projects: `npm run build`
- Git operations: `git status`, `git commit`
- Installing dependencies: `npm install`
- Database migrations: `npm run migrate`

**Best practices:**
```
✅ Chain dependent commands with &&
✅ Run independent commands in parallel
✅ Quote paths with spaces: "path with spaces"
❌ Don't use for file operations (use Read/Edit/Write)
❌ Don't use `echo` to communicate with user
❌ Don't use `find`, `grep`, `cat` (use specialized tools)
```

**Example:**
```
✅ Good: Sequential dependencies
git add . && git commit -m "fix: auth bug" && git push

✅ Good: Parallel independent commands
Run in parallel:
  - npm test
  - npm run lint
  - npm run typecheck

❌ Bad: Using bash for file operations
cat src/index.ts  → use Read tool instead
```

---

## 🧪 Testing Workflow

**Pattern for running tests:**

```
1. Run full test suite:
   bash: npm test

2. If failures, read failed test files:
   Read test files in parallel

3. Read implementation files being tested:
   Read implementation files

4. Fix issues:
   Edit the relevant files

5. Re-run tests:
   bash: npm test

6. Verify all pass before committing
```

---

## 🔧 Git Workflow

**Pattern for commits:**

```
1. Check status (parallel with diff):
   bash: git status
   bash: git diff

2. Review changes to understand what changed

3. Stage relevant files:
   bash: git add src/auth/login.ts src/auth/types.ts

4. Create commit with conventional message:
   bash: git commit -m "$(cat <<'EOF'
   fix(auth): add email verification check before sending

   Prevents sending emails to unverified addresses.
   Fixes #123
   EOF
   )"

5. Verify commit:
   bash: git log -1 --oneline
```

---

## 🚀 Common Patterns

### Pattern: Understand Unfamiliar Code

```
1. Use Task/Explore to understand high-level structure
2. Read key files identified
3. Search for specific patterns with Grep if needed
```

### Pattern: Fix a Bug

```
1. Read the buggy file and related test
2. Understand the issue
3. Edit the file to fix
4. Run tests
5. Commit if passing
```

### Pattern: Add New Feature

```
1. Read similar existing features (parallel Reads)
2. Create/Edit implementation files
3. Create/Edit test files
4. Run tests and linting (parallel)
5. Fix any issues
6. Commit when all checks pass
```

### Pattern: Refactor Code

```
1. Read files to be refactored
2. Run tests to ensure current behavior (baseline)
3. Edit files to refactor
4. Run tests to verify behavior unchanged
5. Run linting
6. Commit if all passes
```

---

## ⚡ Performance Tips

### Parallelization Examples

**✅ Good - Parallel Independent Operations:**
```
Task: Review authentication module

Single message with:
- Read src/auth/login.ts
- Read src/auth/middleware.ts
- Read src/auth/types.ts
- Grep "authenticateUser" (output: files_with_matches)
```

**❌ Bad - Sequential When Could Be Parallel:**
```
Message 1: Read src/auth/login.ts
[wait for response]
Message 2: Read src/auth/middleware.ts
[wait for response]
Message 3: Read src/auth/types.ts
```

### When to Go Sequential

```
✅ Correct - Sequential Dependencies:
Message 1: Grep "UserController" (find the file)
[wait - need to know which file]
Message 2: Read src/controllers/UserController.ts
[wait - need to see the code]
Message 3: Edit src/controllers/UserController.ts
```

---

## 🎓 Decision Tree

```
Need to find files by name?
  → Use Glob

Need to find code content?
  → Use Grep (files_with_matches first, then content)

Need to understand "how does X work?"
  → Use Task/Explore

Need to read specific known files?
  → Use Read (multiple in parallel if possible)

Need to change existing file?
  → Read first, then Edit

Need to create new file?
  → Think: can I edit existing? If truly new, use Write

Need to run commands (tests, build, git)?
  → Use Bash
  → Parallel if independent
  → Sequential (&&) if dependent

Need to search multiple times/open-ended?
  → Use Task tool, don't manually iterate
```

---

## ❌ Common Mistakes

### Don't Do This:
```
❌ cat file.txt (use Read)
❌ grep "pattern" (use Grep tool)
❌ find . -name "*.ts" (use Glob)
❌ echo "message to user" (just output text)
❌ sed -i 's/old/new/' file (use Edit)
❌ Read one file per message (read multiple in parallel)
❌ Manually search multiple times (use Task tool)
❌ Create new README.md without being asked
```

### Do This Instead:
```
✅ Read file.txt
✅ Grep pattern "pattern"
✅ Glob "**/*.ts"
✅ Output text directly to user
✅ Edit file with old_string/new_string
✅ Read [file1, file2, file3] in parallel
✅ Task/Explore for complex searches
✅ Only create files when necessary
```

---

**Remember:** The right tool makes the job faster and more reliable. When in doubt, use specialized tools over bash commands.
