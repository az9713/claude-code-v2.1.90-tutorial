---
name: excalidraw-sketch
description: Create hand-drawn editorial illustration diagrams in Excalidraw with a sketchy, annotated, character-driven style. Use for AI workflow illustrations, technical comparisons, concept explanations, and visual storytelling.
---

# Excalidraw Sketch — Editorial Illustration Style

Generate `.excalidraw` JSON files in a **hand-drawn, editorial illustration style** — sketchy, annotated, character-driven diagrams for explaining AI workflows, technical concepts, and comparisons.

This skill builds on the base `excalidraw` skill. Use the same render pipeline, element templates, and JSON schema from `../excalidraw/references/`. The difference is purely **aesthetic and compositional** — this skill defines a specific visual language.

---

## Reference Samples (MUST READ)

**Before generating any diagram, read the sample images** in `references/` to internalize the target style:

- `references/sample.jpg` — Side-by-side comparison: "Human Interruption" vs "LLM Context Pollution". Shows two-panel layout with robot mascot in each, thick flow arrow between panels, speech/thought bubbles, scattered annotation labels, red X for negative, code windows.
- `references/sample2.jpg` — Top statement + two-panel layout: "/btw Quick Questions" vs "--fork-session Deep Dives". Shows problem statement at top with downward arrow, robot waving in left panel, robot at laptop in right panel, annotation arrows to icons (magnifying glass, gears, HTML/mermaid artifacts).
- `references/sample3.jpg` — Side-by-side with detail sub-row: "Messy Desk" (red X, overwhelmed robot buried in papers, scattered symbols) vs "Clean Desk" (green check, organized robot, thought bubble with progress bar/target). Bottom row shows 3 smaller robot figures demonstrating individual tools (Esc, /rewind, --fork-session, /btw).
- `references/sample4.jpg` — Three-stage sequential flow left-to-right: "Claude Mid-Task" → "Noise in Conversation History" → "Impact: Drowned Signal". Shows robot working with code windows, human figure interrupting with speech bubble, conversation history panel with red X, confused robot surrounded by scattered documents.

**Use these samples as your ground truth** for:
- Robot mascot proportions, shape, and likeness (round head, glowing blue circular eyes, metallic silver-blue body, small blue chest screen, stubby limbs, antenna nub)
- Annotation density and placement style
- How speech/thought bubbles look
- The overall warmth and editorial feel
- Layout composition and scene staging
- How contrast is used (messy/scattered vs. clean/organized)

---

## Style Identity

This style mimics hand-drawn whiteboard sketches used in tech blog posts and YouTube explainers. Key traits:

- **Rough, organic lines** — nothing perfectly straight
- **Casual handwritten text** — like someone sketched it on a whiteboard
- **Heavy annotation** — arrows, labels, callouts everywhere
- **Character-driven scenes** — a recurring robot mascot or simple human figures inhabit each scene
- **Muted, soft palette** — blues, grays, cream, with selective pops of red/green/yellow for emphasis
- **Visual storytelling** — each section is a mini-scene, not a static box-and-arrow diagram

---

## Excalidraw Settings (Apply to ALL Elements)

These settings create the hand-drawn aesthetic:

| Property | Value | Why |
|----------|-------|-----|
| `roughness` | `2` | Maximum hand-drawn wobble — this is the core of the style |
| `fontFamily` | `1` | Virgil (hand-drawn font) — never use monospace or sans-serif |
| `strokeWidth` | `1` for annotations, `2` for shapes, `3` for major arrows | Visual hierarchy through line weight |
| `opacity` | `100` | Always fully opaque |
| `roundness` | `{ "type": 3 }` on rectangles | Rounded corners for a softer, sketchier feel |

---

## Color Palette (Sketch Style)

This replaces the base skill's color palette. All colors below are tuned for the soft, muted, editorial look.

### Shape Fills & Strokes

