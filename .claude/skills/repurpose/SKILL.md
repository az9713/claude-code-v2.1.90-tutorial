---
name: repurpose
description: Repurpose any information source into multiple high-quality derivative artifacts. Analyzes lectures, papers, blog posts, transcripts, and other sources, proposes applicable output formats, and generates them after user approval. Use when user says "repurpose this", "turn this into artifacts", "create content from", "break this down into outputs", or wants to maximize the reach of existing content.
disable-model-invocation: true
argument-hint: [source-file-or-url]
compatibility: Claude Code. Requires Task tool for parallel generation and file system access.
metadata:
  author: simon
  version: 1.0.0
  category: content-creation
---

# Repurpose

Transform any information source into a suite of high-quality derivative artifacts.

## Phase 1: Ingest the Source

Read the source material from `$ARGUMENTS`.

- **File path** (PDF, markdown, text, slides): Use the Read tool. For PDFs, read in batches of 15-20 pages. For very large files (>100 pages), read strategically: title/abstract, introduction, methodology, results/key sections, conclusion, references.
- **URL**: Use WebFetch to retrieve content. If the page is too large, extract the main content.
- **No argument provided**: Ask the user what source to repurpose.

After reading, write a brief internal summary capturing: the title/topic, the author(s), the core thesis or purpose, and the overall structure.

## Phase 2: Analyze the Source

Classify the source along these dimensions. For detailed guidance on how each source type behaves, consult [source-analysis-guide.md](references/source-analysis-guide.md).

**Determine:**

1. **Source type**: presentation/talk, academic paper, blog post, YouTube/video transcript, podcast transcript, technical documentation, report, interview, book chapter, or other
2. **Domain and topic**: What field? What specific subject?
3. **Original audience**: Experts, practitioners, general public, students?
4. **Content signals** — check every one that applies:
   - Contains significant quantitative data (numbers, metrics, benchmarks, costs)
   - Contains citations or references to other works
   - Identifies open problems, limitations, or future work
   - Describes reproducible methodology (code, configs, datasets, hardware)
   - Is a spoken presentation with slide structure or delivery moments
   - Is long-form content (>30 min talk, >5,000 words, >50 slides)
   - Contains structural or relational concepts that benefit from diagrams
   - Contains controversial, debatable, or surprising claims
   - Has a strong narrative arc or personal story
   - References specific tools, libraries, or frameworks

## Phase 3: Propose Artifacts

Consult [artifact-catalog.md](references/artifact-catalog.md) for the full menu of 13 artifact types with applicability criteria.

For each artifact type, evaluate:
- Do the content signals support it? (check positive signals in catalog)
- Are there reasons to skip it? (check negative signals — e.g., don't generate a blog post if the source IS a blog post)
- Rate it: **strong fit**, **moderate fit**, or **skip**

Present your proposal to the user:

```
## Source Analysis

**Source:** [title or description]
**Type:** [source type]
**Domain:** [domain/topic]
**Author(s):** [if known]
**Content signals:** [list checked signals as comma-separated tags]

## Proposed Artifacts

| # | Artifact | Format | Fit | Rationale |
|---|----------|--------|-----|-----------|
| 1 | [name] | HTML/MD | Strong | [why] |
| 2 | [name] | HTML/MD | Strong | [why] |
| ... | ... | ... | ... | ... |

**Excluded (and why):**
- [artifact]: [reason]
- [artifact]: [reason]

Shall I proceed with these N artifacts? You can add, remove, or modify any.
```

**Wait for explicit user approval before generating.** If the user modifies the list, acknowledge and proceed with their revised selection.

## Phase 4: Generate Artifacts

After approval, generate all artifacts **in parallel** using Task agents.

### Output location
- If source is a local file: create `artifacts/` next to the source
- If source is a URL: create `artifacts/` in the current working directory
- Respect any output path the user specifies

### Launching agents

For each approved artifact, launch a **builder** Task agent (`subagent_type: "builder"`) with a prompt containing:

1. **The source content** — full text, or a thorough summary if too large. Err on including more rather than less. The agent has no other context.
2. **The artifact specification** — copy the relevant section from artifact-catalog.md (purpose, format, structure, quality criteria)
3. **The output file path** — exact path where the file should be written
4. **Specific content guidance** — key themes, data points, or sections from the source that are most relevant to this artifact

Launch ALL agents in a **single message** for maximum parallelism. Use `run_in_background: true` for each.

### Quality gates (include in each agent prompt)
- HTML artifacts: self-contained (inline CSS, no external JS/CSS), responsive, print-friendly
- Markdown artifacts: valid GitHub-flavored markdown, renders correctly
- All artifacts: internally consistent numbers, accurate claims, no hallucinated data
- Twitter threads: every post must be 280 characters or fewer
- No artifact should simply restate the source — each must add value through restructuring, reframing, or visual presentation

## Phase 5: Verify and Deliver

After all agents complete:

1. List all generated files with sizes (`ls -la artifacts/`)
2. Spot-check at least one HTML file and one markdown file by reading them
3. Open HTML files in the browser for the user (`start "" "path"` on Windows, `open` on Mac)
4. Present a summary:

```
## Generated Artifacts

| File | Size | Description |
|------|------|-------------|
| artifacts/cheat_sheet.html | 16 KB | One-page visual summary |
| ... | ... | ... |

N artifacts generated from [source description].
```

## Handling Edge Cases

- **Source is too large for a single Task agent context**: Create a thorough summary document first, then pass the summary + key excerpts to each agent
- **Source is in a non-English language**: Note this in the analysis, ask user if artifacts should be in the source language or English
- **Source is multimedia** (video, audio without transcript): Ask user to provide a transcript, or suggest using a transcription tool first
- **User wants a custom artifact not in the catalog**: Accept it — ask them to describe the format, audience, and purpose, then generate it alongside catalog artifacts
- **User wants only specific artifacts**: Skip the proposal phase and generate only what they asked for
