"""
YouTube Video & Web Content Analyzer using Google Gemini API.

Analyze YouTube videos, web pages (blog posts, articles), or local files
(TXT, HTML, PDF) with custom prompts or generate transcripts.
"""

import argparse
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from jinja2 import Template

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}


def is_youtube_url(url):
    """Check if a URL is a YouTube video URL."""
    try:
        parsed = urlparse(url)
        return parsed.hostname in YOUTUBE_HOSTS
    except Exception:
        return False


def is_url(s):
    """Check if a string looks like a URL."""
    try:
        parsed = urlparse(s)
        return parsed.scheme in ("http", "https") and bool(parsed.hostname)
    except Exception:
        return False


def fetch_web_content(url):
    """Fetch a web page and extract its text content."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "pdf" in content_type:
        return extract_pdf_from_bytes(resp.content)

    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    return text


def read_local_file(file_path):
    """Read a local file, handling different formats (txt, html, pdf)."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_from_file(file_path)
    elif ext in (".html", ".htm"):
        return extract_text_from_html_file(file_path)
    else:
        # Default: read as plain text
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


def extract_pdf_from_file(file_path):
    """Extract text from a local PDF file."""
    import pdfplumber
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_pdf_from_bytes(content_bytes):
    """Extract text from PDF bytes (e.g. fetched from a URL)."""
    import io
    import pdfplumber
    text_parts = []
    with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_html_file(file_path):
    """Extract text from a local HTML file."""
    from bs4 import BeautifulSoup
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def get_api_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        print("Error: GOOGLE_API_KEY is not set.")
        print("Add it to .env file:  GOOGLE_API_KEY=your-key-here")
        print("Or get a key at https://aistudio.google.com/apikey")
        sys.exit(1)
    return key


def analyze_video(client, model, youtube_url, prompt):
    response = client.models.generate_content(
        model=model,
        contents=types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(file_data=types.FileData(file_uri=youtube_url)),
            ]
        ),
    )
    return response.text


def analyze_text_content(client, model, text, prompt):
    """Analyze text content (from a file, web page, etc.) with a prompt."""
    response = client.models.generate_content(
        model=model,
        contents=types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(text=text),
            ]
        ),
    )
    return response.text


def analyze_transcript_file(client, model, file_path, prompt):
    text = read_local_file(file_path)
    return analyze_text_content(client, model, text, prompt)


def analyze_web_page(client, model, url, prompt):
    """Fetch a web page and analyze its text content."""
    print(f"Fetching web content from: {url}", file=sys.stderr)
    text = fetch_web_content(url)
    if not text or len(text.strip()) < 50:
        print(f"Warning: Very little text extracted from {url}", file=sys.stderr)
    return analyze_text_content(client, model, text, prompt)


def analyze_video_segment(client, model, youtube_url, prompt, start_seconds, end_seconds):
    response = client.models.generate_content(
        model=model,
        contents=types.Content(
            parts=[
                types.Part(text=prompt),
                types.Part(
                    file_data=types.FileData(
                        file_uri=youtube_url,
                        start_offset=start_seconds,
                        end_offset=end_seconds,
                    )
                ),
            ]
        ),
    )
    return response.text


def mmss_to_seconds(time_str):
    try:
        minutes, seconds = map(int, time_str.split(":"))
        if minutes < 0 or seconds < 0 or seconds >= 60:
            return None
        return minutes * 60 + seconds
    except ValueError:
        return None


def build_transcript_prompt(speakers):
    template = Template(
        """Generate a transcript of the video. Include timestamps and speaker names.

Speakers are:
{% for speaker in speakers %}- {{ speaker }}{% if not loop.last %}\n{% endif %}{% endfor %}

eg:
[00:00] Brady: Hello there.
[00:02] Tim: Hi Brady.

It is important to include the correct speaker names. Use the names you identified earlier.

If there is music or a short jingle playing, signify like so:
[01:02] [MUSIC] or [01:02] [JINGLE]

If you can identify the name of the music or jingle playing then use that instead, eg:
[01:02] [Firework by Katy Perry] or [01:02] [The Sofa Shop jingle]

If there is some other sound playing try to identify the sound, eg:
[01:02] [Bell ringing]

Each individual caption should be quite short, a few short sentences at most.

Signify the end of the episode with [END].

Don't use any markdown formatting, like bolding or italics.

Only use characters from the English alphabet, unless you genuinely believe foreign terms are used.

It is important that you use the correct words and spell everything correctly. Use proper nouns. If the hosts discuss something like a movie, book or celebrity, make sure the most accurate spelling is used.

If any line is longer than 80 characters, split it into multiple lines.
"""
    )
    return template.render(speakers=speakers)


