---
name: plugin-skill-auditor
description: Audit all personal Claude Code skills and plugins, back them up, and generate exhaustive removal and restoration instructions. Covers personal skills (~/.claude/skills/) and plugin marketplaces only — does NOT audit project-level (.claude/skills/) or enterprise skills. Use when you want to inventory, backup, or prepare to clean up your Claude Code extensions. This skill is READ-ONLY and will NEVER remove anything.
argument-hint: "[backup-dir-name]"
allowed-tools: Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(cat *), Bash(date *), Read, Grep, Glob, Write
---

# Plugin & Skill Auditor

**CRITICAL: This skill is AUDIT and BACKUP only. It MUST NEVER delete, remove, uninstall, or modify any skill, plugin, marketplace, or setting. All operations are read-only except for creating the backup directory and writing the report.**

## Scope

This auditor covers **personal-scope** items only (stored in `~/.claude/`):

| Scope | Audited? | Location |
|---|---|---|
| **Personal skills** | Yes | `~/.claude/skills/` |
| **Plugin marketplaces** | Yes | `~/.claude/plugins/marketplaces/` |
| **Plugin cache** | Yes | `~/.claude/plugins/cache/` |
| **User settings** | Yes | `~/.claude/settings.json` |
| **Project skills** | No | `.claude/skills/` (per-project) |
| **Enterprise skills** | No | Managed settings (org-wide) |

