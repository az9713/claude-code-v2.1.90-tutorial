---
name: skill-best-practices
description: Audit installed Claude Code skills against best practices and output ranked suggestions. Use when you want to check skill quality, review a skill for issues, audit all personal skills, lint skills, or improve skill structure. Accepts an optional skill name or "all" (default).
allowed-tools: Read, Glob, Grep
argument-hint: "[skill-name | all]"
---

# Skill Best Practices Auditor

Audit personal Claude Code skills against a 25-check best practices checklist. **READ-ONLY** — outputs findings to terminal only. Never modifies any files.

## Constraints

- **Read-only.** Do not create, edit, or delete any files.
- **Terminal output only.** All results are printed inline.
- **Skip self.** When auditing "all", skip `skill-best-practices` to avoid feedback loops.
- **Skip non-skill directories.** Only audit directories containing a `SKILL.md` file.

## Execution Steps

### Step 1: Determine Scope

Parse `$ARGUMENTS` to decide what to audit:
- If empty or `all` → audit every skill in `~/.claude/skills/`
- If a skill name is given → audit only that skill directory
- If the name doesn't match a directory, search for partial matches and report an error if none found

### Step 2: Gather Data Per Skill

For each skill directory in scope:

1. Check if `SKILL.md` exists (C01). If not, report Critical failure and skip remaining checks for this skill.
2. Read `SKILL.md` in full.
3. Parse YAML frontmatter — extract all key-value pairs.
4. Count total lines in SKILL.md.
5. List all files and directories in the skill folder (non-recursive first, then recursive for depth checks).
6. If `references/` exists, list its contents and count lines per file.

### Step 3: Run Checklist

Load the checklist from `references/checklist.md` in this skill's directory.

Run each of the 25 checks against the gathered data. For each check, record:
- **ID** (e.g., C01, H03, M09)
- **Status:** PASS or FAIL
- **Detail:** Brief explanation (1 line). On FAIL, include the fix recommendation from the checklist.

Apply checks in order: Critical → High → Medium → Low.

For heuristic checks (M07, M08, M09, L01, L03), use best judgment. If uncertain, mark as PASS with a note.

### Step 4: Produce Report

Generate output following the format below. Print it directly to the terminal.

## Output Format

### Per-Skill Section

For each audited skill, output:

```
## [skill-name]

### Critical
- C01 PASS — SKILL.md exists
- C02 FAIL — No YAML frontmatter found
  → Fix: Add YAML frontmatter between --- delimiters at the top of SKILL.md.

### High
- H01 PASS — Description contains trigger phrases
...

### Medium
...

### Low
...

### Passed (X/25)
C01, C03, C04, H01, H02, ...
```

Group findings by criticality. Show FAIL items with their fix recommendation (prefixed with →). List all passed check IDs in a single collapsed line at the end.

Only show criticality sections that have at least one finding (PASS or FAIL).

### Summary Table

After all per-skill sections, output a summary:

```
## Summary

| Skill | Critical | High | Medium | Low | Passed | Score% |
|-------|----------|------|--------|-----|--------|--------|
| my-skill | 0 | 1 | 2 | 0 | 22/25 | 90% |
| other-skill | 1 | 0 | 3 | 1 | 20/25 | 78% |
```

Score% is calculated using the weights from `references/checklist.md`:
- Critical = 8 pts, High = 4 pts, Medium = 2 pts, Low = 1 pt
- Total possible = 81 pts
- Score% = (earned / 81) × 100, rounded to nearest integer

### Final Stats

```
## Stats

- Skills audited: 14
- Average score: 85%
- Most common issue: M01 (no allowed-tools restriction) — 9 skills
- Top recommendation: Add allowed-tools to frontmatter to restrict tool access.
```

Report the single most frequently failed check across all audited skills, with its count and fix.

## Edge Cases

- If a skill directory has no SKILL.md, report only C01 FAIL, skip all other checks, and score 0%.
- If frontmatter is missing, C02 FAIL implies C03 and C04 also FAIL. Still report all three.
- If `$ARGUMENTS` names a skill that doesn't exist, print an error and list available skills.
- For "all" mode, process skills alphabetically by directory name.
