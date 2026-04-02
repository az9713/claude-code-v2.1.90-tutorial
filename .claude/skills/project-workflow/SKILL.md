---
name: project-workflow
description: Project development workflow patterns including Plan-Build-Review-Fix cycle and feature development processes.
triggers:
  - workflow
  - cycle
  - process
  - development flow
  - feature flow
---
# Project Workflow Skill

## Overview

This skill defines the development workflow patterns for the Codebase Singularity framework, including the core Plan-Build-Review-Fix cycle and feature development processes.

## Core Workflow: Plan-Build-Review-Fix

The foundational workflow for all development:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐│
│   │  PLAN   │───►│  BUILD  │───►│ REVIEW  │───►│   FIX   ││
│   └─────────┘    └─────────┘    └─────────┘    └────┬────┘│
│        ▲                                            │      │
│        │              Loop until                    │      │
│        └────────────  quality passes ◄──────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Phase 1: Plan
**Command**: `/plan [feature]`
**Agent**: planner

Activities:
1. Understand requirements
2. Analyze existing code
3. Research solutions
4. Design architecture
5. Create implementation plan

Output: `specs/[feature]-plan.md`

### Phase 2: Build
**Command**: `/build`
**Agent**: builder

Activities:
1. Read implementation plan
2. Create/modify files
3. Write core logic
4. Add error handling
5. Create basic tests

Output: Working code + tests

### Phase 3: Review
**Command**: `/review`
**Agent**: reviewer

Activities:
1. Check code quality
2. Verify logic correctness
3. Security analysis
4. Performance check
5. Test coverage check

Output: `specs/reviews/[date]-review.md`

### Phase 4: Fix
**Command**: `/fix`
**Agent**: fixer

Activities:
1. Address review findings
2. Fix issues by priority
3. Verify fixes
4. Re-run affected tests

Output: Fixed code + verification

## Workflow Patterns

### Feature Development

```
1. /prime        # Load context
2. /plan         # Design feature
3. /build        # Implement
4. /review       # Quality check
5. /fix          # Address issues
6. [Repeat 4-5 until passing]
7. git commit            # Save work
```

### Bug Fix

```
1. /prime        # Load context
2. [Investigate bug]     # Understand issue
3. /plan bugfix  # Plan the fix
4. /fix          # Implement fix
5. /review       # Verify fix
6. git commit            # Save work
```

### Refactoring

```
1. /prime        # Load context
2. /review       # Identify issues
3. /plan refactor # Plan changes
4. /build        # Implement refactor
5. /review       # Verify improvement
6. git commit            # Save work
```

## Complete Cycle Command

**Command**: `/cycle [feature]`

Runs the complete Plan-Build-Review-Fix cycle:

```
Step 1: Planning
├── Read requirements
├── Analyze codebase
├── Create plan
└── Get approval

Step 2: Building
├── Implement plan
├── Create tests
└── Show progress

Step 3: Reviewing
├── Quality check
├── Security check
└── Generate report

Step 4: Fixing (if needed)
├── Address findings
├── Verify fixes
└── Re-review

Step 5: Complete
├── Summary
├── Files changed
└── Next steps
```

## Quality Gates

### Before Building
- [ ] Plan approved
- [ ] Requirements clear
- [ ] Dependencies identified
- [ ] Approach validated

### Before Committing
- [ ] All tests pass
- [ ] Review score ≥ 7/10
- [ ] No critical issues
- [ ] No security vulnerabilities

### Before Release
- [ ] Feature complete
- [ ] Full test coverage
- [ ] Documentation updated
- [ ] Security audit passed

## Agent Coordination

### Single Agent Tasks

| Task | Agent |
|------|-------|
| Create plan | planner |
| Write code | builder |
| Review code | reviewer |
| Fix issues | fixer |
| Write tests | test-writer |
| Fetch docs | doc-fetcher |
| Security check | security-auditor |
| Improve code | refactorer |

### Multi-Agent Workflows

**Feature Development**:
```
planner → builder → test-writer → reviewer → fixer
```

**Security Audit**:
```
reviewer → security-auditor → fixer → reviewer
```

**Documentation**:
```
doc-fetcher → builder (docs) → reviewer
```

## Workflow Commands Reference

| Command | Purpose |
|---------|---------|
| `/prime` | Initialize session |
| `/plan` | Create implementation plan |
| `/build` | Build from plan |
| `/review` | Review code quality |
| `/fix` | Fix review issues |
| `/cycle` | Complete workflow |
| `/orchestrate` | Multi-agent coordination |
| `/delegate` | Direct agent invocation |

## Best Practices

### Planning
- Be thorough but concise
- Consider edge cases early
- Plan for testing
- Identify risks upfront

### Building
- Follow the plan
- Write clean code
- Test as you go
- Ask when unclear

### Reviewing
- Be constructive
- Provide solutions
- Prioritize findings
- Acknowledge good work

### Fixing
- Fix one issue at a time
- Verify each fix
- Don't introduce new issues
- Document changes

## Workflow Troubleshooting

### Plan Not Detailed Enough
- Ask for clarification
- Review similar features
- Break into smaller steps

### Build Taking Too Long
- Break into smaller pieces
- Check for blockers
- Review plan scope

### Review Finding Many Issues
- Don't panic
- Prioritize by severity
- Fix incrementally
- Learn from feedback

### Fix Introducing New Issues
- Roll back changes
- Fix one at a time
- Increase test coverage
- Get second review
