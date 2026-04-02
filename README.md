# Claude Code v2.1.90 — Tutorial Creation Documentation

## Overview

This directory contains a deep dive tutorial for all new features in Claude Code v2.1.90, generated entirely within a Claude Code session on April 1, 2026.

## Files

| File | Description |
|---|---|
| `claude-code-v2.19.0-deep-dive.md` | The full tutorial (746 lines) |
| `README.md` | This file |

## How the Tutorial Was Created

### 1. Discovery: `/powerup`

The session started when the user ran `/powerup` — the new interactive feature tour command introduced in v2.1.90. Power-ups were closed, which prompted the user to ask "what are the new features in v2.1.90?"

### 2. Changelog Research — `claude-code-guide` Agent

Claude Code dispatched a specialized `claude-code-guide` subagent to look up the official v2.1.90 changelog. The agent used 4 tool calls over 29 seconds and 21.3k tokens to retrieve and synthesize release notes from:

- The official Claude Code changelog (`code.claude.com/docs/en/changelog`)
- GitHub releases (`github.com/anthropics/claude-code/releases`)

The agent returned a structured summary covering new features, performance improvements, bug fixes, and security hardening.

### 3. Tutorial Scoping — Brainstorming Skill

When the user asked for a deep dive tutorial, Claude invoked the `superpowers:brainstorming` skill before writing anything. Per the skill's process:

1. **One clarifying question was asked first:** Who is the target audience?
2. **User's answer:** All 3 levels (beginners, intermediate, power users), with hard requirements:
   - Cover every new feature — no omissions
   - Hands-on copy-paste examples that are meaningful, not toy examples
   - Examples must showcase the power of each feature

### 4. Structure Design

Based on the changelog research and user requirements, Claude structured the tutorial across 9 sections matching every feature area in the release:

| # | Area | Scope |
|---|---|---|
| 1 | `/powerup` | New command |
| 2 | `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` | New env var |
| 3 | `.husky` protection | New behavior in acceptEdits mode |
| 4 | SSE linear-time fix | Performance |
| 5 | Parallel `/resume` loading | Performance |
| 6 | Auto mode boundary respect | Bug fix (high impact) |
| 7 | Edit/Write + format-on-save | Bug fix (high impact) |
| 8 | `/resume` cache hit fix | Bug fix (regression) |
| 9 | PowerShell hardening | Security (4 sub-fixes) |

### 5. Writing

The tutorial was written in a single `Write` tool call (746 lines). Each section followed a consistent three-layer structure:

- **What it is** — plain description suitable for any level
- **Why it matters** — labeled by audience tier (Beginner / Intermediate / Power user)
- **Hands-on examples** — real-world, copy-pasteable code covering multiple scenarios per feature

### 6. Output

The tutorial was saved to:
```
docs/claude-code-v2.19.0-deep-dive.md
```
...then copied here.

## Reproducing This Process

To generate a similar tutorial for a future Claude Code release:

```bash
# Start a Claude Code session
claude

# Ask for the changelog
# (Claude will dispatch a claude-code-guide agent automatically)
what are the new features in v<VERSION>

# Request the tutorial
write a deep dive tutorial for the new features in v<VERSION>

# When asked about audience: specify all 3 levels + hard requirements
# Claude will invoke superpowers:brainstorming, ask one clarifying question,
# then write the full tutorial
```

## Session Stats

| Metric | Value |
|---|---|
| Date | 2026-04-01 |
| Model | Claude Sonnet 4.6 |
| User | — |
| Research agent | `claude-code-guide` |
| Research: tool calls | 4 |
| Research: tokens | 21,300 |
| Research: duration | 29s |
| Tutorial: lines | 746 |
| Tutorial: sections | 9 |
| Total session time | ~8 minutes |
| Skills invoked | `superpowers:brainstorming` |

## Notes on Quality Controls

- The brainstorming skill enforced a **clarifying question before writing** — preventing wasted effort on a misaligned tutorial
- The `claude-code-guide` agent was used for research rather than relying on Claude's training knowledge alone, ensuring accuracy against the actual v2.1.90 release notes
- All examples were written to be **runnable**, not illustrative — each can be copied directly into a terminal or config file
