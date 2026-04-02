---
name: mcp-doctor
description: Use when MCP servers fail to connect, omp or Claude Code crashes with EPIPE errors on startup, when MCP tools are unavailable or timing out, or after adding new servers to ~/.claude/mcp.json.
---

# MCP Doctor

## Overview

Diagnoses and repairs broken MCP server configurations. Validates that each server's binary exists and is reachable, then disables broken entries to restore startup.

## When to Use

- omp/Claude Code crashes on startup with EPIPE or connection errors
- MCP tools are unavailable or timing out
- After adding/modifying servers in any MCP config
- Periodic health check of all configured servers

**Not for:** MCP protocol-level debugging, server-side logic issues, or auth token problems (those require testing the server itself).

## Workflow

```dot
digraph mcp_doctor {
    rankdir=LR;
    diagnose [label="1. Diagnose\n(run script)" shape=box];
    review [label="2. Review\n(show results)" shape=box];
    confirm [label="User confirms\ndisabling?" shape=diamond];
    fix [label="3. Fix config\n(add disabled:true)" shape=box];
    log [label="4. Write log" shape=box];
    restart [label="5. Suggest\nrestart" shape=box];
    done [label="Done" shape=doublecircle];

    diagnose -> review -> confirm;
    confirm -> fix [label="yes"];
    confirm -> log [label="no"];
    fix -> log -> restart -> done;
}
```

### Step 1: Run Diagnostic

```bash
bash ~/.claude/skills/mcp-doctor/scripts/mcp_doctor.sh
```

Output: JSON with `sources` (configs found) and `servers` array of `{ name, status, reason, command, source, configPath }`.

The script scans all known MCP config locations:
- **User-level:** `~/.omp/agent/mcp.json`, `~/.claude/mcp.json`, `~/.cursor/mcp.json`, `~/.codeium/windsurf/mcp_config.json`
- **Project-level:** `.omp/mcp.json`, `.claude/mcp.json`, `.cursor/mcp.json`, `.vscode/mcp.json`

### Step 2: Present Results

Format as a table for the user:

| Server | Status | Command | Issue |
|--------|--------|---------|-------|
| example | OK/WARN/FAIL/SKIP | node | (reason if any) |

### Step 3: Fix Broken Servers

Ask user: "Should I disable the FAIL servers?"

On confirmation, for each FAIL server, read its `configPath` and add `"disabled": true` to the server entry in the correct config file. Preserve existing fields and formatting.

### Step 4: Create Log

Write to `~/.claude/logs/mcp-doctor-<YYYY-MM-DD-HHmmss>.log`:

```
MCP Doctor Report - <timestamp>
================================
<server>: <STATUS> - <reason>
...
Actions taken: Disabled <list of servers>
```

### Step 5: Suggest Restart

Tell user to restart omp/Claude Code to apply the fixed config.

## Quick Reference

| Status | Meaning | Action |
|--------|---------|--------|
| OK | Binary found, arg paths valid | None |
| WARN | Binary found, arg path missing | Inform user, don't disable |
| FAIL | Binary not found / docker not running | Disable on user confirmation |
| SKIP | Already has `"disabled": true` | None |

## Common Mistakes

- **Disabling WARN servers** - Only disable FAIL. WARN means the binary exists; missing arg paths may be created at runtime (e.g., npx downloads packages).
- **Skipping the log** - Always write the log. It's the audit trail for what changed and why.
- **Editing config without reading it fresh** - Always re-read `mcp.json` before editing; another process may have changed it.
- **Forgetting the restart** - Config changes only take effect after restart.
