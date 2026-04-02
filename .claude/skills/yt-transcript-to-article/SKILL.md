---
name: yt-transcript-to-article
description: Convert raw YouTube transcripts into polished, high-fidelity readable articles in Markdown. Use this skill whenever the user wants to clean up, rewrite, or convert a YouTube transcript (or multiple transcripts) into an article, blog post, or readable document. Also triggers when the user provides transcript files (txt, html, pdf) or URLs and asks to make them readable, turn them into an article, or clean them up. Even if the user says something casual like "make this transcript readable" or "turn these into a blog post", this skill applies.
---

# YouTube Transcript to Article

Transform one or more raw YouTube transcripts into a polished, high-fidelity Markdown article that reads like it was written by a skilled editor — while preserving every substantive point, argument, and insight from the source material.

## Core Philosophy

The goal is **maximum fidelity with maximum readability**. These are not in tension — a well-structured article can preserve 100% of the source's substance while being dramatically easier to read than a raw transcript. Never sacrifice content for brevity. The reader should be able to watch the original video afterward and find nothing surprising or missing.

Think of yourself as a world-class editor at a publication like The Atlantic or Ars Technica: you restructure, clarify, and polish — but you never distort, omit, or editorialize.

## Input Handling

The user may provide transcripts in any combination of these formats:

| Format | How to access |
|--------|--------------|
| **Plain text file** (.txt) | Read the file directly |
| **HTML file** (.html/.htm) | Read the file; strip HTML tags to extract text content |
| **PDF file** (.pdf) | Read with the Read tool (it handles PDFs) |
| **URL** (YouTube or other) | Use WebFetch to retrieve the page content |
| **Pasted text** | Use directly from the conversation |

When the user provides **multiple transcripts** (e.g., a multi-part series, or several related videos), synthesize them into a single cohesive article. Don't just concatenate — weave them together thematically, de-duplicate overlapping content, and create a unified narrative arc. Note the sources in a "Sources" section at the end.

### Parsing Raw Transcripts

Raw auto-generated transcripts are messy. Expect and handle:
- Timestamps scattered throughout (e.g., `0:00`, `[00:01:23]`, `1:23:45`)
- No punctuation or capitalization
- Filler words ("um", "uh", "like", "you know", "sort of", "kind of")
- Repetitions and false starts ("I think — I think what we need to — what we really need is...")
- Speaker labels that may be wrong or inconsistent
- Auto-caption errors (homophones, technical terms mangled)

Strip all of this noise during processing. For technical terms that appear garbled, use context to infer the correct term. If you're unsure, keep the closest reasonable interpretation and flag it with `[?]`.

## Article Structure

Generate the article with this structure:

```markdown
# [Compelling, Descriptive Title]

> **TL;DR:** [2-4 sentence summary capturing the core thesis and key takeaways]

**Source:** [Video title(s) and channel name(s)]
**Speaker(s):** [Name(s) and brief identification, if known or inferable]

---

## [Section heading]

[Article content organized by topic/theme, not chronologically]

...

## Key Takeaways

- [Bulleted list of the most important points]

---

*Sources: [List of source videos/transcripts with titles]*
```

### Structural Guidelines

- **Title**: Create a descriptive, engaging title that captures the main topic. Not clickbait — informative.
- **TL;DR**: A dense summary for readers who want the gist. Every sentence should carry weight.
- **Section headings**: Organize by **topic and theme**, not by timestamp order. Group related ideas even if they were discussed at different points in the conversation. Use clear, descriptive headings (not "Introduction" / "Part 1" / "Conclusion").
- **Key Takeaways**: Distill the 5-10 most important actionable or memorable points. Each takeaway should be a full sentence that preserves the speaker's nuance — not a stripped-down summary that loses qualifications, caveats, or context. If the speaker said "for most applications, pgvector is fine," don't reduce it to just "use pgvector."

## Writing Guidelines

### Voice and Tone
- Write in **third person** by default ("Smith argues that..." / "The discussion reveals..."). Switch to first person only if the transcript is a single speaker sharing personal experience and first person better preserves the voice.
- For interviews and podcasts, use **attributed direct quotes** for the most powerful or distinctive statements. Paraphrase the rest. Example: `As Chen puts it, "The whole industry is building on quicksand."`
- Maintain the **speaker's register** — if they're casual and funny, let that come through. If they're precise and technical, preserve that precision. Don't flatten personality.

### Fidelity Rules
- **Never invent** information, arguments, or examples not present in the transcript.
- **Never omit** a substantive point, argument, or piece of evidence. Minor tangents and social pleasantries can be trimmed, but when in doubt, keep it.
- **Preserve nuance** — if the speaker hedged, qualified, or expressed uncertainty, reflect that. Don't make tentative claims sound definitive.
- **Preserve disagreement** — if multiple speakers disagree, represent all sides faithfully. Don't smooth over tension.
- **Technical accuracy** — get terminology right. If the speaker explains a concept, make sure your article explains it with equivalent precision.

### Readability
- Break up long passages with subheadings, bullet lists, or block quotes. Bullet lists are welcome for scannability, but each bullet should be a complete thought that preserves the original nuance — never abbreviate a nuanced point into a terse fragment that loses qualifications or context.
- Use short paragraphs (2-4 sentences). Dense walls of text are hard to read.
- Lead each section with its most interesting or important point — don't bury the lede.
- Use transition sentences between sections to maintain narrative flow.
- For complex topics, add brief clarifying context in brackets `[a type of neural network architecture]` when a lay reader might be lost — but don't over-explain to the point of condescension.

### Multi-Speaker Handling
- Identify speakers by name when possible. If names aren't in the transcript, use consistent labels (Host, Guest, Speaker 1, etc.) and ask the user if they know the names.
- For interviews: structure around the topics discussed, weaving in quotes from both interviewer and interviewee. Don't use Q&A format unless the user specifically requests it.
- For panel discussions: when multiple people address the same topic, group their perspectives together rather than presenting them in chronological order.

## Process

1. **Read all inputs** — Load every transcript the user provides. For URLs, fetch the content.
2. **Identify speakers** — Determine who's talking, their names and roles if possible. Ask the user if speaker identity is ambiguous.
3. **Map the content** — Before writing, mentally outline the key topics, arguments, and themes across all transcripts. Identify the best organizational structure.
4. **Write the article** — Following the structure and guidelines above.
5. **Save as Markdown** — Write the output to a `.md` file in the user's working directory. Use a filename derived from the title (e.g., `the-future-of-ai-infrastructure.md`). Tell the user where the file is.

## What NOT to Do

- Don't produce a "summary" — this is an article. It should be comprehensive.
- Don't use generic filler ("In today's rapidly evolving landscape..."). Every sentence should carry information from the source.
- Don't add your own opinions, analysis, or predictions beyond what's in the transcript.
- Don't use chronological organization ("First they discussed X, then Y, then Z"). Organize by theme.
- Don't include timestamps in the output.
- Don't keep filler words, false starts, or verbal tics.