| Semantic Purpose | Fill | Stroke | When to Use |
|------------------|------|--------|-------------|
| Robot body / neutral | `#e8edf3` | `#5b6e85` | Robot mascot shapes, neutral containers |
| Robot eye glow | `#7dd3fc` | `#0284c7` | Robot eye circles |
| Robot chest screen | `#38bdf8` | `#0369a1` | Small rectangle on robot body |
| Panel border | `transparent` | `#94a3b8` | Hand-drawn rounded rectangles framing scenes |
| Good / positive | `#bbf7d0` | `#16a34a` | Green checkmarks, success indicators |
| Bad / negative | `#fecaca` | `#dc2626` | Red X marks, error indicators |
| Warning / attention | `#fef08a` | `#ca8a04` | Yellow highlights, exclamation marks |
| Code window | `#1e293b` | `#475569` | Dark rectangles representing terminal/editor |
| Document / file | `#fefce8` | `#a3a3a3` | Paper-like rectangles for documents |
| Thought bubble | `#f8fafc` | `#94a3b8` | Cloud shapes for thought content |
| Speech bubble | `#ffffff` | `#64748b` | Rounded rectangles with tail for dialogue |
| UI mockup | `#f1f5f9` | `#94a3b8` | Light rectangles representing screens/windows |
| Arrow (flow) | — | `#64748b` | Thick gray arrows between scenes |
| Arrow (annotation) | — | `#94a3b8` | Thinner arrows pointing from labels to elements |

### Text Colors

| Level | Color | Font Size | Use For |
|-------|-------|-----------|---------|
| Diagram title | `#1e293b` | `28-36` | Main title spanning the top |
| Section subtitle | `#334155` | `20-24` | Panel/scene headers |
| Label / annotation | `#475569` | `14-16` | Callout text, small labels |
| Caption | `#64748b` | `14-16` | Explanatory text below scenes |
| Emphasis text | `#dc2626` or `#16a34a` | `16-20` | Key terms, red for bad, green for good |
| On dark background | `#e2e8f0` | `12-14` | Text inside code windows |

### Background

| Property | Value |
|----------|-------|
| Canvas background | `#faf9f6` | Warm cream, not pure white |

---

## Character: Robot Mascot

**Read the sample images first** (`references/sample*.jpg`) to see the target robot likeness. The robot in the samples has: a round-ish head slightly wider than tall, two large glowing blue circular eyes (prominent, ~40% of head width), a compact metallic body with a small bright blue screen on the chest, short stubby arms and legs, and a small antenna nub on top. The overall proportions are chibi/cute — large head relative to body.

The recurring robot character is built from basic Excalidraw shapes to approximate this likeness:

### Robot Construction (approximate element sizes)

```
Head:       rectangle, 50×45, rounded, fill #e8edf3, stroke #5b6e85
Eyes:       2× ellipse, 12×12, fill #7dd3fc, stroke #0284c7
Body:       rectangle, 40×50, rounded, fill #e8edf3, stroke #5b6e85
Chest screen: rectangle, 20×15, fill #38bdf8, stroke #0369a1 (centered on body)
Arms:       2× line, strokeWidth 2, stroke #5b6e85 (short lines from body sides)
Legs:       2× line, strokeWidth 2, stroke #5b6e85 (short lines from body bottom)
Antenna:    line + small ellipse on top of head
```

### Robot Variations (convey state through context, not complex poses)

| State | How to Show |
|-------|-------------|
| Working/focused | Robot next to a code window or laptop shape, small gear icons nearby |
| Confused | Question marks (`?`) and scattered symbols around the robot's head |
| Overwhelmed | Piles of document rectangles surrounding the robot |
| Presenting/explaining | Robot with a speech bubble, one arm line angled outward |
| Happy/success | Green checkmark nearby, clean organized elements around |
| Error/problem | Red X mark nearby, scattered messy elements |

### Human Figure (when needed)

