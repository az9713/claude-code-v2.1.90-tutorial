# Skill Best Practices Checklist

25 checks organized by criticality. Each check has an ID, description, detection logic, and fix recommendation.

---

## Table of Contents

- [Critical (C01–C04)](#critical-c01c04--skill-is-broken)
- [High (H01–H06)](#high-h01h06--skill-works-poorly)
- [Medium (M01–M10)](#medium-m01m10--could-be-improved)
- [Low (L01–L05)](#low-l01l05--nice-to-have)

---

## Critical (C01–C04) — Skill is broken

These issues prevent the skill from being discovered or loaded at all.

### C01: SKILL.md exists

- **Detection:** Check if `SKILL.md` exists in the skill directory.
- **Fix:** Create a `SKILL.md` file. Without it, the skill cannot be loaded.

### C02: YAML frontmatter present

- **Detection:** First line of SKILL.md is `---` and a second `---` delimiter closes the block within the first 30 lines.
- **Fix:** Add YAML frontmatter between `---` delimiters at the top of SKILL.md.

### C03: `name` field present in frontmatter

- **Detection:** Parse frontmatter for a `name:` key with a non-empty value.
- **Fix:** Add `name: your-skill-name` to the frontmatter.

### C04: `description` field present in frontmatter

- **Detection:** Parse frontmatter for a `description:` key with a non-empty value.
- **Fix:** Add a `description:` field explaining when to use the skill.

---

## High (H01–H06) — Skill works poorly

The skill loads but has significant quality or discoverability issues.

### H01: Description contains "when to use" triggers

- **Detection:** Check description for trigger phrases: "use when", "use for", action verbs, symptom descriptions. A good description starts with "Use when..." or includes specific triggering conditions.
- **Fix:** Rewrite description to start with "Use when..." followed by specific symptoms, situations, or contexts that signal this skill applies. Do NOT summarize the skill's workflow.

### H02: SKILL.md under 500 lines

- **Detection:** Count lines in SKILL.md.
- **Fix:** Move heavy reference content to `references/` files and link from SKILL.md. Keep the main file focused on overview, steps, and output format.

### H03: All supporting files referenced from SKILL.md

- **Detection:** List all files in the skill directory (excluding SKILL.md). For each file, check if its filename appears somewhere in SKILL.md.
- **Fix:** Add a reference or link to each supporting file from SKILL.md. Unreferenced files are invisible to the agent.

### H04: `name` field format is valid

- **Detection:** Check that name matches regex `^[a-z0-9-]{1,64}$` (lowercase, hyphens, digits only, max 64 chars).
- **Fix:** Rename to use only lowercase letters, digits, and hyphens. No spaces, underscores, or special characters.

### H05: Folder name matches `name` field

- **Detection:** Compare the skill directory basename with the `name` value in frontmatter.
- **Fix:** Ensure the folder name exactly matches the `name` field in frontmatter.

### H06: Folder uses kebab-case

- **Detection:** Check directory basename matches `^[a-z0-9]+(-[a-z0-9]+)*$`.
- **Fix:** Rename the folder to use kebab-case (lowercase words separated by hyphens).

---

## Medium (M01–M10) — Could be improved

The skill works but has room for meaningful improvement.

### M01: No `allowed-tools` restriction

- **Detection:** Check frontmatter for an `allowed-tools:` field.
- **Fix:** Add `allowed-tools:` to restrict which tools the skill can use. This prevents unintended side effects. Example: `allowed-tools: Read, Glob, Grep` for read-only skills.

### M02: Verbose body without references directory

- **Detection:** SKILL.md exceeds 300 lines AND no `references/` directory exists.
- **Fix:** Extract heavy reference content into `references/` files and link from SKILL.md. Follow progressive disclosure.

### M03: Extraneous documentation files

- **Detection:** Check for files named README.md, CHANGELOG.md, LICENSE, or CONTRIBUTING.md in the skill directory.
- **Fix:** Remove extraneous docs. Skills are self-contained via SKILL.md. A README is redundant.

### M04: Non-standard frontmatter fields

- **Detection:** Compare frontmatter keys against the known set: `name`, `description`, `allowed-tools`, `argument-hint`, `context`, `user-invocable`, `disable-model-invocation`.
- **Fix:** Remove or rename non-standard fields. Unknown fields are ignored and may confuse readers.

### M05: Deeply nested references (>1 level)

- **Detection:** Check if any files exist more than one directory level below the skill root (e.g., `references/sub/file.md`).
- **Fix:** Flatten the directory structure. One level of nesting (`references/`) is sufficient.

### M06: Long reference files lack table of contents

- **Detection:** Reference files (in `references/`) exceeding 100 lines that do not contain a "Table of Contents", "TOC", or "Contents" heading.
- **Fix:** Add a table of contents at the top of long reference files for navigation.

### M07: Side-effect skill missing `disable-model-invocation`

- **Detection:** Heuristic — SKILL.md body contains action words like "deploy", "commit", "push", "delete", "write", "publish", "send" as imperative instructions, but frontmatter lacks `disable-model-invocation: true`.
- **Fix:** If the skill performs destructive or external actions, consider adding `disable-model-invocation: true` to prevent accidental invocation.

### M08: Multi-step task skill missing `context: fork`

- **Detection:** Heuristic — SKILL.md body contains structured step patterns (e.g., "Step 1", "Phase 1", numbered procedures) suggesting a long-running task, but frontmatter lacks `context: fork`.
- **Fix:** Consider adding `context: fork` so the skill runs in a forked context, protecting the main conversation window.

### M09: `$ARGUMENTS` used but no `argument-hint`

- **Detection:** Body of SKILL.md contains `$ARGUMENTS` but frontmatter lacks `argument-hint:`.
- **Fix:** Add `argument-hint:` to frontmatter describing expected arguments. Example: `argument-hint: "[skill-name | all]"`.

### M10: Duplicated content between SKILL.md and references

- **Detection:** Heuristic — check if SKILL.md and any reference file share 3+ identical markdown headings (## or ###).
- **Fix:** Remove duplicated content from one location. SKILL.md should summarize; references should detail.

---

## Low (L01–L05) — Nice-to-have

Polish and style improvements.

### L01: Writing style uses imperative form

- **Detection:** Sample the first 10 instruction-like lines (lines starting with `-`, `*`, or numbered). Check if they begin with imperative verbs (e.g., "Run", "Check", "Add", "Use") vs passive voice or noun phrases.
- **Fix:** Rewrite instructions in imperative form: "Run the tests" not "Tests should be run" or "Running the tests".

### L02: Description length in ideal range (20–300 chars)

- **Detection:** Count characters in the `description` field.
- **Fix:** If under 20 chars, add more trigger context. If over 300 chars, trim to essential triggering conditions only.

### L03: Background knowledge skill missing `user-invocable: false`

- **Detection:** Heuristic — SKILL.md has no step-based instructions, reads like pure reference material (mostly headings, tables, code blocks, no "Step" or imperative instructions), but lacks `user-invocable: false`.
- **Fix:** Add `user-invocable: false` if the skill is background knowledge loaded automatically rather than invoked by the user.

### L04: Has "Common Mistakes" or troubleshooting section

- **Detection:** Check SKILL.md for headings containing "Common Mistakes", "Pitfalls", "Troubleshooting", "Anti-Patterns", or "Gotchas".
- **Fix:** Add a section documenting common mistakes and their fixes. This is the most-referenced section in practice.

### L05: Description keyword stuffing (>500 chars)

- **Detection:** Description field exceeds 500 characters.
- **Fix:** Trim description to essential triggering conditions. Move detailed context into the SKILL.md body instead.

---

## Scoring

Each check has a weight by criticality:
- **Critical:** 8 points each (4 checks = 32 points)
- **High:** 4 points each (6 checks = 24 points)
- **Medium:** 2 points each (10 checks = 20 points)
- **Low:** 1 point each (5 checks = 5 points)

**Total possible: 81 points**

**Score% = (earned points / 81) × 100**

A passing check earns its full points. A failing check earns 0.
