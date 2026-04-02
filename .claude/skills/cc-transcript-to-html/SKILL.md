---
name: transcript-to-html
description: Convert Claude Code JSONL transcripts into readable, styled HTML files. Use this skill when the user wants to export, share, or review a Claude Code session transcript, convert a .jsonl transcript to HTML, create a readable version of a conversation log, or mentions "transcript", "session export", or "conversation to HTML". Also triggers when the user asks to make a transcript readable, shareable, or presentable.
---

# Transcript to HTML Converter

Converts Claude Code JSONL transcript files into clean, readable HTML with a dark theme, color-coded message bubbles, collapsible thinking blocks, and syntax-highlighted tool calls.

## When to use

- User says "convert transcript to HTML" or "make this transcript readable"
- User wants to export or share a Claude Code session
- User has a `.jsonl` transcript file and wants a human-friendly view
- User says "create HTML from session log" or similar

## How it works

Run the bundled Python script. It requires only Python 3 (no dependencies).

```bash
python <skill-directory>/scripts/convert_transcript.py <input.jsonl> <output.html>
```

The skill directory is the directory containing this SKILL.md file. Use it as the base path to reference the script.

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `input.jsonl` | Yes | Path to the Claude Code JSONL transcript |
| `output.html` | No | Output HTML path (defaults to same name with `.html` extension) |

### Examples

```bash
# Convert a transcript
python /path/to/skill/scripts/convert_transcript.py session.jsonl session.html

# Default output name (session.jsonl -> session.html)
python /path/to/skill/scripts/convert_transcript.py session.jsonl
```

## Finding transcripts

Claude Code transcripts are stored in the projects directory:

```
~/.claude/projects/<project-hash>/*.jsonl
```

The most recent `.jsonl` file in the relevant project directory is usually the current session. Use `ls -lt` to find it.

## What the HTML includes

- **Session stats** — timestamp range, message counts, tool call count
- **User messages** (blue) — what the human typed
- **Assistant messages** (amber) — Claude's responses and reasoning
- **Thinking blocks** — collapsible, showing Claude's internal reasoning
- **Tool calls** (green) — compact rendering of Read, Edit, Write, Bash, Glob, Grep, Agent, and browser automation calls
- **Tool results** — truncated to 500 chars to keep the file readable

## What the HTML excludes

- System reminders and task notifications (framework noise)
- Sidechain messages (subagent internals)
- Base64 image data from screenshots
- Full file contents from Read tool results (truncated)
- Repetitive metadata (UUIDs, session IDs, etc.)

This is why the HTML is typically 90-97% smaller than the source JSONL.
