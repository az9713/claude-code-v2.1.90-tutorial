# Example Run: Nathan Lambert CMU Talk

This shows a successful run of the repurpose skill on a 113-slide conference talk.

## Source

**Input:** `full_pdf.txt` (text extraction from 113-slide PDF)
**Talk:** "Building Olmo in the Era of Agents" — Nathan Lambert, AI2
**Event:** LTI Colloquium @ Carnegie Mellon University, Feb 13 2026

## Phase 2 Output: Analysis

```
## Source Analysis

**Source:** Building Olmo in the Era of Agents (113 slides)
**Type:** Conference talk / colloquium presentation
**Domain:** ML/AI — open-source language model training, RL, evaluation
**Author:** Nathan Lambert, Allen Institute for AI
**Content signals:** quantitative data, citations, open problems, reproducible methodology,
  presentation with slides, long-form (90 min), diagrammable concepts, controversial claims

## Proposed Artifacts

| # | Artifact | Format | Fit | Rationale |
|---|----------|--------|-----|-----------|
| 1 | Cheat Sheet | HTML | Strong | Dense GRPO recipe, eval taxonomy, architecture comparisons |
| 2 | Key Numbers Card | HTML | Strong | 15+ key metrics (costs, durations, memory savings) |
| 3 | Blog Post | MD | Strong | Rich enough for a 2000-word thematic essay |
| 4 | Twitter Thread | MD | Strong | Many quotable claims and surprising data points |
| 5 | Annotated Bibliography | MD | Strong | 20+ papers cited |
| 6 | Open Research Questions | MD | Strong | Multiple explicit open problems identified |
| 7 | Reproducibility Guide | MD | Strong | Specific configs, code repos, hardware details |
| 8 | Speaker Notes | MD | Strong | Slides clearly depend on verbal delivery |
| 9 | Modular Outline | MD | Strong | 90 slides easily break into 5 standalone modules |
| 10 | Q&A Prep | MD | Strong | Technical claims invite skeptical questions |
| 11 | Diagram Pack | HTML | Strong | Pipeline, async RL, eval matrix all diagrammable |

**Excluded:**
- Executive Summary: Covered by the blog post for this source
- Slide Deck Outline: Source IS already a slide deck
```

## Phase 4: Generation

All 11 artifacts launched as parallel Task agents (subagent_type: "builder").
Each agent received: full source text + artifact specification + output path.
Total generation time: ~3-5 minutes (parallel).

## Phase 5: Output

```
| File | Size | Description |
|------|------|-------------|
| artifacts/cheat_sheet.html | 16 KB | GRPO recipe, eval taxonomy, pipeline, architecture |
| artifacts/key_numbers.html | 13 KB | 8 stat cards with headline metrics |
| artifacts/blog_post.md | 16 KB | 2037-word thematic essay, 5 arguments |
| artifacts/twitter_thread.md | 4 KB | 18 posts, all verified ≤280 chars |
| artifacts/annotated_bibliography.md | 14 KB | 15 core + 7 contextual references |
| artifacts/open_research_questions.md | 4 KB | 10 research questions with context |
| artifacts/reproducibility_guide.md | 11 KB | Links, configs, hardware, step-by-step |
| artifacts/speaker_notes.md | 14 KB | 11 key moments with rhetorical analysis |
| artifacts/modular_deck_outline.md | 20 KB | 5 modules A-E with timing and audiences |
| artifacts/qa_prep.md | 18 KB | 15 questions, difficulty-rated, draft answers |
| artifacts/diagrams.html | 19 KB | 4 diagrams: pipeline, async RL, eval matrix, arch |

11 artifacts generated from Nathan Lambert's CMU LTI Colloquium talk.
```
