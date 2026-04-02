---
name: stem-tutorial
description: Build a full-featured interactive STEM tutorial web platform with AI tutor, visualizations, quizzes, and progress tracking. Supports BS, MS, PhD, and PostDoc academic levels. Invoke when user wants to create an educational tutorial for any STEM topic.
---

# STEM Tutorial Development Skill

You are building an interactive web-based STEM tutorial platform. This skill guides you through the complete lifecycle: scoping, research, curriculum design, implementation, and validation.

This is a **rigid** skill — follow every phase in order. Do not skip phases. Each phase has a gate: confirm completion before moving to the next.

---

## PHASE 0: SCOPE & LEVEL CALIBRATION

**Trigger:** User says they want to build a tutorial on a STEM topic.

**Ask the user these questions before proceeding (use AskUserQuestion or direct questions):**

1. **Topic**: What specific topic? (e.g., "dynamic programming", "organic chemistry reaction mechanisms", "quantum error correction")
2. **Level**: BS, MS, PhD, or PostDoc?
3. **Prerequisites**: What can we assume the learner already knows?
4. **Learning goal**: Pass an exam? Do research? Switch fields? General understanding?
5. **Source material**: Do you have existing content (textbooks, papers, code, lecture notes)? Provide paths/URLs.
6. **Visualization needs**: What should be interactive? (tables, graphs, simulations, molecule builders, etc.)
7. **Tech preferences**: Any framework/library requirements? (Default: Next.js + Tailwind + Framer Motion)

**Level calibration matrix — use this to set defaults:**

| Dimension | BS | MS | PhD | PostDoc |
|-----------|----|----|-----|---------|
| Depth | Intuition + worked examples | Proofs + implementation | Open problems + research connections | Frontier techniques + cross-disciplinary bridges |
| Assessment | Quizzes, coding exercises | Proofs, implementations, mini-projects | Paper critiques, proof extensions, research proposals | Reproduce results, extend methods, identify gaps |
| AI Tutor tone | Patient TA, analogies, hints-first | Rigorous, proof-oriented, implementation-focused | Research advisor, references papers, Socratic | Colleague, translates notation, efficient |
| Visualizations | Step-by-step animations | Animations + parameter exploration | Experiment sandboxes + paper walkthroughs | Technique comparisons + research notebooks |

**Output:** Save a `tutorial-scope.md` file in the project root with all decisions documented.

**Gate:** User confirms the scope before proceeding.

---

## PHASE 1: CONTENT DISCOVERY & CURATION

**Goal:** Gather and organize all source material into structured content.

### For BS/MS level:

1. Identify the canonical textbook(s) or reference material for the topic
2. If source material was provided, read it thoroughly — extract:
   - Problem/concept list with progressive difficulty
   - Worked examples with inputs and expected outputs
   - Recurrences, formulas, theorems, key definitions
   - Complexity analysis or key properties
3. If NO source material exists, use WebSearch to find:
   - Widely-used open textbooks or course notes
   - Canonical problem sets
   - Well-known visualizations or demonstrations
4. For each concept/problem, document:
   - Title, difficulty, category/pattern
   - Problem statement
   - Core formula/recurrence/theorem
   - State definition (what are we computing?)
   - Base cases / boundary conditions
   - Worked example with specific values
   - Common misconceptions
5. Map each concept to a visualization type:
   - Table filling → animated grid
   - Graph algorithm → node/edge animation
   - Mathematical function → interactive plot
   - Physical system → simulation
   - Chemical structure → molecule builder
   - Proof → step-by-step proof stepper

### For PhD/PostDoc level — perform ALL of the above PLUS Phase 1.5 (Research Stage).

**Output:** Create `src/data/content-inventory.md` listing all concepts with their metadata.

**Gate:** User reviews and approves the concept list.

---

## PHASE 1.5: RESEARCH STAGE (PhD/PostDoc ONLY)

**Skip this phase for BS and MS levels.**

This phase is MANDATORY for PhD and PostDoc tutorials. It ensures content accuracy and research relevance.

### Step 1: Literature Mapping

Use WebSearch and WebFetch to find:
- The 3-5 most cited **survey papers** in the subfield
- The **seminal/foundational papers** (high citation, older)
- The most impactful **recent papers** (last 2-3 years)
- Key **graduate textbook** chapters if they exist
- Active **research groups** and their focus areas

