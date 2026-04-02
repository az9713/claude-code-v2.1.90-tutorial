# Claude Code v2.1.90 — Deep Dive Tutorial

> **Date:** April 1, 2026  
> **Audience:** Beginners → Power Users  
> **Goal:** Hands-on mastery of every new feature in v2.1.90

---

## Table of Contents

1. [/powerup — Interactive Feature Tours](#1-powerup--interactive-feature-tours)
2. [CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE — Offline Plugin Resilience](#2-claude_code_plugin_keep_marketplace_on_failure--offline-plugin-resilience)
3. [.husky Directory Protection in acceptEdits Mode](#3-husky-directory-protection-in-acceptedits-mode)
4. [Performance: SSE Transport Now Linear-Time](#4-performance-sse-transport-now-linear-time)
5. [Performance: Parallel Session Loading in /resume](#5-performance-parallel-session-loading-in-resume)
6. [Fix: Auto Mode Now Respects Explicit User Boundaries](#6-fix-auto-mode-now-respects-explicit-user-boundaries)
7. [Fix: Edit/Write with PostToolUse Format-on-Save Hooks](#7-fix-editwrite-with-posttooluse-format-on-save-hooks)
8. [Fix: /resume No Longer Busts Prompt Cache](#8-fix-resume-no-longer-busts-prompt-cache)
9. [Security: PowerShell Hardening](#9-security-powershell-hardening)

---

## 1. `/powerup` — Interactive Feature Tours

### What it is

`/powerup` is a new built-in slash command that launches an interactive, in-terminal lesson system. Each lesson includes animated demos that show you Claude Code features in action — not documentation, but live walkthroughs you can follow along with.

### Why it matters

Claude Code ships dozens of powerful features that most users never discover. `/powerup` solves the discoverability problem: instead of reading changelogs or docs, you *experience* features interactively.

**Beginner:** Think of it as a built-in onboarding wizard that teaches you the tool while you use it.

**Intermediate:** Use it to quickly audit which features you're not using and add them to your workflow.

**Power user:** Use it to onboard teammates without writing internal documentation.

### Hands-on: Try it now

```bash
# Launch the interactive powerup menu
/powerup
```

This opens an interactive lesson selector. Navigate with arrow keys, press Enter to start a lesson.

**Practical workflow — onboarding a new team member:**

```bash
# In a shared terminal session or screen share, walk through key lessons:
/powerup
# → Select: "Hooks & Automation"
# → Select: "MCP Servers"
# → Select: "Permission Modes"
```

**Practical workflow — before a big feature sprint:**

Before starting a complex task, run `/powerup` and pick the lesson matching your work. For example, if you're about to build an API integration:

```bash
/powerup
# → Select: "Tool Use & Bash Commands"
# → Watch the animated demo showing how Claude executes multi-step tool chains
# → Then start your actual work — you'll have the mental model fresh
```

### Power user tip

`/powerup` lessons are stored as skill files. If you have the skill system set up:

```bash
# Inspect available powerup lessons
ls ~/.claude/skills/powerups/

# You can create custom powerup lessons for your team:
# 1. Write a skill file at ~/.claude/skills/powerups/my-team-workflow.md
# 2. Run /powerup → it will appear in the menu
```

---

## 2. `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` — Offline Plugin Resilience

### What it is

When Claude Code starts, it tries to `git pull` the plugin marketplace to get the latest skills and agents. If that pull fails (no network, firewall, broken remote), the previous behavior was to clear the cache and run without plugins. Now, setting this environment variable tells Claude Code to keep the last-good cache instead.

### Why it matters

**Beginners:** If you work on a laptop that's sometimes offline, your installed skills and agents will now keep working even without internet access.

**Intermediate:** In CI/CD pipelines or Docker containers without outbound git access, your Claude Code plugins now survive without explicit offline setup.

**Power users:** Critical for air-gapped environments, corporate proxies, or any environment where the marketplace git remote is unreachable.

### Hands-on: Configure for your environment

**Option 1 — Per-session (test it):**

```bash
CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1 claude
```

To verify it's working, simulate a network failure:

```bash
# Block outbound git temporarily (macOS/Linux)
sudo pfctl -e -f /dev/null  # or use your firewall

# Then start Claude Code — plugins should still load from cache
CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1 claude

# Inside Claude: verify your skills are available
/help  # should still list your installed skills
```

**Option 2 — Permanent (add to shell profile):**

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1' >> ~/.bashrc
source ~/.bashrc
```

**Option 3 — Docker container:**

```dockerfile
# In your Dockerfile
FROM node:20

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Cache plugins during build (when network is available)
RUN claude --version  # triggers initial marketplace pull

# Keep cache on failure at runtime
ENV CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1

CMD ["claude"]
```

**Option 4 — CI pipeline (GitHub Actions):**

```yaml
# .github/workflows/claude-task.yml
jobs:
  claude-task:
    runs-on: ubuntu-latest
    env:
      CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE: "1"
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Cache Claude plugins
        uses: actions/cache@v4
        with:
          path: ~/.claude/plugins/cache
          key: claude-plugins-${{ runner.os }}
          restore-keys: claude-plugins-
      
      - name: Run Claude task
        run: claude -p "Review this PR for security issues and output a JSON report" --output-format json
```

### Power user: Combine with explicit cache priming

```bash
# Pre-warm the cache in a networked environment, then ship the image
claude --sync-plugins-only   # pulls latest, exits
docker commit my-container my-image:with-plugins
# Deploy image — CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE ensures cache stays intact
```

---

## 3. `.husky` Directory Protection in `acceptEdits` Mode

### What it is

`acceptEdits` mode auto-approves Claude's file edits without prompting you each time. v2.1.90 adds `.husky/` to the protected directory list in this mode — Claude can no longer silently modify your git hooks in `acceptEdits` mode without explicit user confirmation.

### Why it matters

**Beginners:** Husky manages your git hooks (pre-commit, pre-push, etc.) — scripts that run automatically before commits. Protecting `.husky/` means Claude can't accidentally (or maliciously) change what happens when you commit code.

**Intermediate:** This closes an attack surface. A compromised prompt or injected instruction could previously use `acceptEdits` mode to add a malicious pre-commit hook that exfiltrates code or credentials. Now it can't.

**Power users:** If you *intentionally* want Claude to update Husky config, you need to either: (a) approve the specific edit when prompted, or (b) run in a higher-trust mode explicitly.

### Hands-on: See the protection in action

**Setup — a realistic project with Husky:**

```bash
# Create a project with Husky
mkdir my-project && cd my-project
git init
npm init -y
npm install --save-dev husky

# Initialize Husky
npx husky init

# This creates .husky/pre-commit
cat .husky/pre-commit
# #!/usr/bin/env sh
# . "$(dirname -- "$0")/_/husky.sh"
# npm test
```

**Start Claude in acceptEdits mode:**

```bash
claude --permission-mode acceptEdits
```

**Now try asking Claude to modify the hook — you'll be prompted:**

```
You: Update the pre-commit hook to also run eslint before tests
```

Instead of silently editing `.husky/pre-commit`, Claude will now pause and ask for explicit confirmation — even in `acceptEdits` mode.

**Verify the protection in your settings:**

```bash
# Check what's in the protected paths list
cat ~/.claude/settings.json | jq '.protectedPaths'
# Should include ".husky"
```

**Legitimate use: if you want Claude to update hooks intentionally:**

```bash
# Run with explicit bypass for a specific session where you trust the changes
claude --permission-mode bypassPermissions
# Or: approve the individual edit when Claude prompts you in acceptEdits mode
```

### Power user: Extend this pattern to other sensitive dirs

Now that `.husky` is protected, consider protecting other sensitive config dirs in your project's `CLAUDE.md`:

```markdown
# CLAUDE.md

## Protected Directories
Claude must always ask before modifying:
- `.husky/` — git hooks
- `.github/workflows/` — CI pipeline definitions  
- `terraform/` — infrastructure as code
- `k8s/` — Kubernetes manifests
- `secrets/` — any directory named secrets (should not exist but just in case)
```

---

## 4. Performance: SSE Transport Now Linear-Time

### What it is

Claude Code communicates with MCP servers using Server-Sent Events (SSE). When receiving large streamed responses (e.g., a tool returning thousands of lines of file content), the old code processed frames in **O(n²)** time — meaning it got quadratically slower as responses grew. v2.1.90 fixes this to **O(n)**.

### Why it matters

**Beginners:** Claude Code will feel snappier when working with large files or tools that return big outputs.

**Intermediate:** Long-running tasks involving large codebases, database dumps, or log analysis will complete significantly faster.

**Power users:** If you have MCP tools that return large payloads (e.g., a tool that reads an entire database schema or returns a large JSON blob), you'll see dramatic speedups. A tool returning 10,000 tokens of data could be 100x faster.

### Hands-on: Benchmark before vs. after (or measure your current gains)

Create a test MCP tool that returns large output to see the improvement:

```javascript
// mcp-perf-test-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({ name: 'perf-test', version: '1.0.0' }, {
  capabilities: { tools: {} }
});

server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'get_large_dataset',
    description: 'Returns a large JSON dataset for perf testing',
    inputSchema: { type: 'object', properties: { rows: { type: 'number' } } }
  }]
}));

server.setRequestHandler('tools/call', async (req) => {
  if (req.params.name === 'get_large_dataset') {
    const rows = req.params.arguments?.rows ?? 5000;
    const data = Array.from({ length: rows }, (_, i) => ({
      id: i,
      name: `Record ${i}`,
      value: Math.random() * 1000,
      tags: ['alpha', 'beta', 'gamma'],
      metadata: { created: new Date().toISOString(), version: '1.0' }
    }));
    return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Register it in your Claude config:**

```json
// ~/.claude/mcp_servers.json
{
  "perf-test": {
    "command": "node",
    "args": ["/path/to/mcp-perf-test-server.js"]
  }
}
```

**Then time a large operation:**

```bash
# In Claude, time the tool call
time claude -p "Call get_large_dataset with 10000 rows and count how many have value > 500"
```

On v2.1.90, this should be noticeably faster than on v2.1.89 for large row counts.

**Real-world scenario — analyzing a large log file via MCP:**

```bash
# If you have a filesystem MCP server:
claude -p "Read /var/log/nginx/access.log and find the top 10 IP addresses by request count"
# With the linear-time fix, even 50MB log files process smoothly
```

---

## 5. Performance: Parallel Session Loading in `/resume`

### What it is

When you run `/resume` and view the all-projects list, Claude Code previously loaded each project's sessions sequentially. With many projects (50+), this made the list slow to appear. v2.1.90 loads all project sessions in parallel.

### Why it matters

**Beginners:** The `/resume` screen now loads almost instantly regardless of how many past conversations you have.

**Intermediate:** If you use Claude Code heavily across many projects, your `/resume` UX goes from "wait 10+ seconds" to near-instant.

**Power users:** This also affects programmatic session enumeration, making tooling that scans past sessions faster.

### Hands-on: Feel the difference

If you already have many projects, just run:

```bash
/resume
```

The all-projects view should now populate immediately instead of loading row by row.

**Build up a realistic multi-project history (if you don't have one):**

```bash
# Create 20 mini-projects and start sessions in each
for i in $(seq 1 20); do
  mkdir -p /tmp/test-projects/project-$i
  cd /tmp/test-projects/project-$i
  git init -q
  echo "# Project $i" > README.md
  # Start and immediately exit a Claude session to create history
  echo "Summarize this README" | claude --output-format text > /dev/null 2>&1
done

# Now try /resume — the all-projects list loads all 20 in parallel
/resume
```

**Power user: Scripting across sessions**

The parallel loading improvement also benefits any tooling that reads session history:

```bash
# List all recent sessions across all projects (now fast)
ls ~/.claude/projects/*/sessions/*.jsonl | \
  xargs -P 8 -I{} sh -c 'echo "$(stat -f "%m %N" {} 2>/dev/null || stat -c "%Y %n" {})"' | \
  sort -rn | head -20 | awk '{print $2}'
```

---

## 6. Fix: Auto Mode Now Respects Explicit User Boundaries

### What it is

In `bypassPermissions` (auto) mode, Claude was ignoring explicit instructions like "don't push this branch" or "wait for my review before running tests." Claude would proceed with those actions anyway. This is now fixed.

### Why it matters

**Beginners:** When you tell Claude "don't do X," it will now actually not do X — even in fully autonomous mode.

**Intermediate:** This was a subtle but dangerous bug. In automated workflows, Claude might push to main, deploy to production, or send a message at exactly the wrong moment despite explicit instructions.

**Power users:** This restores the guarantee that natural-language constraints in your prompts are respected in auto mode. You can now safely include instructions like "do not merge until tests pass" in automated pipelines without wrapping them in brittle conditional logic.

### Hands-on: Real examples of boundaries Claude now respects

**Example 1 — Branch safety in a CI pipeline:**

```bash
# Previously might push despite the instruction; now it won't
claude --permission-mode bypassPermissions -p "
  Implement the authentication feature from JIRA-447.
  Write tests, make them pass, commit the code.
  DO NOT push to remote — I will review and push manually.
"
# ✅ v2.1.90: Claude commits locally, stops before git push
```

**Example 2 — Staged deployment workflow:**

```bash
claude --permission-mode bypassPermissions -p "
  Deploy the app to staging using: ./scripts/deploy.sh staging
  Run the smoke tests.
  If smoke tests pass, stop and report results.
  DO NOT deploy to production — wait for my explicit approval.
"
# ✅ v2.1.90: Claude deploys to staging, runs tests, reports — never touches prod
```

**Example 3 — Database migration safety:**

```bash
claude --permission-mode bypassPermissions -p "
  Write and apply the migration for the new 'notifications' table.
  Test it against the local dev database.
  DO NOT run against staging or production databases.
  DO NOT commit anything yet — I want to review the migration file first.
"
# ✅ v2.1.90: Writes migration, tests locally, stops. No commit, no remote DB.
```

**Example 4 — Multi-step dependency:**

```bash
claude --permission-mode bypassPermissions -p "
  Refactor the UserService class to use dependency injection.
  After each file you edit, run its unit tests.
  WAIT until all unit tests pass before touching integration tests.
"
# ✅ v2.1.90: Respects the ordering constraint, doesn't jump ahead
```

### Power user: Combining with hooks for double-safety

Even with this fix, add a PostToolUse hook for critical boundaries as a belt-and-suspenders approach:

```json
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "bash -c 'if echo \"$CLAUDE_TOOL_INPUT\" | grep -q \"git push\"; then echo \"BLOCKED: git push requires manual approval\" >&2; exit 1; fi'"
      }]
    }]
  }
}
```

---

## 7. Fix: Edit/Write with PostToolUse Format-on-Save Hooks

### What it is

If you have a PostToolUse hook that auto-formats files after Claude edits them (e.g., running `prettier` or `black`), Claude's next edit to the same file would fail with `"File content has changed"` — because the formatter rewrote the file between Claude's read and its next write. This is now fixed.

### Why it matters

**Beginners:** If you use code formatters, Claude can now edit multiple files in one session without errors.

**Intermediate:** This was blocking a very common workflow: format-on-save + Claude editing code. Many teams hit this. Now it just works.

**Power users:** This enables reliable multi-file refactors with formatting enabled — something that previously required disabling hooks or doing workarounds.

### Hands-on: Set up the format-on-save workflow that now works

**Step 1 — Configure a format-on-save hook:**

```json
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=$(echo $CLAUDE_TOOL_RESULT | jq -r \".path // empty\"); if [ -n \"$FILE\" ]; then case \"$FILE\" in *.py) black \"$FILE\" 2>/dev/null ;; *.js|*.ts|*.jsx|*.tsx) prettier --write \"$FILE\" 2>/dev/null ;; *.go) gofmt -w \"$FILE\" 2>/dev/null ;; esac; fi'"
          }
        ]
      }
    ]
  }
}
```

**Step 2 — Run a multi-file refactor that previously would have broken:**

```bash
claude -p "
  Refactor the entire src/ directory to use async/await instead of Promise chains.
  Edit every .js file that uses .then() and .catch().
  Make sure error handling is preserved.
"
# ✅ v2.1.90: Prettier runs after each file edit, but Claude continues cleanly
# ✅ No more 'File content has changed' errors mid-refactor
```

**Step 3 — A realistic Python project example:**

```bash
# Project structure
mkdir -p myapp/src myapp/tests
cat > myapp/src/service.py << 'EOF'
def process_data(data):
    result=[]
    for item in data:
        if item['active']==True:
            result.append({'id':item['id'],'value':item['value']*2})
    return result
EOF

cat > myapp/src/repository.py << 'EOF'
import sqlite3
def get_all_users(db_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows=cursor.fetchall()
    conn.close()
    return rows
EOF

# Now ask Claude to refactor both files — black will auto-format after each edit
cd myapp
claude -p "
  Add type hints to all functions in src/service.py and src/repository.py.
  Add docstrings explaining what each function does.
  Keep the logic identical — only add types and docs.
"
# ✅ black runs after service.py edit, then after repository.py edit
# ✅ Both files end up properly formatted with no errors
```

### Power user: Richer format-on-save with validation

```json
// ~/.claude/settings.json  
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c '\nFILE=$(echo \"$CLAUDE_TOOL_RESULT\" | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get(\\\"path\\\",\\\"\\\"))\" 2>/dev/null)\n[ -z \"$FILE\" ] && exit 0\ncase \"$FILE\" in\n  *.py)\n    black \"$FILE\" 2>/dev/null\n    mypy \"$FILE\" --ignore-missing-imports 2>/dev/null || true\n    ;;\n  *.ts|*.tsx)\n    prettier --write \"$FILE\" 2>/dev/null\n    tsc --noEmit --skipLibCheck 2>/dev/null || true\n    ;;\nesac\n'"
          }
        ]
      }
    ]
  }
}
```

---

## 8. Fix: `/resume` No Longer Busts Prompt Cache

### What it is

Since v2.1.69, resuming a session with `/resume` caused a full prompt-cache miss on the first request — meaning Claude had to re-process the entire conversation context from scratch. This was expensive (slower + higher cost) and affected anyone using deferred tools, MCP servers, or custom agents. v2.1.90 fixes this regression.

### Why it matters

**Beginners:** Resuming a past session is now as fast and cheap as it should be.

**Intermediate:** For long sessions (50+ turns), a cache miss on resume could add 10-30 seconds of latency and meaningful cost to every session restart. This is now gone.

**Power users:** If you're building workflows that resume sessions programmatically, your cache hit rates are now restored to pre-v2.1.69 levels. This also matters for MCP-heavy setups where the schema context is large.

### Hands-on: Verify your cache is being hit on resume

```bash
# Start a session and do some work
claude -p "Analyze the architecture of this project and give me a detailed breakdown"

# Note the session ID
claude /sessions  # find your session ID

# Resume it
claude --resume <session-id> -p "Based on your analysis, what are the top 3 refactoring priorities?"

# Check if cache was hit (look for cache_read_input_tokens in the response metadata)
claude --resume <session-id> \
  --output-format json \
  -p "Follow up: estimate effort for each refactoring priority" | \
  jq '.usage | {cache_hit: .cache_read_input_tokens, cache_miss: .input_tokens}'
```

If `cache_read_input_tokens` is high (close to the total context size), you're hitting the cache. If it's 0, you're missing.

**Automated workflow that benefits from this fix:**

```bash
#!/bin/bash
# daily-project-review.sh
# Resumes yesterday's session and continues the review

SESSION_ID=$(cat ~/.my-project-session-id 2>/dev/null)

if [ -n "$SESSION_ID" ]; then
  # Resume existing session — now cache is preserved ✅
  claude --resume "$SESSION_ID" \
    --permission-mode bypassPermissions \
    -p "Continue the code review. What files still need to be reviewed from our session yesterday?"
else
  # Start fresh session
  SESSION_ID=$(claude \
    --permission-mode bypassPermissions \
    --output-format json \
    -p "Start a systematic code review of the src/ directory. Begin with the most critical files." | \
    jq -r '.session_id')
  echo "$SESSION_ID" > ~/.my-project-session-id
fi
```

---

## 9. Security: PowerShell Hardening

### What it is

Four PowerShell-specific security vulnerabilities were patched:

1. **Trailing `&` background job bypass** — Commands ending in `&` could be used to spawn background jobs that escaped Claude's execution tracking
2. **`-ErrorAction Break` debugger hang** — This flag could pause execution in a PowerShell debugger, hanging the session indefinitely
3. **Archive-extraction TOCTOU vulnerability** — A time-of-check/time-of-use race condition when extracting archives (e.g., Expand-Archive)
4. **Parse-fail fallback deny-rule degradation** — If PowerShell command parsing failed, the system would fall back to a permissive allow instead of a secure deny

Additionally, `Get-DnsClientCache` and `ipconfig /displaydns` were removed from the auto-allow list (they could leak DNS history / internal network topology).

### Why it matters

**Beginners:** Claude Code on Windows is now safer by default.

**Intermediate:** If you run Claude in automated pipelines on Windows, these fixes eliminate several ways malicious inputs could hijack execution.

**Power users:** The TOCTOU fix is especially important for any workflow where Claude extracts archives in a shared/temp directory. The parse-fail deny fix means an ambiguous or malformed command fails safely instead of being permitted.

### Hands-on: Verify the fixes

**Test 1 — Background job bypass is blocked:**

```powershell
# In a Claude session on Windows, try:
claude -p "Run this PowerShell command: Write-Host 'hello' & Start-Sleep 60"
# ✅ v2.1.90: The & background job is blocked / sanitized before execution
```

**Test 2 — DNS commands are no longer auto-allowed:**

```powershell
# Previously auto-allowed; now requires explicit user approval
claude -p "Show me the DNS cache on this machine"
# ✅ v2.1.90: Prompts for permission instead of running silently
```

**Test 3 — Safe archive extraction:**

```powershell
# Create a test archive
Compress-Archive -Path "C:\temp\test-files\*" -DestinationPath "C:\temp\test.zip"

# Ask Claude to extract it — TOCTOU race is now handled safely
claude -p "Extract C:\temp\test.zip to C:\temp\extracted"
# ✅ v2.1.90: Extraction is atomic-safe, no race window
```

**Harden your Windows Claude setup further:**

```json
// ~/.claude/settings.json (Windows)
{
  "denyTools": [],
  "env": {
    "CLAUDE_CODE_POWERSHELL_STRICT": "1"
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -Command \"$input = $env:CLAUDE_TOOL_INPUT | ConvertFrom-Json; $cmd = $input.command; if ($cmd -match 'Get-DnsClientCache|ipconfig /displaydns|Invoke-WebRequest.*external') { Write-Error 'Blocked: sensitive command'; exit 1 }\""
          }
        ]
      }
    ]
  }
}
```

---

## Summary: What to Do First

| If you are... | Start here |
|---|---|
| New to Claude Code | Run `/powerup` and work through the core lessons |
| Working offline / in CI | Set `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` |
| Using Husky + acceptEdits | Read §3 — your hooks are now protected by default |
| Running auto mode pipelines | Update your prompts to use explicit boundary instructions (§6) |
| Using format-on-save hooks | Test a multi-file refactor — it should now work end-to-end (§7) |
| Resuming long sessions | Check your cache hit rates — the regression is fixed (§8) |
| Running on Windows | Review the PowerShell hardening notes (§9) |

---

*Tutorial written for Claude Code v2.1.90 — April 1, 2026*