Simple silhouette: ellipse head (20×20) + rectangle body (15×30), fill `#94a3b8`, stroke `#475569`. With a speech bubble for dialogue.

---

## Annotation System

This style is **annotation-heavy**. Every scene should have multiple callout labels.

### Annotation Elements

| Element | How to Build |
|---------|-------------|
| **Callout label** | Free-floating text (14-16px, color `#475569`) + thin arrow (strokeWidth 1, stroke `#94a3b8`) pointing to the target |
| **Speech bubble** | Rounded rectangle (fill `#ffffff`, stroke `#64748b`) with hand-written text inside. Add a small triangle line below for the tail. |
| **Thought bubble** | Ellipse (fill `#f8fafc`, stroke `#94a3b8`) with wavy/cloud-like feel. Place 2-3 small ellipses trailing toward the character. |
| **Red X** | Two crossing lines (stroke `#dc2626`, strokeWidth 3) — 30×30 |
| **Green check** | Two lines forming a checkmark (stroke `#16a34a`, strokeWidth 3) |
| **Question marks** | Free-floating text `?` in various sizes (16-28px), scattered, color `#ca8a04` or `#dc2626` |
| **Exclamation marks** | Free-floating text `!` (20-28px), color `#ca8a04` |
| **Scattered symbols** | Small text elements (`@`, `#`, `%`, `*`, `?`) in varied sizes around a focal point to convey noise/chaos |
| **Icon: gear** | Small diamond (20×20) or use text `⚙` |
| **Icon: magnifying glass** | Small ellipse (15×15) + short line for handle |

### Annotation Density

Aim for **5-10 annotation labels per scene/panel**. Each major element should have at least one label pointing to it. This density is what gives the style its editorial/explainer character.

---

## Layout Patterns

Choose the layout that fits the concept. These can be combined.

### Pattern 1: Side-by-Side Comparison

Two panels with hand-drawn rounded-rectangle borders. Used for before/after, good/bad, two approaches.

```
┌─────────────────┐    ┌─────────────────┐
│  ✗ Bad Title     │    │  ✓ Good Title    │
│                  │    │                  │
│   [robot scene]  │ →  │   [robot scene]  │
│                  │    │                  │
│  caption text    │    │  caption text    │
└─────────────────┘    └─────────────────┘
```

- Panel width: 500-700 each
- Gap between panels: 80-120
- Optional thick arrow or label between panels
- Red X icon on "bad" panel title, green checkmark on "good" panel title

### Pattern 2: Sequential Flow (Left to Right)

3+ scenes arranged horizontally with thick directional arrows between them. Used for processes, chains of events, cause-and-effect.

```
[Scene 1]  ──→  [Scene 2]  ──→  [Scene 3]
 subtitle        subtitle        subtitle
 robot +         robot +         robot +
 context         context         context
 caption         caption         caption
```

- Each scene is a loose grouping (no border required, or light dashed border)
- Thick gray arrows (strokeWidth 3) between scenes
- Each scene has: subtitle above, robot + context elements in middle, caption below
- Scene width: 300-500 each

### Pattern 3: Top Statement + Detail Row

A headline statement or problem at the top, with an arrow pointing down to a row of smaller scenes/solutions below.

```
        ┌──────────────────────────┐
        │    Problem Statement     │
        └────────────┬─────────────┘
                     ↓
    [solution 1]  [solution 2]  [solution 3]
```

- Top element is prominent (large text, bordered)
- Downward arrow to the detail row
- Detail row items are smaller scenes with robots

### Pattern 4: Hub and Spoke

Central concept with radiating connections to surrounding elements. Used for "one thing connects to many."

### Pattern 5: Mixed / Free-Form

Combine any patterns above. Common: comparison panels at top + detail row at bottom. Or sequential flow with an inset detail panel.

### Layout Constants

| Spacing | Value |
|---------|-------|
| Between major scenes | `100-150px` |
| Between elements within a scene | `30-50px` |
| Panel padding (if bordered) | `40-60px` |
| Title to first panel | `60-80px` |
| Robot size (total height) | `100-130px` |
| Minimum scene width | `300px` |

