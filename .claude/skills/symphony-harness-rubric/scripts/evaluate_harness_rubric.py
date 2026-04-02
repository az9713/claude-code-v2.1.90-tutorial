#!/usr/bin/env python3
"""Evaluate harness-engineering maturity for Symphony readiness.

Rubric derived from:
https://openai.com/index/harness-engineering/
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WEIGHTS = {1: 10, 2: 10, 3: 8, 4: 8, 5: 12, 6: 8, 7: 12, 8: 6, 9: 6, 10: 10, 11: 6, 12: 4}
TITLES = {
    1: "Per-task isolated environments/worktrees",
    2: "App bootable/runnable in isolated workspace",
    3: "Agent-driven UI automation capability",
    4: "Local observability access for agents",
    5: "Docs as system-of-record + AGENTS map",
    6: "Docs mechanically enforced",
    7: "Architecture boundary enforcement",
    8: "Taste invariants enforced",
    9: "Plans as versioned first-class artifacts",
    10: "Agent-centered PR loop",
    11: "End-to-end autonomous workflow coverage",
    12: "Entropy control and continuous cleanup",
}

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "target",
    ".idea",
    ".vscode",
}
TEXT_EXTS = {
    ".md",
    ".txt",
    ".rst",
    ".adoc",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".sh",
    ".ps1",
    ".bat",
    ".cmd",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".ex",
    ".exs",
    ".swift",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".xml",
}


@dataclass
class FileRecord:
    rel: str
    rel_lower: str
    text: str
    text_lower: str


@dataclass
class Result:
    idx: int
    title: str
    weight: int
    score: int
    points: float
    evidence: list[str]
    recommendations: list[str]
    rationale: str


class RepoIndex:
    def __init__(self, root: Path, max_bytes: int = 750_000):
        self.root = root
        self.max_bytes = max_bytes
        self.files: list[FileRecord] = []
        self._load()

    def _load(self) -> None:
        for current, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            base = Path(current)
            for name in files:
                p = base / name
                rel = p.relative_to(self.root).as_posix()
                rel_lower = rel.lower()
                if not self._is_text_file(p):
                    continue
                try:
                    if p.stat().st_size > self.max_bytes:
                        continue
                    data = p.read_bytes()
                    if b"\x00" in data:
                        continue
                    text = data.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                self.files.append(FileRecord(rel=rel, rel_lower=rel_lower, text=text, text_lower=text.lower()))

    @staticmethod
    def _is_text_file(path: Path) -> bool:
        suffix = path.suffix.lower()
        if suffix in TEXT_EXTS:
            return True
        return path.name.lower() in {"dockerfile", "makefile", "readme", "agents.md", "claude.md", "workflow.md"}

    def has_text(self, patterns: list[str]) -> bool:
        return len(self.find_text(patterns, limit=1)) > 0

    def has_path(self, patterns: list[str]) -> bool:
        return len(self.find_path(patterns, limit=1)) > 0

    def find_text(self, patterns: list[str], limit: int = 8) -> list[str]:
        regexes = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]
        out: list[str] = []
        for f in self.files:
            if any(r.search(f.text) for r in regexes):
                out.append(f.rel)
                if len(out) >= limit:
                    break
        return out

    def find_path(self, patterns: list[str], limit: int = 8) -> list[str]:
        regexes = [re.compile(p, re.IGNORECASE) for p in patterns]
        out: list[str] = []
        for f in self.files:
            if any(r.search(f.rel_lower) for r in regexes):
                out.append(f.rel)
                if len(out) >= limit:
                    break
        return out


def uniq(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def level_score(levels: list[tuple[bool, int]]) -> int:
    score = 0
    for ok, lvl in levels:
        if ok:
            score = max(score, lvl)
    return score


def points(weight: int, score: int) -> float:
    return round(weight * (score / 4.0), 2)


def eval_controls(idx: RepoIndex) -> list[Result]:
    controls: list[Result] = []

    c1 = level_score(
        [
            (idx.has_text([r"\bworkspace\b", r"\bworktree\b", r"\bsandbox\b"]), 1),
            (idx.has_text([r"git worktree", r"workspace_root", r"create_for_issue"]), 2),
            (idx.has_text([r"validate_workspace_path", r"workspace_outside_root", r"invalid_workspace_cwd"]), 3),
            (idx.has_text([r"workspace_symlink_escape", r"before_remove", r"remove_issue_workspaces"]), 4),
        ]
    )
    controls.append(
        Result(
            1,
            TITLES[1],
            WEIGHTS[1],
            c1,
            points(WEIGHTS[1], c1),
            uniq(idx.find_text([r"workspace", r"worktree", r"validate_workspace_path", r"invalid_workspace_cwd"])),
            [
                "Implement per-task isolated workspace/worktree provisioning." if c1 < 2 else "",
                "Add hard workspace boundary and symlink escape checks." if c1 < 3 else "",
                "Automate cleanup of stale/terminal-state workspaces." if c1 < 4 else "",
            ],
            "Isolation and workspace safety for autonomous runs.",
        )
    )

    c2 = level_score(
        [
            (idx.has_text([r"first run", r"quick run", r"mix setup", r"npm install", r"make all"]), 1),
            (idx.has_text([r"after_create", r"bootstrap", r"git clone .* \."]), 2),
            (idx.has_path([r"\.github/workflows/"]) and idx.has_text([r"test", r"lint", r"build"]), 3),
            (idx.has_text([r"step-by-step", r"expected", r"troubleshooting"]), 4),
        ]
    )
    controls.append(Result(2, TITLES[2], WEIGHTS[2], c2, points(WEIGHTS[2], c2), uniq(idx.find_text([r"mix setup", r"after_create", r"quick run", r"step-by-step"]) + idx.find_path([r"\.github/workflows/"])), [r for r in ["Provide deterministic one-command bootstrap from fresh checkout." if c2 < 2 else "", "Add CI proof of fresh-checkout build/test reproducibility." if c2 < 3 else "", "Document expected outputs/failure recovery for each setup step." if c2 < 4 else ""] if r], "Deterministic bootability in isolated environments."))

    c3 = level_score([(idx.has_text([r"playwright", r"cypress", r"selenium", r"puppeteer", r"browser-use"]), 1), (idx.has_path([r"playwright", r"cypress", r"e2e", r"browser"]) or idx.has_text([r"ui test", r"e2e"]), 2), (idx.has_text([r"headless", r"screenshot", r"visual regression"]), 3), (idx.has_text([r"ui walkthrough", r"automation", r"capture"]), 4)])
    controls.append(Result(3, TITLES[3], WEIGHTS[3], c3, points(WEIGHTS[3], c3), uniq(idx.find_text([r"playwright", r"cypress", r"browser-use", r"screenshot", r"e2e"]) + idx.find_path([r"e2e", r"playwright", r"browser"])), [r for r in ["Adopt an agent-usable browser automation stack." if c3 < 2 else "", "Integrate UI automation in repeatable CI/scripted checks." if c3 < 3 else "", "Add screenshot/visual evidence capture for autonomous validation." if c3 < 4 else ""] if r], "Ability for agents to validate UI behavior independently."))

    c4 = level_score([(idx.has_text([r"log", r"logger", r"logging"]), 1), (idx.has_text([r"dashboard", r"observability", r"api/v1/state", r"liveview", r"telemetry"]), 2), (idx.has_text([r"snapshot", r"rate_limits", r"state_payload", r"presenter"]), 3), (idx.has_text([r"prometheus", r"opentelemetry", r"metrics", r"trace"]), 4)])
    controls.append(Result(4, TITLES[4], WEIGHTS[4], c4, points(WEIGHTS[4], c4), uniq(idx.find_text([r"observability", r"api/v1/state", r"snapshot", r"logger", r"telemetry"])), [r for r in ["Expose machine-readable runtime observability for agents." if c4 < 2 else "", "Add consistent state snapshot API/dashboard surfaces." if c4 < 3 else "", "Expand metrics/tracing for deeper autonomous diagnosis." if c4 < 4 else ""] if r], "Observable runtime state accessible to automation."))

    c5 = level_score([(idx.has_path([r"^docs/"]), 1), (idx.has_path([r"readme\.md", r"agents\.md", r"claude\.md", r"workflow\.md"]), 2), (idx.has_text([r"architecture", r"communication flow", r"developer guide", r"user guide"]), 3), (idx.has_path([r"docs/architecture", r"docs/user", r"docs/developer", r"docs/study"]) and idx.has_text([r"system-of-record", r"without external help"]), 4)])
    controls.append(Result(5, TITLES[5], WEIGHTS[5], c5, points(WEIGHTS[5], c5), uniq(idx.find_path([r"^docs/", r"readme\.md", r"agents\.md", r"claude\.md", r"workflow\.md"])), [r for r in ["Establish docs as the primary system-of-record." if c5 < 2 else "", "Add architecture and audience-specific guides with code anchors." if c5 < 3 else "", "Ensure docs are complete enough for no-external-help onboarding." if c5 < 4 else ""] if r], "Repository knowledge codification for humans and agents."))

    c6 = level_score([(idx.has_text([r"pr_body\.check", r"specs\.check", r"markdownlint", r"pull_request_template"]), 1), (idx.has_path([r"\.github/workflows/"]) and idx.has_text([r"lint", r"check", r"ci"]), 2), (idx.has_text([r"must follow", r"required", r"do not merge", r"quality gate"]), 3), (idx.has_text([r"link check", r"docs check", r"freshness", r"strict"]), 4)])
    controls.append(Result(6, TITLES[6], WEIGHTS[6], c6, points(WEIGHTS[6], c6), uniq(idx.find_text([r"pr_body\.check", r"specs\.check", r"quality gate", r"pull_request_template", r"do not merge"]) + idx.find_path([r"\.github/workflows/"])), [r for r in ["Add CI-enforced documentation/process checks." if c6 < 2 else "", "Gate merges on required templates and quality checks." if c6 < 3 else "", "Introduce docs freshness/link validation in CI." if c6 < 4 else ""] if r], "Mechanical enforcement of documentation/process contracts."))

    c7 = level_score([(idx.has_text([r"architecture", r"boundary", r"guardrails", r"must not"]), 1), (idx.has_text([r"validate_workspace_path", r"unsupported", r"nimbleoptions\.validate", r"invalid"]), 2), (idx.has_text([r"import-linter", r"depcruise", r"archunit", r"forbidden import", r"eslint.*boundaries", r"specs\.check"]), 3), (idx.has_path([r"test/"]) and idx.has_text([r"reject", r"outside_root", r"invalid", r"unsupported"]), 4)])
    controls.append(Result(7, TITLES[7], WEIGHTS[7], c7, points(WEIGHTS[7], c7), uniq(idx.find_text([r"validate_workspace_path", r"guardrails", r"boundary", r"unsupported", r"nimbleoptions"]) + idx.find_path([r"test/"])), [r for r in ["Document architecture dependency boundaries explicitly." if c7 < 2 else "", "Add static/test enforcement for boundary violations." if c7 < 3 else "", "Strengthen high-risk boundary regression tests." if c7 < 4 else ""] if r], "Architecture rule clarity and enforcement strength."))

    c8 = level_score([(idx.has_text([r"lint", r"credo", r"eslint", r"ruff", r"strict"]), 1), (idx.has_text([r"formatter", r"mix format", r"prettier", r"gofmt"]), 2), (idx.has_text([r"required rules", r"@spec", r"logging conventions", r"style"]), 3), (idx.has_text([r"make all", r"threshold", r"coverage", r"dialyzer"]), 4)])
    controls.append(Result(8, TITLES[8], WEIGHTS[8], c8, points(WEIGHTS[8], c8), uniq(idx.find_text([r"credo", r"@spec", r"required rules", r"make all", r"coverage", r"dialyzer"])), [r for r in ["Establish baseline lint/format checks across the repo." if c8 < 2 else "", "Encode engineering invariants as explicit enforceable rules." if c8 < 3 else "", "Tighten strict quality gates and regression protection." if c8 < 4 else ""] if r], "Enforcement of engineering taste and quality invariants."))

    c9 = level_score([(idx.has_path([r"plan", r"roadmap", r"workpad", r"adr", r"todo"]), 1), (idx.has_text([r"\[ \]", r"\[x\]", r"checklist", r"acceptance criteria", r"validation"]), 2), (idx.has_text([r"completion bar", r"step 0", r"step 1", r"execution phase", r"status map"]), 3), (idx.has_text([r"traceability", r"final checklist", r"handoff notes", r"notes"]), 4)])
    controls.append(Result(9, TITLES[9], WEIGHTS[9], c9, points(WEIGHTS[9], c9), uniq(idx.find_path([r"plan", r"roadmap", r"workpad", r"workflow", r"todo"]) + idx.find_text([r"acceptance criteria", r"validation", r"checklist", r"completion bar"])), [r for r in ["Version plan artifacts in-repo with clear status states." if c9 < 2 else "", "Tie plan execution to acceptance/validation checkpoints." if c9 < 3 else "", "Strengthen traceability from plan to delivery outcomes." if c9 < 4 else ""] if r], "Planning artifacts quality and execution traceability."))

    c10 = level_score([(idx.has_text([r"pull request", r"human review", r"feedback", r"pr"]), 1), (idx.has_text([r"pr feedback sweep", r"check-address-verify", r"no outstanding comments", r"checks are green"]), 2), (idx.has_text([r"pr_body\.check", r"land skill", r"workspace\.before_remove", r"merge"]), 3), (idx.has_text([r"repeat this sweep", r"blocking until", r"explicit pushback"]), 4)])
    controls.append(Result(10, TITLES[10], WEIGHTS[10], c10, points(WEIGHTS[10], c10), uniq(idx.find_text([r"pr feedback sweep", r"human review", r"checks are green", r"land skill", r"pr_body\.check"])), [r for r in ["Define a strict agent-first PR feedback resolution loop." if c10 < 2 else "", "Automate PR quality gates and merge readiness checks." if c10 < 3 else "", "Enforce repeat-until-clean feedback sweeps in workflow." if c10 < 4 else ""] if r], "Readiness for agent-centered PR handling and review loops."))

    c11 = level_score([(idx.has_text([r"reproduce first", r"validation", r"implementation"]), 1), (idx.has_text([r"todo", r"in progress", r"human review", r"merging", r"done"]), 2), (idx.has_text([r"step 0", r"step 1", r"step 2", r"step 3", r"step 4"]), 3), (idx.has_text([r"escape hatch", r"blocked", r"unblock", r"retry", r"terminal state"]), 4)])
    controls.append(Result(11, TITLES[11], WEIGHTS[11], c11, points(WEIGHTS[11], c11), uniq(idx.find_text([r"reproduce first", r"step 0", r"human review", r"merging", r"done", r"blocked"])), [r for r in ["Define an explicit autonomous lifecycle from reproduction to merge/escalation." if c11 < 2 else "", "Standardize state transitions and completion criteria." if c11 < 3 else "", "Add robust blocked/unblock and retry semantics." if c11 < 4 else ""] if r], "Coverage of full autonomous engineering lifecycle."))

    c12 = level_score([(idx.has_text([r"quality bar", r"definition of done", r"policy", r"checklist"]), 1), (idx.has_text([r"debt prevention", r"cleanup", r"before_remove", r"entropy"]), 2), (idx.has_text([r"do not merge", r"must pass", r"required"]), 3), (idx.has_text([r"recurring", r"monthly", r"periodic", r"scheduled"]), 4)])
    controls.append(Result(12, TITLES[12], WEIGHTS[12], c12, points(WEIGHTS[12], c12), uniq(idx.find_text([r"debt prevention", r"quality bar", r"do not merge", r"cleanup", r"recurring", r"monthly"])), [r for r in ["Establish explicit anti-entropy quality principles and governance." if c12 < 2 else "", "Tie cleanup/debt controls to merge policy." if c12 < 3 else "", "Add recurring quality audits and trend tracking cadence." if c12 < 4 else ""] if r], "Anti-entropy governance and ongoing maintenance discipline."))

    return controls


def maturity(total: float) -> str:
    if total <= 24:
        return "Pre-harness"
    if total <= 49:
        return "Assisted harness"
    if total <= 69:
        return "Harness foundation"
    if total <= 84:
        return "Strong harness"
    return "Harness-native"


def tier(total: float, s: dict[int, int]) -> str:
    pilot = total >= 45 and all(s.get(k, 0) >= 2 for k in (1, 2, 5, 7, 10))
    unattended = total >= 70 and all(s.get(k, 0) >= 3 for k in (1, 2, 5, 6, 7, 10))
    agent_first = total >= 85 and s.get(3, 0) >= 3 and s.get(4, 0) >= 3
    if agent_first:
        return "Tier 3: Agent-first (close to harness-engineering exemplar)"
    if unattended:
        return "Tier 2: Reliable unattended runs"
    if pilot:
        return "Tier 1: Pilot with human supervision"
    return "Tier 0: Not ready for dependable Symphony autonomy"


def render_markdown(repo_root: Path, results: list[Result]) -> str:
    total = round(sum(r.points for r in results), 2)
    scores = {r.idx: r.score for r in results}
    gaps = sorted(results, key=lambda r: (r.score, -r.weight))[:3]
    lines: list[str] = []
    lines.append("# Harness Engineering Evaluation")
    lines.append("")
    lines.append(f"- Generated: {dt.datetime.now(dt.timezone.utc).isoformat()}")
    lines.append(f"- Repository: `{repo_root}`")
    lines.append("- Rubric derived from https://openai.com/index/harness-engineering/.")
    lines.append("- Method: heuristic static scan of repository files (best-effort inference).")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- **Total Score:** **{total}/100**")
    lines.append(f"- **Maturity Band:** **{maturity(total)}**")
    lines.append(f"- **Symphony Readiness Tier:** **{tier(total, scores)}**")
    lines.append("")
    lines.append("## Weighted Score Table")
    lines.append("")
    lines.append("| # | Control | Weight | Score (0-4) | Points |")
    lines.append("|---|---|---:|---:|---:|")
    for r in results:
        lines.append(f"| {r.idx} | {r.title} | {r.weight} | {r.score} | {r.points:.2f} |")
    lines.append("")
    lines.append("## Top Retrofit Priorities")
    lines.append("")
    for i, g in enumerate(gaps, 1):
        lines.append(f"{i}. **Control {g.idx}: {g.title}** (score `{g.score}/4`, weight `{g.weight}`)")
    lines.append("")
    lines.append("## Detailed Findings")
    lines.append("")
    for r in results:
        lines.append(f"### Control {r.idx}: {r.title}")
        lines.append(f"- Weight: `{r.weight}`")
        lines.append(f"- Score: `{r.score}/4`")
        lines.append(f"- Weighted points: `{r.points:.2f}`")
        lines.append(f"- Rationale: {r.rationale}")
        lines.append("- Evidence files:")
        if r.evidence:
            for e in r.evidence[:12]:
                lines.append(f"  - `{e}`")
        else:
            lines.append("  - none detected by heuristic scan")
        lines.append("- Recommendations:")
        if r.recommendations:
            for rec in r.recommendations:
                lines.append(f"  - {rec}")
        else:
            lines.append("  - Maintain and periodically re-audit this control.")
        lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- This is an inference-based rubric, not an official OpenAI certification.")
    lines.append("- Some practices can be undercounted if they are external or undocumented in the repo.")
    lines.append("- Review results with maintainers before making structural changes.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score harness engineering maturity for Symphony readiness.")
    parser.add_argument("--repo-root", default=".", help="Repository root path (default: current directory)")
    parser.add_argument(
        "--output",
        default="HARNESS_ENGINEERING_EVALUATION.md",
        help="Markdown output path (default: HARNESS_ENGINEERING_EVALUATION.md)",
    )
    parser.add_argument("--json-output", default="", help="Optional JSON output path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        raise SystemExit(f"Invalid repo root: {repo_root}")

    idx = RepoIndex(repo_root)
    results = eval_controls(idx)
    report = render_markdown(repo_root, results)

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote markdown report: {out}")

    if args.json_output:
        total = round(sum(r.points for r in results), 2)
        payload = {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "repo_root": str(repo_root),
            "rubric_source": "https://openai.com/index/harness-engineering/",
            "total_score": total,
            "maturity_band": maturity(total),
            "readiness_tier": tier(total, {r.idx: r.score for r in results}),
            "controls": [
                {
                    "id": r.idx,
                    "title": r.title,
                    "weight": r.weight,
                    "score": r.score,
                    "points": r.points,
                    "rationale": r.rationale,
                    "evidence": r.evidence,
                    "recommendations": r.recommendations,
                }
                for r in results
            ],
        }
        jout = Path(args.json_output).resolve()
        jout.parent.mkdir(parents=True, exist_ok=True)
        jout.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote JSON report: {jout}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
