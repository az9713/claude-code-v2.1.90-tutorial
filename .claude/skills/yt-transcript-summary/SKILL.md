---
name: yt-transcript-summary
description: Analyze YouTube videos, web pages (blog posts, articles), or local files (TXT, HTML, PDF) using Google Gemini API. Extracts key takeaways, summaries, code, prompts, and more.
triggers:
  - summarize youtube video
  - summarize youtube
  - summarize transcript
  - analyze youtube
  - analyze video
  - yt summary
  - yt transcript
  - youtube takeaways
  - extract from video
  - summarize article
  - summarize blog post
  - analyze web page
  - analyze url
---

# YouTube, Web & File Content Analyzer

Analyze YouTube videos, web pages (blog posts, articles), or local files (TXT, HTML, PDF) using Google Gemini API via the `yt_analyze.py` CLI tool.

## Script Location

The script and supporting files are co-located with this skill:

```
~/.claude/skills/yt-transcript-summary/
├── SKILL.md
└── scripts/
    ├── yt_analyze.py
    ├── my_prompt.txt
    └── requirements.txt
```

**Script dir:** `~/.claude/skills/yt-transcript-summary/scripts/`

## How to Build the Command

Parse the user's request for these inputs:

| Input | How to pass it |
|-------|---------------|
| YouTube URL | Positional argument: `python yt_analyze.py "URL"` |
| Web page URL (blog, article) | Positional argument: `python yt_analyze.py "URL"` (auto-detected as non-YouTube) |
| Local file path (txt, html, pdf) | `--file "path/to/file.ext"` |
| Custom prompt (inline text) | `-p "prompt text"` |
| Built-in preset | `--builtin <preset>` |
| Transcript mode | `--transcript` (optionally `--speakers "Name1" "Name2"`) |
| Segment analysis (YouTube only) | `--start MM:SS --end MM:SS` |
| Custom output path | `-o "output.md"` |

**URL and `--file` are mutually exclusive** — the script enforces this.

### Source Type Detection

The script automatically detects the source type:

- **YouTube URL** (youtube.com, youtu.be) → sends video directly to Gemini via `file_data`
- **Web page URL** (any other http/https URL) → fetches the page, extracts text (strips HTML), sends text to Gemini
- **Local file** (`--file`) → reads the file based on extension:
  - `.txt`, `.md`, `.json`, `.csv`, etc. → read as plain text
  - `.html`, `.htm` → parse HTML tags, extract text content
  - `.pdf` → extract text from all pages using pdfplumber

## Multiple URLs

The user may provide multiple URLs in a single request, separated by commas, spaces, or newlines. They can be a mix of YouTube and web page URLs. For example:

```
/yt-transcript-summary https://youtube.com/watch?v=abc, https://example.com/blog-post, https://youtube.com/watch?v=def
```

When multiple URLs are detected:

1. **Parse** all URLs from the input (split on commas, spaces, or newlines; filter to valid URLs).
2. **Process each URL sequentially** — run a separate `python yt_analyze.py "URL" <shared-flags>` command for each URL. All other flags (e.g., `-p`, `--builtin`, `--transcript`) apply to every URL.
3. **Report progress** — after each URL completes, tell the user which source finished and its output file path before moving to the next.
4. **Summarize at the end** — after all sources are processed, list all output file paths together.

Do **not** run multiple URLs in parallel — the Gemini API may rate-limit concurrent requests.

## Prompt Resolution Order

1. If the user says "transcript mode" or wants a transcript → use `--transcript`
2. If the user names a built-in preset → use `--builtin <preset>`
3. If the user provides an inline prompt → use `-p "their prompt"`
4. Otherwise → omit prompt flags (the script defaults to reading `my_prompt.txt`)

### Available Built-in Presets

`summary`, `summary-full`, `summarize-tests`, `takeaways`, `extract-code`, `extract-python`, `extract-notebook-code`, `extract-notebook-cells`, `extract-prompts`, `extract-system-prompts`, `extract-markdown`, `extract-markdown-contents`, `extract-source-and-markdown`, `extract-text`, `extract-commands`, `extract-terminal`, `extract-slides`, `extract-prompts-and-responses`, `extract-all`, `extract-task-instructions`, `extract-skills`, `extract-agentic-prompts`, `extract-claude-md`, `extract-prd`, `extract-workflow-md`, `extract-settings-json`, `extract-spec-md`, `extract-imagen-prompts`, `extract-veo-prompts`, `extract-music-prompts`, `extract-pipeline-yaml`, `extract-input-text`, `extract-tree-view`, `extract-workflow`

## Execution

Run the command via `Bash` from the **user's current working directory** (never `cd` into the script directory). Use the full path to the script:

```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py <args>
```

The output `.md` file will be written to the user's current working directory. The script prints the output path to stderr. After execution, tell the user the output file path.

**Important:** Never output files to the skill's scripts directory. Always run from the user's cwd.

## Examples

**YouTube URL with default prompt:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.youtube.com/watch?v=abc123"
```

**Web page (blog post, article):**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.latent.space/p/turbopuffer"
```

**Local HTML file:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py --file "article.html"
```

**Local PDF file:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py --file "paper.pdf"
```

**Local transcript file:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py --file "/path/to/transcript.txt"
```

**Custom inline prompt:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.youtube.com/watch?v=abc123" -p "Extract all code snippets"
```

**Built-in preset:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.youtube.com/watch?v=abc123" --builtin takeaways
```

**Transcript mode with speakers:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.youtube.com/watch?v=abc123" --transcript --speakers "Alice" "Bob"
```

**Segment analysis:**
```bash
python ~/.claude/skills/yt-transcript-summary/scripts/yt_analyze.py "https://www.youtube.com/watch?v=abc123" --start 01:30 --end 05:00 -p "Summarize this segment"
```

## Prerequisites

- `GOOGLE_API_KEY` must be set (in `.env` or environment)
- Python dependencies: `pip install -r requirements.txt` (google-genai, python-dotenv, jinja2, requests, beautifulsoup4, pdfplumber)