BUILTIN_PROMPTS = {
    # --- Analysis prompts ---
    "summary": """Analyze the following YouTube video content. Provide a detailed breakdown:

1. **Main Thesis/Claim:** What is the central point the creator is making?
2. **Key Topics:** List the main subjects discussed, referencing specific segments.
3. **Summary:** Provide a concise summary of the video content.

Use the provided title, chapter timestamps/descriptions, and description text if available.
""",
    "summary-full": """Analyze the following YouTube video content. Provide a detailed breakdown:

1. **Main Thesis/Claim:** What is the central point the creator is making?
2. **Key Topics:** List the main subjects discussed, referencing specific segments.
3. **Call to Action:** Identify any explicit requests made to the viewer.
4. **Summary:** Provide a concise summary of the video content.

Use the provided title, chapter timestamps/descriptions, and description text if available.

If you need to output in Chinese, use Traditional Chinese, never Simplified Chinese.
""",
    "summarize-tests": "Summarize the test results for each of the models that the host tested",
    "takeaways": "Extract all the key takeaways by the host. Summarize the video.",
    # --- Extraction prompts ---
    "extract-code": "Extract all the code shown in this video",
    "extract-python": "Extract all the python code",
    "extract-notebook-code": "Extract all the code in Colab notebook",
    "extract-notebook-cells": "Extract all the Python code and texts in all the notebook cells",
    "extract-prompts": "Extract all the prompts shown in this video",
    "extract-system-prompts": "Extract all the system prompts in this video",
    "extract-markdown": "Extract all the markdown files shown in this video",
    "extract-markdown-contents": "Extract the contents of all markdown files shown in this video",
    "extract-source-and-markdown": "Extract the contents of all source code and markdown files",
    "extract-text": "Extract all the text shown in the video frame by frame. Mark the texts captured by timestamp.",
    "extract-commands": "Extract all the command lines used in this video",
    "extract-terminal": "Extract everything shown in the terminal",
    "extract-slides": "Extract the slides from this video",
    "extract-prompts-and-responses": "Extract each prompt and its corresponding response from this video",
    "extract-all": "Extract all the prompts, codes, markdown files in this video",
    "extract-task-instructions": "Extract all the Task instructions from this video",
    "extract-skills": "Extract the contents of all the Skill files",
    "extract-agentic-prompts": "Extract all the agentic prompts shown in markdown files in this video",
    # --- Specific file extraction prompts ---
    "extract-claude-md": "Extract the content of the CLAUDE.md file",
    "extract-prd": "Extract the PRD file",
    "extract-workflow-md": "Extract the workflow.md file",
    "extract-settings-json": "Extract the settings.json file",
    "extract-spec-md": "Extract the content of the file spec.md",
    # --- Video AI prompts ---
    "extract-imagen-prompts": "Extract all the imagen4 prompts used to generate images",
    "extract-veo-prompts": "Create VEO3 prompts for each segment of this video.",
    "extract-music-prompts": "Extract all the Elevenlabs Music prompts shown in the video. Summarize the tips that enable users to construct good Music prompts.",
    # --- Pipeline / config ---
    "extract-pipeline-yaml": "Extract as much as text from pipeline.yaml as possible",
    "extract-input-text": 'Extract all the text under "Input Text" in the UI',
    "extract-tree-view": "Extract the tree view of the directory structure",
    "extract-workflow": "Extract the workflow(s) that the host used. Extract all markdown files and prompts.",
}


def sanitize_filename(name, max_len=100):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    name = re.sub(r'_+', '_', name)
    return name[:max_len]


def extract_video_id(url):
    """Extract video ID from a YouTube URL as a fallback identifier."""
    m = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', url)
    return m.group(1) if m else None


def get_video_metadata_from_gemini(client, model, youtube_url):
    """Extract video title and channel name using Gemini (no yt-dlp dependency)."""
    try:
        response = client.models.generate_content(
            model=model,
            contents=types.Content(
                parts=[
                    types.Part(text='Return ONLY two lines, nothing else:\nLine 1: the exact video title\nLine 2: the channel name'),
                    types.Part(file_data=types.FileData(file_uri=youtube_url)),
                ]
            ),
        )
        lines = response.text.strip().split("\n")
        lines = [l.strip() for l in lines if l.strip()]
        if len(lines) >= 2:
            return lines[0], lines[1]
        elif len(lines) == 1:
            return lines[0], "unknown_channel"
    except Exception as e:
        print(f"Warning: Could not fetch video metadata from Gemini: {e}", file=sys.stderr)
    video_id = extract_video_id(youtube_url)
    fallback_title = video_id if video_id else "video"
    return fallback_title, "unknown_channel"


def build_output_filename(url, client=None, model=None):
    if client and model:
        title, channel = get_video_metadata_from_gemini(client, model, url)
    else:
        video_id = extract_video_id(url)
        title = video_id if video_id else "video"
        channel = "unknown_channel"
    date_str = datetime.now().strftime("%m-%d-%Y")
    safe_title = sanitize_filename(title, max_len=20)
    safe_channel = sanitize_filename(channel)
    return f"{safe_title}_{safe_channel}_{date_str}.md"