Create `src/data/research/reading-list.md`:
```markdown
# Reading List: [Topic]

## Foundational Papers
- [Author, Year] "Title" — Why it matters: ...

## Survey Papers
- [Author, Year] "Title" — Covers: ...

## Recent Advances
- [Author, Year] "Title" — Key contribution: ...

## Textbook References
- [Author] "Book Title", Chapters X-Y
```

### Step 2: Technique Inventory

For each technique/method being taught, document:
- What problem does it solve?
- What are the assumptions and limitations?
- What are the alternatives and trade-offs?
- Is there a canonical implementation or reference code?
- What are common failure modes practitioners encounter?
- What are the known open extensions?

Create `src/data/research/techniques.md`.

### Step 3: Open Problem Identification

Document:
- Known open questions in the subfield
- Active areas of debate or controversy
- Recent results that changed conventional wisdom
- Opportunities for new researchers
- Connections to adjacent fields

Create `src/data/research/frontier.md`. This content feeds into "Research Connections" sections in the tutorial.

### Step 4: Notation & Convention Audit

Different papers and communities use different notation. This is critical for PostDoc-level tutorials where learners are switching fields.

- Identify notation conflicts across sources
- Establish a consistent convention for the tutorial
- Create a notation glossary

Create `src/data/research/notation.md`.

### Step 5: Accuracy Risk Assessment

- Flag any content where AI might hallucinate (niche results, recent findings)
- Mark sections that need human expert review
- Identify numerical results that must be verified computationally

Create `src/data/research/validation-checklist.md`.

**Gate:** User reviews research artifacts. Confirm before building.

---

## PHASE 2: CURRICULUM DESIGN

**Goal:** Structure content into a progressive curriculum before writing any code.

### Define module sequence

Create `src/data/curriculum.md`:

```markdown
# [Topic] Tutorial — Curriculum

## Module 1: [Title]
- **Prerequisites:** [what learner needs]
- **Learning objectives:** [what they'll be able to do after]
- **Core content:** [theory + worked examples]
- **Visualization:** [what's interactive — describe the component]
- **Practice:** [problems with solutions]
- **Assessment:** [quiz questions, coding exercises, etc.]
- **[PhD/PostDoc] Research connections:** [papers, open problems]

## Module 2: [Title]
...
```

### Define assessment strategy by level

- **BS:** Multiple-choice, fill-blank, short coding exercises. AI grades automatically.
- **MS:** Proofs (AI-graded free response), implementations (AI code review), mini-project prompts.
- **PhD:** Paper critique prompts, proof extension exercises, "propose a research direction" open-ended questions. AI provides feedback, not definitive grades.
- **PostDoc:** "Reproduce this result" challenges, "apply this technique to your domain" exercises, cross-domain connection prompts.

### Define AI tutor persona

Write the system prompt for the AI tutor, calibrated to level:

```
BS:  "You are a patient, encouraging TA. Give hints before answers.
      Use analogies. Keep it accessible."

MS:  "You are a rigorous instructor. Give proof sketches when asked.
      Expect mathematical maturity. Point out edge cases."

PhD: "You are a research advisor. Reference specific papers. When
      stuck, suggest which paper section to read. Point out
      connections to adjacent fields. Flag open problems."

PostDoc: "You are a colleague helping someone transition into this
          field. Translate notation from their background. Be direct
          and efficient. Focus on what transfers vs. what breaks."
```

### Define visualization requirements

For each module, specify:
- Component type (table, graph, plot, simulation, proof-stepper, molecule-builder, etc.)
- Input parameters the learner can modify
- What state changes should be animated
- What the "step" granularity is

**Output:** `src/data/curriculum.md` with complete module definitions.

**Gate:** User approves curriculum structure.

---

## PHASE 3: PROJECT SCAFFOLDING

**Goal:** Set up the project with all dependencies and directory structure.

### Default tech stack (override if user specified preferences in Phase 0):

| Layer | Choice |
|-------|--------|
| Framework | Next.js (App Router) |
| Styling | Tailwind CSS |
| Animations | Framer Motion |
| Code Editor | Monaco Editor (`@monaco-editor/react`) — if homework involves coding |
| Charts | Recharts — if progress/skill visualization needed |
| Math Rendering | KaTeX — if formulas need rendering (MS/PhD/PostDoc) |
| AI | OpenRouter (routes to Claude, GPT-4, Gemini — user picks model) |
| Persistence | localStorage (no DB for MVP) |

### Directory structure

