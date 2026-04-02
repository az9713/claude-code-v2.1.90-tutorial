---
name: code-review
description: Code review checklist and best practices for thorough quality assessment.
triggers:
  - review
  - code review
  - audit
  - quality check
---
# Code Review Skill

## Overview

This skill provides a systematic approach to code review, ensuring thorough quality assessment while maintaining constructive feedback practices.

## Review Checklist

### Code Quality
- [ ] Code is readable and self-documenting
- [ ] Functions are small and focused (< 50 lines)
- [ ] Variable names are descriptive
- [ ] No unnecessary complexity
- [ ] DRY principle followed
- [ ] Consistent formatting

### Logic & Correctness
- [ ] Logic is sound and correct
- [ ] Edge cases handled
- [ ] Boundary conditions checked
- [ ] No off-by-one errors
- [ ] Return values are correct
- [ ] State mutations are intentional

### Error Handling
- [ ] All error cases handled
- [ ] Error messages are helpful
- [ ] No silent failures
- [ ] Async errors are caught
- [ ] Errors don't leak sensitive info

### Security (OWASP Top 10)
- [ ] No hardcoded credentials
- [ ] Input is validated/sanitized
- [ ] No injection vulnerabilities (SQL, XSS, command)
- [ ] Authentication/authorization proper
- [ ] Sensitive data protected

### Performance
- [ ] No obvious inefficiencies
- [ ] Appropriate data structures
- [ ] No N+1 query patterns
- [ ] Unnecessary operations avoided
- [ ] Memory leaks prevented

### Testing
- [ ] Tests exist for new code
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error cases
- [ ] Tests are maintainable

### Documentation
- [ ] Complex logic explained
- [ ] Public APIs documented
- [ ] No outdated comments
- [ ] README updated if needed

## Review Process

### Step 1: Understand Context
1. Read the PR description
2. Understand the purpose
3. Check related issues/tickets
4. Review the overall approach

### Step 2: High-Level Review
1. Does the approach make sense?
2. Are there architectural concerns?
3. Is it the right solution?
4. Are there simpler alternatives?

### Step 3: Detailed Review
1. Go through each file
2. Check against checklist
3. Note issues with severity
4. Provide specific feedback

### Step 4: Summarize
1. Categorize findings
2. Prioritize issues
3. Acknowledge good work
4. Provide clear recommendations

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **Blocker** | Security risk, crashes | Must fix before merge |
| **Critical** | Bugs, broken functionality | Must fix |
| **Major** | Code quality issues | Should fix |
| **Minor** | Style, suggestions | Nice to have |
| **Info** | Questions, discussion | FYI only |

## Feedback Guidelines

### Good Feedback

```markdown
# Constructive
"This function is getting complex. Consider extracting the validation
logic into a separate `validateInput()` function for better readability."

# Specific with solution
"Line 45: This SQL query is vulnerable to injection. Consider using
parameterized queries:
`const result = await db.query('SELECT * FROM users WHERE id = ?', [userId]);`"

# Educational
"Nice use of early returns here! For consistency, consider applying
the same pattern in the `processOrder` function above."
```

### Bad Feedback

```markdown
# Vague
"This could be better."

# No solution
"This is wrong."

# Harsh
"This is terrible code. Did you even test this?"

# Nitpicking
"Use single quotes instead of double quotes."
(When both are acceptable in the project)
```

## Review Report Template

```markdown
# Code Review Report

**PR/Commit**: [Reference]
**Reviewer**: [Name]
**Date**: [Date]

## Summary

| Severity | Count |
|----------|-------|
| Blocker | X |
| Critical | X |
| Major | X |
| Minor | X |

**Verdict**: Approve / Request Changes / Needs Discussion

## Findings

### Blockers
[None / List items]

### Critical
[None / List items]

### Major
[None / List items]

### Minor
[None / List items]

## What's Good
- [Positive observation 1]
- [Positive observation 2]

## Recommendations
1. [Action item]
2. [Action item]
```

## Common Issues to Catch

### Security
- Hardcoded secrets
- SQL injection
- XSS vulnerabilities
- Missing authentication
- Insecure direct object references

### Performance
- N+1 database queries
- Missing indexes
- Large synchronous operations
- Memory leaks
- Unnecessary API calls

### Reliability
- Missing error handling
- Race conditions
- Undefined behavior on edge cases
- No input validation
- Silent failures

### Maintainability
- Code duplication
- God functions (too long)
- Unclear naming
- Missing documentation
- Complex conditionals

## Self-Review Before PR

Authors should check:
1. [ ] Tests pass locally
2. [ ] Code is formatted
3. [ ] No debug code left
4. [ ] Self-reviewed the diff
5. [ ] PR description is clear
6. [ ] Related issues linked
