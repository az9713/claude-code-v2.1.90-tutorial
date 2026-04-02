# Artifact Catalog

Each artifact type below includes: purpose, format, when to include, when to skip, content structure, and quality criteria.

---

## 1. Cheat Sheet

**Format:** HTML (single page, print-optimized)
**Audience:** Practitioners who want a quick reference

**Include when:** Source contains frameworks, recipes, taxonomies, decision trees, step-by-step processes, or dense factual content that benefits from visual organization.
**Skip when:** Source is purely narrative/opinion with no structured knowledge to extract.

**Structure:**
- Title and attribution header
- 3-5 major sections as visual blocks (CSS grid or flexbox)
- Tables, bullet lists, and short labeled items — no paragraphs
- Print media queries for A4/Letter, dark borders for visual separation
- Footer with source attribution and date

**Quality criteria:**
- Fits on one printed page (test at standard margins)
- Every item is factual and traceable to the source
- No filler text — every word earns its space
- Self-contained HTML with inline CSS, no external dependencies

---

## 2. Key Numbers Card

**Format:** HTML (dark-themed dashboard)
**Audience:** Decision-makers, journalists, anyone who needs headline stats

**Include when:** Source contains 5+ significant quantitative data points (costs, durations, performance metrics, comparisons, resource requirements).
**Skip when:** Source is qualitative, philosophical, or narrative without meaningful numbers.

**Structure:**
- Dark background with high-contrast cards
- Each card: one number, a label, and 1-line context
- Organize cards by theme (e.g., Performance, Cost, Scale)
- Responsive grid layout, hover effects optional
- Source attribution footer

**Quality criteria:**
- Every number is directly from the source — never estimated or hallucinated
- Units are explicit (hours, days, %, dollars, tokens)
- Context prevents misinterpretation (e.g., "per GPU-hour" not just a raw number)
- 6-12 cards total — fewer is better than padding

---

## 3. Blog Post

**Format:** Markdown (~1500-2500 words)
**Audience:** Practitioners in the source's domain (think technical blog readers)

**Include when:** Source is not already a blog post, and contains enough substance for a thematic essay that reframes the content for a reading audience.
**Skip when:** Source IS a blog post. Also skip if the source is too thin (<1000 words of substance) to support a full essay.

**Structure:**
- Compelling title (not the same as the source title)
- 4-6 thematic sections with headers (organize by argument, NOT by source order)
- Flowing paragraphs, not bullet lists
- Opening hook that establishes why the reader should care
- Closing section that synthesizes or looks forward
- No "In this post, I will discuss..." meta-commentary

**Quality criteria:**
- Adds value beyond summarizing — reframes, connects ideas, draws implications
- Written for someone who hasn't seen the source
- Each section stands on its own argument
- Specific and concrete, not vague hand-waving
- Attribution to the source author throughout

---

## 4. Twitter/X Thread

**Format:** Markdown (numbered posts)
**Audience:** Social media followers, broad tech/domain audience

**Include when:** Almost always applicable. Source has interesting claims, data, or insights worth sharing.
**Skip when:** Source is confidential/embargoed, or is itself a social media thread.

**Structure:**
- 12-20 posts, numbered [1/N] format
- Post 1: strong hook with the single most interesting claim or number
- Middle posts: organized by theme, not source order
- Final post: call to action or link to source
- Written in first person as if by the source author

**Quality criteria:**
- EVERY post must be 280 characters or fewer — this is non-negotiable
- Each post is self-contained and interesting alone
- Thread has a narrative arc, not just a list of facts
- Uses concrete details, not vague summaries
- No hashtag spam — 0-1 hashtags per post maximum

---

## 5. Annotated Bibliography

**Format:** Markdown
**Audience:** Researchers, students, anyone wanting to go deeper

**Include when:** Source cites or references 5+ other works (papers, tools, datasets, projects).
**Skip when:** Source has no meaningful external references, or is itself a bibliography/survey.

**Structure:**
- Organized by theme (not alphabetical)
- For each entry: full citation, 1-2 sentence annotation explaining relevance to the source's argument
- Separate "Core references" from "Contextual references"
- Include links where available (DOI, arXiv, GitHub)

**Quality criteria:**
- Citations are accurate (author names, year, title)
- Annotations explain WHY this reference matters in context, not just what the paper is about
- No fabricated references — only cite works actually mentioned or clearly implied by the source

---

## 6. Open Research Questions

**Format:** Markdown
**Audience:** Researchers, graduate students, anyone looking for problems to work on

**Include when:** Source identifies unsolved problems, limitations, future work, or open challenges (explicitly or implicitly).
**Skip when:** Source is purely instructional/tutorial with no frontier-of-knowledge content.

**Structure:**
- 5-15 questions, each with:
  - A clear problem statement as the heading
  - 2-4 sentences of context from the source
  - Why it matters and who might work on it
- Ordered by estimated impact (highest first)

**Quality criteria:**
- Questions are genuinely open (not already solved)
- Context connects each question to specific claims in the source
- Actionable — a reader could start working on any question after reading the entry
- Distinguishes between "the author said this is open" vs "this is implied by the source"

---

## 7. Reproducibility Guide

**Format:** Markdown
**Audience:** Practitioners who want to replicate or build on the source's work

**Include when:** Source describes a reproducible process: experiments, software, training runs, analyses with specific configs, hardware, or tools.
**Skip when:** Source is opinion, commentary, or purely theoretical with nothing to reproduce.

**Structure:**
- Prerequisites section (hardware, software, accounts needed)
- Key resources with links (code repos, datasets, model weights, papers)
- Configuration details (hyperparameters, settings, versions)
- Step-by-step reproduction outline
- Known issues and gotchas mentioned in the source
- Contact/community info for getting help