```
[project]/
├── src/
│   ├── app/                    # Next.js pages
│   │   ├── layout.tsx          # Root layout, navbar, theme
│   │   ├── page.tsx            # Landing/dashboard
│   │   ├── modules/            # Per-module pages
│   │   │   ├── page.tsx        # Module list
│   │   │   └── [slug]/
│   │   │       ├── page.tsx    # Module detail + visualizer
│   │   │       ├── quiz/       # Per-module quiz
│   │   │       └── homework/   # Per-module homework
│   │   ├── exams/              # Exam pages
│   │   ├── progress/           # Progress dashboard
│   │   ├── theory/             # Full theory reference
│   │   ├── settings/           # API key, model, theme
│   │   └── api/ai/             # AI API routes
│   ├── components/
│   │   ├── visualizer/         # Domain-specific visualizations
│   │   ├── tutor/              # AI chat sidebar
│   │   ├── quiz/               # Quiz components
│   │   ├── editor/             # Code editor + feedback
│   │   ├── progress/           # Charts, badges, streaks
│   │   ├── proof/              # [MS/PhD/PostDoc] Proof stepper
│   │   ├── research/           # [PhD/PostDoc] Paper reader, notebook
│   │   └── ui/                 # Shared UI primitives
│   ├── data/
│   │   ├── modules/            # One file per module (metadata + content)
│   │   ├── quizzes/            # Static quiz banks
│   │   ├── exams/              # Exam definitions
│   │   └── research/           # [PhD/PostDoc] Literature, notation
│   ├── lib/
│   │   ├── engine/             # Domain-specific computation engine
│   │   │   ├── types.ts        # Core type definitions
│   │   │   ├── runner.ts       # Step-by-step execution
│   │   │   └── algorithms/     # Per-module algorithm implementations
│   │   ├── ai/                 # AI client, prompts, rate limiter
│   │   └── storage/            # localStorage persistence
│   └── hooks/                  # React hooks
├── .env.example
├── next.config.ts
└── package.json
```

### Actions:
1. Create project directory, run `npm init`, install dependencies
2. Create config files (tsconfig, postcss, next.config, .env.example)
3. Create globals.css with theme variables (pick a distinctive aesthetic per the frontend-design skill)
4. Create the full directory structure
5. Define core TypeScript types in `src/lib/engine/types.ts`:
   - `Module` (replaces DPProblem — generic for any STEM topic)
   - `Step` (visualization state snapshot)
   - `Algorithm` (run + solve interface)
   - `QuizQuestion`, `Exam`, `UserProgress`, `AISettings`
   - [PhD/PostDoc] `Paper`, `ResearchNote`, `NotationEntry`

**Gate:** Project scaffolds and `npx tsc --noEmit` passes.

---

## PHASE 4: PARALLEL BUILD

**Goal:** Build all independent modules in parallel using a team of agents.

### Create a team with TeamCreate, then spawn agents for these independent workstreams:

**Agent 1: Layout & Landing Page**
- Root layout with navbar, theme toggle, responsive design
- Landing page with module grid, course overview, CTAs
- Follow the frontend-design skill for distinctive aesthetics

**Agent 2: Module Data Extraction**
- Create one data file per module from the curriculum + source material
- Each file exports a Module object with all fields
- Create index file with exports

**Agent 3: Computation Engine**
- Implement each module's algorithm/computation in TypeScript
- Each produces Step[] arrays for the visualizer
- Deep-copy state at each step
- Include reconstruction/backtracking steps

**Agent 4: AI Integration**
- OpenRouter client (streaming + non-streaming)
- System prompts for all personas (tutor, grader, quiz-gen, reviewer)
- Context builder (injects current module state into prompts)
- Rate limiter
- All API routes (chat, quiz-generate, grade, feedback)

**After first wave completes, spawn second wave:**

**Agent 5: Visualizer Components**
- Domain-specific visualization components
- Step controls (play/pause/step/speed)
- Input editor for parameter modification
- Main visualizer wrapper

**Agent 6: All Other Components**
- AI tutor sidebar
- Quiz system (multiple choice, coding, free response)
- Code editor (Monaco, dynamic import)
- Progress components (radar chart, badges, streak)
- UI primitives (button, card, modal, badges)
- [MS/PhD/PostDoc] Proof stepper component
- [PhD/PostDoc] Paper reader, research notebook components

**Agent 7: Page Routes & Wiring (depends on all above)**
- Quiz data files, exam definitions
- All page routes wired to components and data
- Storage hooks (progress, settings, timer)

