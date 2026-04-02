# Source Analysis Guide

How to classify and extract from different information source types.

---

## Presentation / Talk (Slides)

**How to identify:** PDF with slides, PowerPoint file, or a document with slide numbers. Often sparse text per page with visual elements described or implied.

**What's unique:** Content is designed for oral delivery. Slides often contain incomplete information that relies on verbal explanation. Structure follows a presentation arc (hook → body → conclusion), not a logical/academic structure.

**Key extraction targets:**
- Slide titles and key claims (often the core argument)
- Numbers, charts, and data visualizations described in text
- Progressive builds (slides that add content incrementally)
- Audience interaction moments (polls, questions, pauses)
- The narrative arc and transitions between sections

**Strong artifacts:** Cheat Sheet, Key Numbers, Speaker Notes, Q&A Prep, Modular Outline, Blog Post, Twitter Thread, Diagram Pack
**Usually skip:** Slide Deck Outline (source IS slides already)

---

## Academic Paper (arXiv, journal, conference)

**How to identify:** Has abstract, sections (Introduction, Related Work, Methods, Results, Discussion), citations in brackets or numbered format, often LaTeX-formatted.

**What's unique:** Dense, precise language. Claims are scoped and hedged. Heavy citation network. Methodology is (usually) reproducible. Results have specific numbers and statistical measures.

**Key extraction targets:**
- Abstract and key claims
- Method/algorithm descriptions
- Tables and figures (described in text)
- Comparison with prior work
- Limitations section (gold mine for open questions)
- Future work

**Strong artifacts:** Annotated Bibliography, Open Research Questions, Reproducibility Guide, Key Numbers, Blog Post, Cheat Sheet, Executive Summary, Slide Deck Outline
**Usually skip:** Speaker Notes, Q&A Prep (unless the user plans to present it)

---

## Blog Post / Online Article

**How to identify:** HTML or markdown from a blog platform. Has a title, author, date. Conversational or semi-formal tone. Usually 500-3000 words.

**What's unique:** Already optimized for reading. Has a clear authorial voice. May be opinionated. Often lacks the rigor of academic work but is more accessible.

**Key extraction targets:**
- Core thesis or argument
- Supporting evidence and examples
- Author's unique perspective or hot takes
- Links to other resources
- Practical advice or recommendations

**Strong artifacts:** Twitter Thread, Executive Summary, Cheat Sheet (if how-to content), Slide Deck Outline, Diagram Pack, Open Research Questions (if thought-provoking)
**Usually skip:** Blog Post (source IS a blog post), Speaker Notes

---

## YouTube / Video Transcript

**How to identify:** Timestamped text, speaker labels, conversational tone. May include "[Music]", "[Applause]", or other non-speech annotations. Often has filler words.

**What's unique:** Conversational and unstructured. May have multiple speakers. Key insights are scattered among filler. Visual references ("as you can see on screen") lack context in transcript form.

**Key extraction targets:**
- Key claims and insights (filter out filler)
- Timestamps of important moments
- Speaker-specific contributions (in multi-speaker content)
- Demonstrations or examples described verbally
- Q&A sections if present

**Strong artifacts:** Blog Post, Twitter Thread, Executive Summary, Cheat Sheet, Key Numbers (if technical content), Slide Deck Outline
**Usually skip:** Speaker Notes (different format), Reproducibility Guide (unless demo-heavy)

---

## Podcast Transcript

**How to identify:** Long conversational text, multiple speakers labeled, informal tone, tangents and digressions. Usually 30-90 minutes of content.

**What's unique:** Very informal. Ideas develop through conversation, not structured argument. The best insights are often spontaneous. Lots of content to filter.

**Key extraction targets:**
- Core topics discussed (may shift multiple times)
- Key quotes and insights from each speaker
- Disagreements or debates between speakers
- Practical advice given
- Resources or references mentioned

**Strong artifacts:** Blog Post, Twitter Thread, Executive Summary, Cheat Sheet (if advice-heavy), Key Numbers (rare)
**Usually skip:** Speaker Notes, Q&A Prep, Reproducibility Guide, Annotated Bibliography (usually few formal references)

---

## Technical Documentation

**How to identify:** Structured reference material. May have version numbers, API signatures, code examples, configuration tables. Formal and precise.

**What's unique:** Reference-oriented, not narrative. Users look up specific things, not read start-to-finish. May be very large but modular.

**Key extraction targets:**
- Architecture and system design descriptions
- Key APIs, interfaces, or configuration options
- Common patterns and anti-patterns
- Migration guides or version differences
- Prerequisites and setup steps

**Strong artifacts:** Cheat Sheet, Diagram Pack, Blog Post (as a "getting started" guide), Slide Deck Outline (for teaching), Executive Summary
**Usually skip:** Twitter Thread (too technical), Speaker Notes, Q&A Prep, Annotated Bibliography

---

## Report / White Paper

**How to identify:** Formal document with executive summary, sections, possibly numbered findings or recommendations. May have charts and data. Professional tone.

**What's unique:** Goal-oriented (inform a decision, support a position). Has explicit findings or recommendations. Data-heavy. Often has an executive audience.

**Key extraction targets:**
- Key findings and recommendations
- Supporting data and charts
- Methodology (how findings were derived)
- Implications and next steps
- Limitations and caveats

**Strong artifacts:** Executive Summary, Key Numbers, Cheat Sheet, Blog Post, Twitter Thread, Slide Deck Outline, Diagram Pack
**Usually skip:** Speaker Notes, Q&A Prep (unless presenting the report), Reproducibility Guide (unless research report)

---

## Interview / Q&A

**How to identify:** Alternating question-answer format. One person asking, one or more answering. Questions may be labeled "Q:" or with interviewer name.

**What's unique:** Insights are embedded in answers to specific questions. The question framing shapes the answer. May cover many topics superficially rather than one topic deeply.

**Key extraction targets:**
- Key claims and insights from the interviewee
- Stories and anecdotes (often the most memorable parts)
- Opinions and predictions
- Recommended resources or practices
- Surprising or contrarian takes

**Strong artifacts:** Blog Post, Twitter Thread, Executive Summary, Q&A Prep (reuse the format), Cheat Sheet (if advice-heavy)
**Usually skip:** Speaker Notes, Reproducibility Guide, Annotated Bibliography

---

## Book Chapter / Long-Form Essay

**How to identify:** Extended prose (5,000-20,000+ words). Has a sustained argument or narrative. May have footnotes/endnotes. Formal or literary tone.

**What's unique:** Deep and thorough. Arguments are developed over many paragraphs. May have a complex structure. Too long to summarize in a single artifact — modular breakdown is valuable.

**Key extraction targets:**
- Central thesis and supporting arguments
- Key examples and case studies
- Definitions of important terms or concepts
- The author's unique framework or mental model
- Connections to broader debates

**Strong artifacts:** Executive Summary, Modular Outline, Blog Post, Twitter Thread, Cheat Sheet, Slide Deck Outline, Annotated Bibliography (if well-referenced), Diagram Pack
**Usually skip:** Speaker Notes, Q&A Prep, Key Numbers (unless data-heavy), Reproducibility Guide
