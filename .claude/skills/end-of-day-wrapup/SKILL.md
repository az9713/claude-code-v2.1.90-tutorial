---
name: wrapup
description: End-of-day wrap-up that audits what Claude did automatically and what you did manually, then generates a beautiful HTML report with tomorrow's priority.
---

# End of Day Wrap-Up

You are a personal productivity system. At the end of each day, you scan your own activity, ask the user what they worked on, and combine everything into a clean end-of-day summary with a beautiful HTML report.

## How It Works

### Step 1: Audit Your Own Activity

Before asking the user anything, scan the project for files you created or modified today. Check:

- Any output files (documents, reports, HTML files, images, etc.)
- Any data files that changed
- Any skills or configuration updates

Use Bash to find recently modified files:
```bash
find . -type f -mtime -1 2>/dev/null | grep -v node_modules | grep -v .git | head -60
```

Build a plain-English list of what you did, grouped by category:
- Documents or reports generated
- Research completed
- Data updated
- Files created or modified
- Other outputs

If nothing was found, say so honestly: "No automated outputs detected today."

### Step 2: Ask the User

After completing the audit, ask ONE question:

> "Here's what I did today: [list your activity]
>
> Now tell me what YOU did. Quick brain dump. Bullet points, half sentences, doesn't matter. What did you work on today?"

Wait for the user's response before continuing.

### Step 3: Generate the Wrap-Up

Combine both sources into this structure:

```
## End of Day - [Weekday, Month Day, Year]

### What Cowork Did (Automatically)
- [specific output, e.g. "Generated quarterly report from sales data"]
- [e.g. "Drafted 3 email responses for client follow-ups"]
- [e.g. "Researched competitor pricing and saved findings"]

### What You Did (Manually)
- [cleaned-up version of user's brain dump]
- [another item]

### Combined Progress
[2-3 sentences synthesizing both lists. What moved forward today?]

### Carried Forward
- [unfinished item that needs action tomorrow]

### Tomorrow's #1 Priority
**[One clear, specific thing]**
Why this first: [one sentence]

### Reflection
[2-3 sentences. Honest and direct. What worked? What slowed things down?]
```

### Rules
- Write in plain English. Short sentences. No jargon.
- Be specific. Not "generated content" but "generated 3 email drafts for the client proposal."
- "Carried Forward" is only things that genuinely need to happen, not abandoned ideas.
- "Tomorrow's #1 Priority" is ONE thing. Force the choice.
- "Reflection" is honest and useful. Never write "Great job!" or "You crushed it!" Just be real.

### Step 4: Generate the HTML Report

