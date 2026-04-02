---
name: debug-chrome-extension
description: Diagnose and fix Claude Code Chrome extension connection issues. Use when /chrome shows disabled status, MCP tools are unavailable, or browser automation fails to connect.
---

# Debug Chrome Extension Connection

## Overview

The Claude in Chrome extension uses a three-component architecture:

```
Chrome Extension ──► Native Host ──► MCP Server ◄── Claude Code CLI
                    (named pipe)
```

**Components:**
1. **Chrome Extension** - Browser extension that controls Chrome
2. **Native Host** (`--chrome-native-host`) - Spawned by extension, creates named pipe
3. **MCP Server** (`--claude-in-chrome-mcp`) - Provides tools to Claude Code
4. **CLI Session** (`--chrome`) - Connects to MCP server for browser tools

Connection failures occur when any component is missing, stale, or miscommunicated.

## Quick Diagnosis

Run these commands to check component status:

### 1. Check Running Processes

```bash
# Windows (PowerShell)
Get-CimInstance Win32_Process -Filter 'name="claude.exe"' | Select-Object ProcessId, CommandLine | Format-List

# Look for these three processes:
# - claude.exe --chrome (or --permission-mode ... --chrome) - CLI session
# - claude.exe --chrome-native-host - Native messaging host
# - claude.exe --claude-in-chrome-mcp - MCP server providing tools
```

### 2. Check Named Pipe Exists

```bash
# Windows (PowerShell)
Get-ChildItem //./pipe/ | Where-Object Name -like '*claude*'

# Should see: claude-mcp-browser-bridge-{username}
```

### 3. Check Debug Log for Errors

```bash
# Find current session log
tail -100 ~/.claude/debug/latest | grep -i "chrome\|mcp\|error"

# Look for:
# - "Connection timeout" - MCP server not responding
# - "Connection failed" - Pipe or process issue
# - "Tool not found" - MCP server not connected
```

### 4. Check Extension Installation

```bash
# Windows - verify extension is installed
ls "$env:LOCALAPPDATA/Google/Chrome/User Data/Default/Extensions/fcoeoabgfenejglbffodgkkbkcdhcgfn/"
```

## Common Failure Modes

### 1. MCP Connection Timeout

**Symptoms:**
- `/chrome` shows "Status: Disabled"
- Debug log shows: `Connection to MCP server "claude-in-chrome" timed out`
- Chrome tools return "Tool not found"

**Cause:** CLI session failed to connect to MCP server at startup.

**Fix:**
```bash
# Restart Claude Code session
exit
claude --chrome
```

### 2. Stale Native Host Process

**Symptoms:**
- Native host process exists but was started hours ago
- MCP server process is missing
- New connection attempts fail

**Cause:** Old native host from previous Chrome session blocking new connections.

**Fix:**
```powershell
# Kill stale processes (Windows)
Get-Process claude | Where-Object {$_.StartTime -lt (Get-Date).AddHours(-1)} | Stop-Process -Force

# Click Chrome extension icon to spawn fresh native host
# Then restart Claude Code with: claude --chrome
```

### 3. Missing MCP Server Process

**Symptoms:**
- Native host running (`--chrome-native-host`)
- CLI running (`--chrome`)
- No `--claude-in-chrome-mcp` process

**Cause:** CLI startup failed before spawning MCP server.

**Fix:**
```bash
# Full restart required
# 1. Kill all Claude processes except your terminal
# 2. Close Chrome completely
# 3. Reopen Chrome
# 4. Click Claude extension icon
# 5. Run: claude --chrome
```

### 4. Named Pipe Missing

**Symptoms:**
- No `claude-mcp-browser-bridge-*` pipe in pipe directory
- Native host not running

**Cause:** Chrome extension not activated or native host crashed.

**Fix:**
1. Open Chrome
2. Click the Claude extension icon (puzzle piece menu if pinned)
3. Wait for native host to spawn
4. Verify pipe exists, then start `claude --chrome`

### 5. Extension Not Installed

**Symptoms:**
- Debug log shows "Extension not found in Default"
- No extension directory in Chrome extensions folder

**Fix:**
Install from Chrome Web Store: Search "Claude" by Anthropic

### 6. Registry/Manifest Mismatch

**Symptoms:**
- Extension installed but native host never spawns
- No Claude processes appear when clicking extension

**Diagnosis:**
```powershell
# Check registry points to correct manifest
reg query "HKCU\Software\Google\Chrome\NativeMessagingHosts\com.anthropic.claude_code_browser_extension"

# Check manifest exists at that path
cat "$env:APPDATA/Claude Code/ChromeNativeHost/com.anthropic.claude_code_browser_extension.json"

# Verify manifest points to valid batch file
cat ~/.claude/chrome/chrome-native-host.bat
```

**Fix:** Reinstall Claude Code to reset native messaging configuration.

## Full Reset Procedure

When individual fixes don't work:

```powershell
# 1. Kill all Claude processes
Get-Process claude -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Close Chrome completely
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force

# 3. Wait a moment
Start-Sleep -Seconds 2

# 4. Start Chrome
Start-Process chrome

# 5. Click Claude extension icon in Chrome

# 6. Verify native host spawned
Get-Process claude

# 7. Start Claude Code
claude --chrome
```

## Verifying Success

After fixes, verify all components:

```bash
# 1. Run /chrome command - should show "Status: Enabled"

# 2. Check processes (should see 3 claude.exe)
tasklist | grep claude

# 3. Test a tool
# The MCP tools like tabs_context_mcp should work
```

## Debug Log Locations

- **Windows:** `~/.claude/debug/*.txt`
- **Current session:** `~/.claude/debug/latest` (symlink)

Search patterns:
```bash
grep "claude-in-chrome" ~/.claude/debug/latest
grep "Connection" ~/.claude/debug/latest
grep "MCP server" ~/.claude/debug/latest
```