> **Terminology** follows [Claude Code skill scopes](https://code.claude.com/docs/en/skills): **Personal** = `~/.claude/skills/` (all your projects), **Project** = `.claude/skills/` (this project only), **Enterprise** = managed settings (all users in org), **Plugin** = `<plugin>/skills/` (where plugin is enabled).

## What This Skill Does

1. **Audits** all personal skills, plugin marketplaces, enabled plugins, and their relationships
2. **Backs up** all personal skill and plugin configuration files to the current working directory
3. **Generates** a comprehensive report with exact instructions to both REMOVE and RESTORE every item

## Execution Steps

### Step 1: Create Backup Directory

Create a timestamped backup directory in the current working directory:

```
claude-code-backup-YYYY-MM-DD/
├── skills/                    # Full copies of all skill directories (all files, following symlinks)
├── plugins/                   # Copies of all marketplace.json files
├── settings/                  # Copy of settings.json
└── AUDIT-REPORT.md            # The full audit and instruction report
```

Use `$ARGUMENTS` as the directory name if provided, otherwise default to `claude-code-backup-YYYY-MM-DD` using today's date.

### Step 2: Discover All Components

Scan the following locations and record everything found:

#### 2a. Personal Skills
- Path: `~/.claude/skills/`
- For each subdirectory, read its `SKILL.md` frontmatter (name, description)
- Copy the **entire skill directory** to the backup `skills/` directory (use `cp -rL` to follow symlinks so the backup contains real files, not broken symlinks)
- Skip `node_modules` directories during copy to save space (they can be reinstalled via `npm install`)
- Note any supporting files (scripts, templates, etc.)

#### 2b. Plugin Marketplaces
- Path: `~/.claude/plugins/marketplaces/`
- For each marketplace directory, read `.claude-plugin/marketplace.json`
- Record: marketplace name, owner, description, git remote URL (if applicable), list of all plugins available in that marketplace
- Copy each `marketplace.json` to the backup `plugins/` directory

#### 2c. Plugin Cache
- Path: `~/.claude/plugins/cache/`
- List all cached plugin entries and their versions

#### 2d. Enabled Plugins (from Settings)
- Path: `~/.claude/settings.json`
- Read the `enabledPlugins` object
- For each entry, record the plugin name and marketplace
- Copy `settings.json` to the backup `settings/` directory

### Step 3: Cross-Reference

For each enabled plugin, determine:
- Which marketplace it comes from
- What skills it provides (by reading the marketplace.json `plugins[].skills` arrays)
- What agents it provides (by reading the marketplace.json `plugins[].agents` arrays)
- What commands it provides (by reading the marketplace.json `plugins[].commands` arrays)
- The original source (git URL or local path)

### Step 4: Generate AUDIT-REPORT.md

Write a comprehensive markdown report to the backup directory. The report MUST contain ALL of the following sections:

---

#### Report Section: Overview Summary

A table summarizing:
- Total personal skills count
- Total plugin marketplaces count
- Total enabled plugins count
- Total available (but not enabled) plugins count
- Backup location and timestamp

#### Report Section: Personal Skills Inventory

For EACH personal skill found in `~/.claude/skills/`:

```markdown
### Skill: `<skill-name>`
- **Location**: `~/.claude/skills/<skill-name>/SKILL.md`
- **Description**: <from frontmatter>
- **Supporting Files**: <list any additional files in the skill directory, excluding node_modules>
- **Backup Location**: `<backup-dir>/skills/<skill-name>/` (full directory)

#### How to REMOVE this skill:
```bash
rm -rf ~/.claude/skills/<skill-name>
```

#### How to RESTORE this skill:
```bash
cp -r "<backup-dir>/skills/<skill-name>" ~/.claude/skills/<skill-name>
```
> **Note**: If this skill had `node_modules`, run `npm install` inside the skill directory after restoring.
```

#### Report Section: Plugin Marketplaces Inventory

For EACH marketplace in `~/.claude/plugins/marketplaces/`:

```markdown
### Marketplace: `<marketplace-name>`
- **Location**: `~/.claude/plugins/marketplaces/<marketplace-name>/`
- **Owner**: <owner name and email>
- **Description**: <description>
- **Source/Repository**: <git remote URL or "local">
- **Version**: <version if available>
- **Total plugins available**: <count>
- **Your enabled plugins from this marketplace**: <list>

#### Plugins in this marketplace:
| Plugin Name | Description | Enabled? |
|---|---|---|
| <name> | <desc> | Yes/No |

#### How to REMOVE this marketplace:
```bash
# 1. First disable all plugins from this marketplace in settings.json
#    Remove these entries from the "enabledPlugins" object:
<list each "pluginname@marketplace": true line to remove>

# 2. Remove the marketplace directory
rm -rf ~/.claude/plugins/marketplaces/<marketplace-name>

# 3. Remove cached plugin data for this marketplace
rm -rf ~/.claude/plugins/cache/<marketplace-name>
```

#### How to RESTORE this marketplace:
```bash
# Option A: Reinstall via Claude Code CLI
/install <marketplace-name>

# Option B: If it's a git-based marketplace, clone it manually
cd ~/.claude/plugins/marketplaces
git clone <git-url> <marketplace-name>

# Then re-enable desired plugins by adding to ~/.claude/settings.json "enabledPlugins":
<JSON entries to add>
```
```

#### Report Section: Enabled Plugins Detail

For EACH enabled plugin in `settings.json`:

```markdown
### Plugin: `<plugin-name>` (from `<marketplace-name>`)
- **Settings Key**: `"<plugin-name>@<marketplace-name>": true`
- **Source**: <source path or git URL>
- **Provides Skills**: <list of skill names>
- **Provides Agents**: <list of agent names>
- **Provides Commands**: <list of command names>

#### How to DISABLE (without removing marketplace):
Edit `~/.claude/settings.json` and remove this line from `enabledPlugins`:
```json
"<plugin-name>@<marketplace-name>": true
```

#### How to RE-ENABLE:
Edit `~/.claude/settings.json` and add this line to `enabledPlugins`:
```json
"<plugin-name>@<marketplace-name>": true
```
Or use: `/install <plugin-name>` from the plugin browser.
```

#### Report Section: Nuclear Option - Complete Cleanup

Provide a single script that removes EVERYTHING (skills + plugins + settings), clearly marked with warnings:

```markdown
## DANGER ZONE: Complete Removal of All Skills and Plugins

**WARNING: This will remove ALL custom skills, ALL plugin marketplaces, ALL cached plugins, and ALL enabled plugin settings. This is irreversible without a backup.**

### Step 1: Backup first (already done if you ran this audit)

### Step 2: Remove all personal skills
```bash
rm -rf ~/.claude/skills/*
```

### Step 3: Remove all plugin marketplaces and cache
```bash
rm -rf ~/.claude/plugins/marketplaces/
rm -rf ~/.claude/plugins/cache/
```

### Step 4: Remove enabledPlugins from settings
Edit `~/.claude/settings.json` and delete the entire `"enabledPlugins"` block.

### Step 5: Restart Claude Code
Close and reopen Claude Code for changes to take effect.
```

#### Report Section: Complete Restoration from Backup

Provide the full restoration procedure using the backup created by this audit:

```markdown
## Full Restoration from Backup

### Step 1: Restore personal skills
```bash
# For each skill in the backup:
cp -r <backup-dir>/skills/* ~/.claude/skills/
```

### Step 2: Reinstall marketplaces
<For each marketplace, provide the specific /install command or git clone command>

### Step 3: Re-enable plugins
<Provide the exact JSON to paste into settings.json enabledPlugins>

### Step 4: Restart Claude Code
```
```

### Step 5: Display Results

After generating the report:
1. Print a summary to the user showing what was found
2. Tell them the backup location
3. Tell them to read `AUDIT-REPORT.md` for full removal/restoration instructions

## Important Constraints

- **NEVER** delete, remove, or uninstall anything
- **NEVER** modify `settings.json` or any plugin/skill files
- **ONLY** create new files in the backup directory
- **ONLY** read existing files for auditing
- If a file cannot be read, note it in the report and continue
- Skip `node_modules` directories when listing supporting files
- For the `surveil` skill or any skill with large dependency trees, only list top-level supporting files