def build_web_output_filename(url):
    """Build an output filename from a web URL's path."""
    parsed = urlparse(url)
    # Use the last path segment as a title hint
    path_parts = [p for p in parsed.path.strip("/").split("/") if p]
    title = path_parts[-1] if path_parts else parsed.hostname
    date_str = datetime.now().strftime("%m-%d-%Y")
    safe_title = sanitize_filename(title, max_len=30)
    safe_host = sanitize_filename(parsed.hostname or "web", max_len=20)
    return f"{safe_title}_{safe_host}_{date_str}.md"


def main():
    parser = argparse.ArgumentParser(
        description="Analyze YouTube videos or transcript files using Google Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://youtube.com/watch?v=abc123
  %(prog)s https://youtube.com/watch?v=abc123 -p "Extract all the code"
  %(prog)s --file transcript.txt
  %(prog)s --file transcript.txt -p "Summarize this transcript"
  %(prog)s https://youtube.com/watch?v=abc123 --builtin summary
  %(prog)s https://youtube.com/watch?v=abc123 --transcript --speakers "Alice" "Bob"
  %(prog)s https://youtube.com/watch?v=abc123 --start 01:30 --end 05:00 -p "Summarize this segment"
""",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("url", nargs="?", default=None, help="YouTube URL or any web page URL")
    source.add_argument("--file", "-f", help="Path to a local file (txt, html, pdf)")
    parser.add_argument(
        "-p", "--prompt", help="Custom prompt to send with the video"
    )
    parser.add_argument(
        "--builtin",
        choices=list(BUILTIN_PROMPTS.keys()),
        help="Use a built-in prompt: " + ", ".join(BUILTIN_PROMPTS.keys()),
    )
    parser.add_argument(
        "--transcript",
        action="store_true",
        help="Generate a transcript of the video",
    )
    parser.add_argument(
        "--speakers",
        nargs="+",
        default=["Speaker"],
        help="Speaker names for transcript mode (default: Speaker)",
    )
    parser.add_argument(
        "--model",
        default="gemini-3-pro-preview",
        help="Gemini model to use (default: gemini-3-pro-preview)",
    )
    parser.add_argument("--start", help="Start time in MM:SS format (for segment analysis)")
    parser.add_argument("--end", help="End time in MM:SS format (for segment analysis)")
    parser.add_argument(
        "-o", "--output", help="Write output to a file instead of stdout"
    )
    parser.add_argument(
        "--prompt-file", default="my_prompt.txt",
        help="Read the prompt from a file (default: my_prompt.txt)"
    )

    args = parser.parse_args()

    # Determine the prompt
    if args.transcript:
        prompt = build_transcript_prompt(args.speakers)
    elif args.builtin:
        prompt = BUILTIN_PROMPTS[args.builtin]
    elif args.prompt:
        prompt = args.prompt
    else:
        # Resolve prompt file relative to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = args.prompt_file if os.path.isabs(args.prompt_file) else os.path.join(script_dir, args.prompt_file)
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read()
        print(f"Using prompt from {prompt_path}\n", file=sys.stderr)

    client = genai.Client(api_key=get_api_key())
    print(f"Model: {args.model}", file=sys.stderr)

    if args.file:
        # Analyze a local file (txt, html, pdf)
        print(f"Analyzing file: {args.file}", file=sys.stderr)
        result = analyze_transcript_file(client, args.model, args.file, prompt)
        if args.output:
            output_path = args.output
        else:
            base = os.path.splitext(os.path.basename(args.file))[0]
            date_str = datetime.now().strftime("%m-%d-%Y")
            output_path = f"{sanitize_filename(base, max_len=20)}_{date_str}.md"
    elif args.url and is_youtube_url(args.url):
        # Analyze a YouTube video
        print(f"Analyzing YouTube video: {args.url}", file=sys.stderr)
        if args.start or args.end:
            start = mmss_to_seconds(args.start) if args.start else 0
            end = mmss_to_seconds(args.end) if args.end else None
            if start is None or (args.end and end is None):
                print("Error: Invalid time format. Use MM:SS.", file=sys.stderr)
                sys.exit(1)
            if end is None:
                print("Error: --end is required when using --start.", file=sys.stderr)
                sys.exit(1)
            print(f"Segment: {args.start} - {args.end}", file=sys.stderr)
            result = analyze_video_segment(client, args.model, args.url, prompt, start, end)
        else:
            result = analyze_video(client, args.model, args.url, prompt)
        output_path = args.output if args.output else build_output_filename(args.url, client, args.model)
    elif args.url and is_url(args.url):
        # Analyze a web page (blog post, article, etc.)
        print(f"Analyzing web page: {args.url}", file=sys.stderr)
        result = analyze_web_page(client, args.model, args.url, prompt)
        output_path = args.output if args.output else build_web_output_filename(args.url)
    else:
        print(f"Error: '{args.url}' is not a valid URL. Provide a URL or use --file.", file=sys.stderr)
        sys.exit(1)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\nOutput written to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