After showing the text wrap-up, generate a self-contained HTML file and save it. Use this template, filling in all `[PLACEHOLDER]` values:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>End of Day - [DATE]</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0a0a0c;
      --surface: #131318;
      --surface-raised: #1a1a22;
      --text: #e8e8ed;
      --text-dim: #7a7a8c;
      --text-muted: #4a4a58;
      --border: rgba(255,255,255,0.06);
      --accent: #DA7756;
      --accent-glow: rgba(218,119,86,0.15);
      --green: #22c55e;
      --green-bg: rgba(34,197,94,0.08);
      --yellow: #eab308;
      --yellow-bg: rgba(234,179,8,0.08);
      --blue: #3b82f6;
      --blue-bg: rgba(59,130,246,0.08);
      --orange: #f97316;
      --orange-bg: rgba(249,115,22,0.08);
      --radius: 12px;
      --radius-sm: 8px;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'DM Sans', -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
    }
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      opacity: 0.03;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
      pointer-events: none;
      z-index: 9999;
    }
    .container { max-width: 900px; margin: 0 auto; padding: 48px 24px 80px; }
    .header { margin-bottom: 48px; position: relative; }
    .header::after {
      content: '';
      position: absolute;
      bottom: -24px; left: 0; right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--border), transparent);
    }
    .header-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .date-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--accent);
      letter-spacing: 2px;
      text-transform: uppercase;
      font-weight: 500;
    }
    .pulse-dot {
      width: 8px; height: 8px;
      background: var(--accent);
      border-radius: 50%;
      animation: pulse 2s ease-in-out infinite;
      box-shadow: 0 0 12px var(--accent-glow);
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    h1 {
      font-size: 42px;
      font-weight: 700;
      letter-spacing: -1.5px;
      line-height: 1.1;
      background: linear-gradient(135deg, var(--text) 0%, var(--text-dim) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .subtitle { color: var(--text-dim); font-size: 15px; margin-top: 8px; }
    .section { margin-top: 40px; }
    .section-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
    }
    .section-icon {
      width: 32px; height: 32px;
      border-radius: var(--radius-sm);
      display: flex; align-items: center; justify-content: center;
      font-size: 15px;
      flex-shrink: 0;
    }
    .section-label {
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-weight: 500;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 24px;
    }
    .card + .card { margin-top: 8px; }
    .item-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
    .item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 15px;
      color: var(--text);
      line-height: 1.5;
    }
    .item-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      margin-top: 8px;
      flex-shrink: 0;
    }
    .green .section-icon { background: var(--green-bg); }
    .green .section-label { color: var(--green); }
    .green .item-dot { background: var(--green); }
    .blue .section-icon { background: var(--blue-bg); }
    .blue .section-label { color: var(--blue); }
    .blue .item-dot { background: var(--blue); }
    .orange .section-icon { background: var(--orange-bg); }
    .orange .section-label { color: var(--orange); }
    .orange .item-dot { background: var(--orange); }
    .yellow .section-icon { background: var(--yellow-bg); }
    .yellow .section-label { color: var(--yellow); }
    .yellow .item-dot { background: var(--yellow); }
    .accent-color .section-icon { background: var(--accent-glow); }
    .accent-color .section-label { color: var(--accent); }
    .accent-color .item-dot { background: var(--accent); }
    .priority-card {
      background: var(--surface);
      border: 1px solid rgba(218,119,86,0.3);
      border-radius: var(--radius);
      padding: 24px;
      position: relative;
      overflow: hidden;
    }
    .priority-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--accent), transparent);
    }
    .priority-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 10px;
    }
    .priority-task {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
      line-height: 1.3;
      color: var(--text);
      margin-bottom: 10px;
    }
    .priority-why {
      font-size: 14px;
      color: var(--text-dim);
      line-height: 1.6;
    }
    .prose-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 24px;
      font-size: 15px;
      color: var(--text-dim);
      line-height: 1.7;
    }
    .prose-card p + p { margin-top: 12px; }
    .stats-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-top: 40px;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px 20px;
      text-align: center;
    }
    .stat-num {
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -1px;
      color: var(--text);
    }
    .stat-label {
      font-size: 12px;
      color: var(--text-dim);
      margin-top: 4px;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .footer {
      margin-top: 60px;
      padding-top: 24px;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .footer-text {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="header-top">
        <span class="date-label">[DATE_LABEL]</span>
        <div class="pulse-dot"></div>
      </div>
      <h1>End of Day</h1>
      <p class="subtitle">Here's everything that moved forward today.</p>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-num">[COWORK_COUNT]</div>
        <div class="stat-label">Cowork outputs</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">[USER_COUNT]</div>
        <div class="stat-label">Your tasks done</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">[CARRIED_COUNT]</div>
        <div class="stat-label">Carried forward</div>
      </div>
    </div>

    <div class="section green">
      <div class="section-header">
        <div class="section-icon">&#x26A1;</div>
        <span class="section-label">What Cowork Did</span>
      </div>
      <div class="card">
        <ul class="item-list">
          [COWORK_ITEMS]
        </ul>
      </div>
    </div>

    <div class="section blue">
      <div class="section-header">
        <div class="section-icon">&#x1F9E0;</div>
        <span class="section-label">What You Did</span>
      </div>
      <div class="card">
        <ul class="item-list">
          [USER_ITEMS]
        </ul>
      </div>
    </div>

    <div class="section orange">
      <div class="section-header">
        <div class="section-icon">&#x1F4CA;</div>
        <span class="section-label">Combined Progress</span>
      </div>
      <div class="prose-card">
        <p>[COMBINED_PROGRESS]</p>
      </div>
    </div>

    <div class="section yellow">
      <div class="section-header">
        <div class="section-icon">&rarr;</div>
        <span class="section-label">Carried Forward</span>
      </div>
      <div class="card">
        <ul class="item-list">
          [CARRIED_ITEMS]
        </ul>
      </div>
    </div>

    <div class="section" style="margin-top: 40px;">
      <div class="section-header">
        <div class="section-icon accent-color" style="background: var(--accent-glow);">01</div>
        <span class="section-label" style="color: var(--accent); font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;">Tomorrow's #1 Priority</span>
      </div>
      <div class="priority-card">
        <div class="priority-label">START HERE TOMORROW</div>
        <div class="priority-task">[PRIORITY_TASK]</div>
        <div class="priority-why">[PRIORITY_WHY]</div>
      </div>
    </div>

    <div class="section accent-color">
      <div class="section-header">
        <div class="section-icon">&#x25C6;</div>
        <span class="section-label">Reflection</span>
      </div>
      <div class="prose-card">
        <p>[REFLECTION]</p>
      </div>
    </div>

    <div class="footer">
      <span class="footer-text">CLAUDE COWORK - END OF DAY</span>
      <span class="footer-text">[DATE_LABEL]</span>
    </div>
  </div>
</body>
</html>
```

Fill in every `[PLACEHOLDER]` with actual content from the wrap-up:

| Placeholder | What to fill in |
|---|---|
| `[DATE]` | Full date, e.g. "March 6, 2026" |
| `[DATE_LABEL]` | Uppercase, e.g. "THURSDAY - MARCH 6, 2026" |
| `[COWORK_COUNT]` | Number of things Cowork did |
| `[USER_COUNT]` | Number of things user did |
| `[CARRIED_COUNT]` | Number of things carried forward |
| `[COWORK_ITEMS]` | HTML list items: `<li class="item"><span class="item-dot"></span>[item]</li>` |
| `[USER_ITEMS]` | Same format for user tasks |
| `[COMBINED_PROGRESS]` | 2-3 sentence synthesis |
| `[CARRIED_ITEMS]` | Same format for carried-forward items |
| `[PRIORITY_TASK]` | The ONE thing to start tomorrow |
| `[PRIORITY_WHY]` | One sentence explaining why |
| `[REFLECTION]` | 2-3 sentence honest reflection |

Save the report as `wrapup-[YYYY-MM-DD].html` in the current directory and open it in the browser.

## Scheduling This

To run this automatically at end of every workday:

1. Open your Claude Cowork Project
2. Go to Scheduled Tasks
3. Create a new task with time 6:00 PM, frequency every weekday, prompt `/wrapup`

Claude will audit its own activity, ask for your input, and generate the full report.

## Variations

| Command | What it does |
|---------|-------------|
| `/wrapup` | Standard end-of-day wrap-up with HTML report |
| `/wrapup week` | Weekly version that wraps up Mon-Fri and identifies patterns |
| `/wrapup quick` | Just tomorrow's priority. No HTML, no reflection. 30 seconds. |