### Level-specific components to include:

| Component | BS | MS | PhD | PostDoc |
|-----------|:--:|:--:|:---:|:------:|
| Animated visualizer | Yes | Yes | Yes | Yes |
| Code editor + AI grading | Yes | Yes | Yes | Maybe |
| Quiz system | Yes | Yes | Yes | Maybe |
| Proof stepper | No | Yes | Yes | Yes |
| Paper reader panel | No | No | Yes | Yes |
| Research notebook | No | No | Yes | Yes |
| Notation glossary sidebar | No | No | Yes | Yes |
| "Research Connections" sections | No | No | Yes | Yes |
| Cross-domain bridge notes | No | No | No | Yes |

**Gate:** All agents complete. `npx tsc --noEmit` passes.

---

## PHASE 5: INTEGRATION & WIRING

**Goal:** Connect all pieces and verify the app works end-to-end.

### Checklist:
- [ ] All page routes render without errors
- [ ] Navigation between all pages works
- [ ] Visualizer plays through all modules' steps correctly
- [ ] AI tutor responds with streaming (test with BYOK key)
- [ ] Quiz flow: answer questions → see score → save to progress
- [ ] Homework flow: write code → submit → see AI feedback → save score
- [ ] Exam flow: start → timer → answer → auto-submit → see results
- [ ] Progress page shows completion, scores, skill chart, badges
- [ ] Settings page: API key, model picker, theme toggle all persist
- [ ] Dark/light mode works on all pages
- [ ] [PhD/PostDoc] Research connections render, paper references link correctly

### Run the build:
```bash
npm run build
```
Fix any build errors. This is the final integration check.

**Gate:** `npm run build` succeeds with zero errors.

---

## PHASE 6: VALIDATION & REVIEW

**Goal:** Verify correctness, pedagogy, and usability.

### Content Accuracy Check
- For each module, run the computation engine and verify outputs match known correct values
- If source material has worked examples, compare step-by-step
- [PhD/PostDoc] Cross-reference claims against cited sources. Flag anything unsupported.

### Pedagogical Review
- Does the difficulty progression make sense?
- Are prerequisites actually sufficient?
- Are assessments aligned with learning objectives?
- Do visualizations aid understanding or just look pretty?

### AI Tutor Testing
- Ask the tutor common questions at the target academic level
- Verify it calibrates responses appropriately (not too simple, not too advanced)
- Verify it doesn't hallucinate facts
- [PhD/PostDoc] Verify it references real papers and techniques

### Usability Check
- Mobile responsive (test at 375px viewport)
- Dark/light mode — no broken contrast
- Keyboard navigation works
- Math rendering (KaTeX) displays correctly if used
- Code editor loads without blocking page

### Use the code-reviewer agent:
Spawn `superpowers:code-reviewer` agent to review the full implementation against the curriculum plan and coding standards.

**Gate:** All checks pass. Report findings to user.

---

## PHASE 7: DEPLOYMENT & HANDOFF

1. Ensure `.env.example` documents all required environment variables
2. Verify `npm run build` produces clean output
3. If user wants to deploy: guide them through Vercel deployment
4. Create a brief README.md at project root documenting:
   - What the tutorial covers
   - How to run locally
   - How to configure AI (BYOK vs hosted key)
   - How to add new modules

**Done.** Report the final summary to the user.

---

## QUICK REFERENCE: LEVEL-SPECIFIC ADDITIONS

When the user specifies a level, use this checklist to ensure all level-specific features are included:

### PhD Level — Extra Requirements
- [ ] Phase 1.5 (Research Stage) completed
- [ ] reading-list.md, techniques.md, frontier.md, notation.md created
- [ ] AI tutor uses "research advisor" persona
- [ ] Modules include "Research Connections" sections
- [ ] Proof stepper component included
- [ ] Paper reader component included
- [ ] Assessment includes open-ended research exercises
- [ ] Notation glossary sidebar available

### PostDoc Level — Extra Requirements (all PhD requirements PLUS):
- [ ] AI tutor uses "colleague" persona with field-translation focus
- [ ] Notation audit emphasizes cross-field convention differences
- [ ] Modules include "Cross-Domain Bridges" sections
- [ ] Research notebook component for capturing insights
- [ ] "Apply to Your Domain" exercises in assessments
- [ ] Prerequisite sections focus on "what transfers vs. what breaks"
