---
name: session-monitor
description: Launch a live dashboard showing all running Claude Code sessions on this machine. Use when the user asks to monitor sessions, check what's running, or view session activity.
triggers:
  - session monitor
  - session dashboard
  - monitor sessions
  - show all sessions
  - what sessions are running
  - check my sessions
allowed-tools:
  - Bash
---

# Session Monitor Dashboard

## How to launch

1. Install dependencies (first time only):
```bash
cd ~/.claude/skills/session-monitor/server && npm install
```

2. Start the server:
```bash
node ~/.claude/skills/session-monitor/server/index.js
```

3. Tell the user to open http://localhost:3848

Set `SESSION_MONITOR_PORT` env var to override the default port.