**Quality criteria:**
- Every link is to a real, publicly accessible resource
- Configs and numbers match the source exactly
- Honest about what CAN and CANNOT be reproduced
- Practical — assumes the reader has domain competence but no insider knowledge

---

## 8. Speaker Notes

**Format:** Markdown
**Audience:** The speaker (for future talks), other speakers adapting the content, presentation coaches

**Include when:** Source is a presentation, lecture, or talk — especially one with slides that clearly depend on verbal delivery for full impact.
**Skip when:** Source is not a presentation/talk. Also skip for written content (papers, blog posts, documentation).

**Structure:**
- Select 8-15 key moments where delivery matters most (not every slide)
- For each moment:
  - **On slide:** What the audience sees
  - **Verbal delivery:** What the speaker probably said (reconstructed from context)
  - **Rhetorical technique:** Why this moment works (setup/reversal, vulnerability, audience interaction, etc.)
- Overall delivery strategy summary at the end

**Quality criteria:**
- Reconstructed delivery is plausible and consistent with the speaker's voice/style
- Rhetorical analysis adds genuine insight (not just "this is effective")
- Focuses on moments that NEED verbal delivery, not self-explanatory slides

---

## 9. Modular Outline

**Format:** Markdown
**Audience:** Conference organizers, educators, the speaker, anyone repackaging the content

**Include when:** Source is long-form (>30 min talk, >5000 words, >40 slides) and can be meaningfully broken into standalone modules.
**Skip when:** Source is already short/focused on a single topic, or is not structured content.

**Structure:**
- 3-6 modules, each with:
  - Module title and duration/length estimate
  - Source section/slide range
  - Key message (one sentence)
  - Standalone context needed (what an audience needs to know if they only see this module)
  - Suggested audience
- Cross-module journey suggestions (which modules combine well for different time slots)
- Appendix recommendations

**Quality criteria:**
- Each module genuinely stands alone — no critical dependency on another module
- Time/length estimates are realistic
- Module boundaries follow natural thematic breaks, not arbitrary divisions
- Standalone context is minimal but sufficient

---

## 10. Q&A Prep

**Format:** Markdown
**Audience:** The speaker or presenter, before a talk or panel

**Include when:** Source is a presentation, lecture, or public talk where the speaker will face audience questions. Also useful for anyone presenting controversial or technical claims.
**Skip when:** Source is not a presentation. Also skip for purely written content that won't be presented live.

**Structure:**
- 10-15 predicted questions, each with:
  - The question (as an audience member would phrase it)
  - Difficulty rating: Easy, Medium, Hard, or Minefield
  - Draft answer in the speaker's voice (direct, honest, specific)
- Mix of: friendly/curious questions, skeptical/challenging questions, and "gotcha" questions
- Hardest questions first (they need the most prep)

**Quality criteria:**
- Questions are ones a knowledgeable, skeptical audience would actually ask
- Answers are honest — they acknowledge limitations rather than deflecting
- Answers use specific data/examples from the source, not vague hand-waving
- Draft answers are in the speaker's natural voice, not corporate-speak

---

## 11. Diagram Pack

**Format:** HTML (self-contained, multiple diagrams)
**Audience:** Visual learners, presenters who want to reuse diagrams, documentation writers

**Include when:** Source contains processes, architectures, taxonomies, comparisons, or relationships that benefit from visual representation.
**Skip when:** Source is purely narrative/opinion with no structural concepts to diagram.

**Structure:**
- 3-6 diagrams, each self-contained and copy-pasteable
- Types: flow diagrams (CSS flexbox/grid), comparison tables, matrix layouts, pipeline visualizations
- Pure HTML+CSS, no JavaScript required
- Each diagram has a title, the visualization, and a brief caption
- Consistent visual style across all diagrams

**Quality criteria:**
- Diagrams are accurate representations of the source content
- Readable at both screen and print sizes
- Self-contained HTML — each diagram works if extracted alone
- Clean visual hierarchy with clear labels

---

## 12. Executive Summary

**Format:** Markdown (~300-600 words)
**Audience:** Non-experts, managers, executives, journalists — anyone who needs the gist without the depth

**Include when:** Almost always applicable. Any source with substance can be summarized for a broader audience.
**Skip when:** Source is already a summary or abstract. Also skip if the source is under 500 words (too short to need summarizing).

**Structure:**
- Title and one-line description
- 3-5 key takeaways as bullet points
- Brief context paragraph (who created this, when, why it matters)
- "So what?" paragraph (implications for the reader's world)
- Optional: 2-3 key numbers if the source is quantitative

**Quality criteria:**
- Accessible to someone outside the source's domain
- No jargon without explanation
- Honest about what the source claims vs. what is established fact
- Short enough to read in 2 minutes

---

## 13. Slide Deck Outline

**Format:** Markdown
**Audience:** Someone who wants to present this content (may be the original author or someone else)

**Include when:** Source is NOT already a presentation, but contains content worth presenting. Papers, blog posts, reports, and transcripts are good candidates.
**Skip when:** Source IS already a slide deck or presentation — use Modular Outline instead.

**Structure:**
- Target talk length (suggest 15, 30, or 45 min versions)
- 15-30 slide descriptions, each with:
  - Slide title
  - Key visual or content (what goes ON the slide)
  - Speaker note (what to SAY)
- Organized with clear narrative arc: hook, context, core content, implications, close
- Audience interaction moments marked

**Quality criteria:**
- Slides follow the "one idea per slide" principle
- Speaker notes are conversational, not script-reading
- Narrative arc has tension and resolution
- Visual suggestions are concrete (not "add a relevant image")
