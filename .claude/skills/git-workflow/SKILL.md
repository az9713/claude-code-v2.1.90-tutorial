---
name: git-workflow
description: Git workflow patterns for branching, commits, and pull requests following project conventions.
triggers:
  - git
  - branch
  - commit
  - merge
  - pull request
  - PR
---
# Git Workflow Skill

## Overview

This skill defines the git workflow patterns for the project, including branching strategies, commit conventions, and pull request guidelines.

## Branching Strategy

### Branch Types

| Branch | Purpose | Naming |
|--------|---------|--------|
| `main` | Production-ready code | Protected |
| `develop` | Integration branch | Protected |
| `feature/*` | New features | `feature/description` |
| `bugfix/*` | Bug fixes | `bugfix/issue-description` |
| `hotfix/*` | Production fixes | `hotfix/critical-fix` |
| `release/*` | Release preparation | `release/v1.2.0` |

### Branch Naming Convention

```
type/short-description

Examples:
feature/user-authentication
bugfix/login-validation
hotfix/security-patch
release/v2.0.0
```

## Commit Conventions

### Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting (no code change) |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

### Examples

```bash
# Feature
feat(auth): add JWT token validation

# Bug fix
fix(api): resolve null pointer in user lookup

# Documentation
docs(readme): update installation instructions

# Refactor
refactor(utils): simplify date formatting logic
```

### Commit Guidelines

1. **Keep commits atomic**: One logical change per commit
2. **Use present tense**: "add feature" not "added feature"
3. **Keep subject under 50 characters**
4. **Wrap body at 72 characters**
5. **Reference issues**: `Closes #123` or `Fixes #456`

## Workflow Steps

### Starting New Work

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add .
git commit -m "feat(scope): description"

# 4. Push branch
git push -u origin feature/my-feature
```

### Creating Pull Request

```bash
# 1. Ensure up to date with develop
git checkout develop
git pull origin develop
git checkout feature/my-feature
git rebase develop

# 2. Push final changes
git push origin feature/my-feature

# 3. Create PR via GitHub/CLI
gh pr create --base develop --title "feat: description" --body "..."
```

### PR Description Template

```markdown
## Summary
[Brief description of changes]

## Changes Made
- [Change 1]
- [Change 2]

## Testing Done
- [Test 1]
- [Test 2]

## Checklist
- [ ] Tests pass
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #XXX
```

### Merging

```bash
# Squash merge for features
git checkout develop
git merge --squash feature/my-feature
git commit -m "feat(scope): complete feature description"
git push origin develop

# Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

## Common Tasks

### Sync with Upstream

```bash
git fetch origin
git checkout develop
git pull origin develop
git checkout feature/my-feature
git rebase develop
```

### Fix Merge Conflicts

```bash
# During rebase
git status  # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git rebase --continue
```

### Amend Last Commit

```bash
# Change message
git commit --amend -m "new message"

# Add forgotten files
git add forgotten-file.js
git commit --amend --no-edit
```

### Interactive Rebase (Clean History)

```bash
# Squash last 3 commits
git rebase -i HEAD~3

# In editor, change 'pick' to 'squash' for commits to combine
```

## Protected Branch Rules

### `main` Branch
- Requires PR with 1+ approval
- Requires passing CI
- No direct pushes
- Linear history (squash merge)

### `develop` Branch
- Requires PR
- Requires passing CI
- No force push

## Release Process

```bash
# 1. Create release branch
git checkout develop
git checkout -b release/v1.2.0

# 2. Update version numbers, changelog
# ... make release preparations ...

# 3. Merge to main
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags

# 4. Merge back to develop
git checkout develop
git merge release/v1.2.0
git push origin develop

# 5. Clean up
git branch -d release/v1.2.0
```

## Troubleshooting

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (Discard Changes)
```bash
git reset --hard HEAD~1
```

### Recover Deleted Branch
```bash
git reflog  # Find commit hash
git checkout -b recovered-branch <hash>
```

### Clean Untracked Files
```bash
git clean -fd  # Remove untracked files and directories
```