---

## Composition Rules

1. **Bold title always at the top** — 28-36px, centered, spanning the full diagram width
2. **Every scene has a robot** (or human figure) — characters make it editorial, not just a flowchart
3. **Surround characters with context** — icons, documents, code windows, speech bubbles create the "scene"
4. **Annotate aggressively** — if something could have a label, give it one
5. **Use scattered symbols for chaos/noise** — question marks, random punctuation, jumbled text to show "messy" states
6. **Use organized, clean shapes for order** — neat stacks, aligned elements, checkmarks to show "clean" states
7. **Contrast is storytelling** — messy vs. clean, red vs. green, scattered vs. organized
8. **Captions ground each scene** — 1-2 sentences below each panel/scene explaining the takeaway

---

## Design Process

### Step 0: Study the Reference Samples
Read the sample images in `references/sample*.jpg` using the Read tool. Internalize the robot likeness, annotation style, scene composition, and overall feel. Every diagram you produce should look like it belongs in the same series as these samples.

### Step 1: Determine Layout Pattern
Based on the concept, pick from the layout patterns above (or combine them).

### Step 2: Plan Scenes
For each scene/panel:
- What is the robot doing?
- What context objects surround it? (code windows, documents, chat bubbles, etc.)
- What annotations/callouts label the key elements?
- What's the caption/takeaway?

### Step 3: Build Section by Section
Follow the base excalidraw skill's section-by-section workflow:
1. Create the base file with title + first scene
2. Add one scene per edit pass
3. Use descriptive string IDs (e.g., `"robot1_head"`, `"panel_bad_border"`)
4. Namespace seeds by section

### Step 4: Render & Validate
Use the base skill's render pipeline:
```bash
cd .claude/skills/excalidraw/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```
Then Read the PNG and run the fix loop.

### Sketch-Specific Checks (in addition to base skill checks)
- [ ] `roughness: 2` on all shapes and lines
- [ ] `fontFamily: 1` (Virgil) on all text
- [ ] Canvas background is `#faf9f6` (cream, not white)
- [ ] Every scene has a robot or human character
- [ ] At least 5 annotation callouts per scene
- [ ] Scattered symbols used for "chaos/noise" states
- [ ] Red/green color coding for bad/good contrast
- [ ] Thick gray arrows (strokeWidth 3) between major scenes
- [ ] Captions present below each scene/panel

---

## Quality Checklist

### Style
1. **Hand-drawn feel**: roughness 2, Virgil font, rounded corners — nothing looks "clean/corporate"
2. **Character presence**: Every scene has a robot or human figure
3. **Annotation density**: 5-10 callouts per scene, not sparse
4. **Color restraint**: Muted blues/grays dominate, with selective red/green/yellow pops
5. **Warm background**: Cream (`#faf9f6`), not cold white

### Composition
6. **Bold title**: Large, centered, at the top
7. **Scene separation**: Clear visual boundaries between scenes (borders, whitespace, or arrows)
8. **Caption grounding**: Each scene has explanatory text below
9. **Flow direction**: Clear reading path (left-to-right or top-to-bottom)
10. **Balanced weight**: No scene overwhelms or gets lost

### Storytelling
11. **Contrast**: Bad/good, messy/clean, before/after conveyed through visual elements (not just text)
12. **Context objects**: Each robot is surrounded by relevant props (code windows, documents, chat bubbles)
13. **Scattered symbols**: Chaos states use scattered `?`, `!`, `@`, `#` symbols
14. **Emotional clarity**: The robot's situation is immediately understandable from context

### Technical
15. **Valid JSON**: Passes Excalidraw import
16. **Rendered & validated**: PNG reviewed, no overlaps, clipping, or broken arrows
17. **Descriptive IDs**: All elements have readable string IDs
