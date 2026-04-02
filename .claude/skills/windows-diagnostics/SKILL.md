---
name: windows-diagnostics
description: "360-degree Windows system health diagnostics — covers CPU, memory, disk, network, security, startup programs, services, system info, hardware, and installed software. Use this skill whenever the user mentions system diagnostics, PC health check, performance issues, 'why is my computer slow', disk space, memory usage, startup optimization, security audit, bloatware removal, system cleanup, laptop health, or wants to keep their PC in prime condition. Also use when the user asks about high CPU, RAM usage, what's eating their disk, or wants a full system report."
---

# Windows 360° System Diagnostics

Performs a comprehensive system health check across 10 categories, generates a severity-classified HTML report, and summarizes findings with actionable recommendations.

## How to Run

### Step 1: Collect diagnostics data

Run the PowerShell collection script. It gathers data across all 10 diagnostic categories and outputs JSON:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File "C:/Users/simon/.claude/skills/windows-diagnostics/scripts/collect_diagnostics.ps1"
```

The script outputs JSON to stdout and saves it to `%TEMP%\windows_diagnostics.json`. Each section has its own error handling — if one category fails (e.g., Defender status requires admin), the rest still complete.

### Step 2: Generate the HTML report

```bash
python "C:/Users/simon/.claude/skills/windows-diagnostics/scripts/generate_report.py"
```

This reads the JSON, applies severity rules, and produces a styled HTML report at `./SystemHealthReport_YYYY-MM-DD.html` (in the current working directory). It also prints a summary to stdout.

Optionally specify a custom output path:
```bash
python "C:/Users/simon/.claude/skills/windows-diagnostics/scripts/generate_report.py" "/path/to/report.html"
```

### Step 3: Generate a per-session RemediationPlan

After the HTML report is generated, read `references/remediation_workflows.md` as a template library, then write a tailored `RemediationPlan_YYYY-MM-DD.md` to the **current working directory** (same folder as the HTML report).

**Rules for the remediation plan:**
- Include **only** the workflows that match actual findings from this run — skip everything else
- Pre-fill commands with real values from the diagnostic JSON (actual service names, actual process names, actual AppX package names found)
- Each issue gets: a one-line explanation of why it matters, pros/cons of acting, UI steps, CLI commands, and alternatives where relevant
- Order by severity: CRITICAL → WARNING → INFO
- End with a "Quick Wins" section listing the 2–3 highest-impact, lowest-risk actions the user can take right now

**Pros/cons and alternatives requirement:**
For every remedial action, include a brief **Pros / Cons** block before the steps:
- **Pros:** what improves if you take this action
- **Cons:** what you lose or risk (e.g., "HP Audio Control removal means losing HP's equalizer presets — Windows default audio still works")
- **Alternatives:** if there's a conflict (the process is needed but also causing harm), propose a middle-ground — e.g., disable at startup but keep installed, throttle instead of kill, configure instead of remove

This ensures the user can make an informed decision rather than blindly following instructions. Be specific about the trade-off for this machine's actual configuration, not generic warnings.

The file is a standalone document the user can read, share, or act on without Claude open. Keep it concise and scannable.

### Step 4: Summarize to the user

After both the HTML report and RemediationPlan are written, present findings organized by severity:

1. **CRITICAL items first** — these need immediate attention
2. **WARNING items** — should be addressed soon
3. **INFO items** — optimization opportunities
4. **OK items** — briefly mention what's healthy (don't list every OK finding)

Tell the user both output files are ready and where they are.

### Step 5: Offer to execute workflows

Ask the user: *"Would you like me to run any of these fixes for you?"*

When the user says yes to a CLI remediation:
- Show the exact command(s) you'll run before executing
- Run them via Bash tool
- Report the output (what was removed/changed/freed)
- Confirm success or surface any errors

**Important execution rules:**
- Always confirm before uninstalling software or deleting files
- Prefer targeted removals over bulk cleanups
- If a command requires admin (`Set-Service`, `Remove-AppxPackage -AllUsers`, etc.), warn the user and offer the UI alternative instead
- After running cleanup commands, show before/after metrics where possible (e.g., disk space freed, startup item count change)

## Admin vs Non-Admin

The script works without admin, but these features require elevation:
- Windows Defender detailed status
- Full event log access
- Physical disk SMART data
- Windows Update pending list (COM object)
- Secure Boot status

If key sections show errors, tell the user: "Some security checks require administrator privileges. Would you like me to explain how to re-run elevated?"

To re-run elevated, the user should open an admin terminal and run the same commands.

## Interpreting Results

Read `references/severity_rules.md` for the full classification rules. Key thresholds:
- Disk: <5% free = CRITICAL, <15% = WARNING
- Memory: >95% = CRITICAL, >85% = WARNING
- CPU: >95% = CRITICAL, >90% = WARNING
- Startup: >25 items = CRITICAL, >15 = WARNING
- Uptime: >60 days = CRITICAL, >30 = WARNING
- Any disabled security feature (Defender, Firewall) = CRITICAL

## Heavyweight Startup Process Detection

The `generate_report.py` script flags known heavyweight startup processes (Docker, LM Studio, Notion, Spotify, Steam, etc.) as WARNING. When generating the per-session RemediationPlan, go beyond the Task Manager startup tab — the registry often contains additional entries not visible there. Check both:

```powershell
Get-ItemProperty 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
```

For each heavyweight process found, the remediation plan should explain:
- What the process does and why it's heavy (RAM, disk I/O, background services)
- Whether disabling startup affects functionality (almost never does)
- The exact registry key name to remove if Task Manager doesn't show it

## Bloatware Reference

Read `references/known_bloatware.md` for the list of common pre-installed packages that can be safely removed, and which packages must NOT be removed.

## Important Notes

- The large file scan only covers Desktop, Documents, Downloads, and Videos to avoid long runtimes. It skips `node_modules`, `.git`, and `.venv` directories.
- Temperature data via WMI is unreliable on many consumer laptops. Don't alarm the user if thermal data is unavailable.
- The `Win32_Product` class is intentionally NOT used (it triggers MSI reconfiguration and is extremely slow). Software is enumerated from the registry instead.
- The health score is indicative, not absolute. A score of 100 means no issues were detected, not that the system is perfect.
