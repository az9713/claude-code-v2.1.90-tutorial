---
name: symphony-harness-rubric
description: Score how harness-engineered a codebase is for Symphony readiness, based on the rubric derived from https://openai.com/index/harness-engineering/. Use this whenever the user asks for harness engineering assessment, Symphony readiness scoring, autonomy-readiness audits, retrofit recommendations, or asks "is my repo harness engineered?"
---

# Symphony Harness Rubric

Assess a repository with a weighted Harness Engineering scorecard and produce:
1. Quantified scores per control
2. Maturity band
3. Symphony readiness threshold classification
4. Prioritized retrofit recommendations

This skill is based on:
- https://openai.com/index/harness-engineering/

## Output requirements

- MUST write a Markdown report file in the user's current working directory.
- Default output filename:
  - `HARNESS_ENGINEERING_EVALUATION.md`
- Report MUST explicitly state:
  - "Rubric derived from https://openai.com/index/harness-engineering/."

## Run

From the user's current repository root (or target path):

```bash
python ~/.claude/skills/symphony-harness-rubric/scripts/evaluate_harness_rubric.py \
  --repo-root . \
  --output ./HARNESS_ENGINEERING_EVALUATION.md
```

If Python launcher is needed on Windows:

```powershell
python "$env:USERPROFILE\.claude\skills\symphony-harness-rubric\scripts\evaluate_harness_rubric.py" `
  --repo-root . `
  --output .\HARNESS_ENGINEERING_EVALUATION.md
```

## Assistant response after running

After writing the report:
1. Tell the user the output file path.
2. Provide a short summary:
   - Total score
   - Maturity band
   - Symphony readiness tier
   - Top 3 retrofit priorities

## Notes

- The article is descriptive, not a formal compliance standard.
- The evaluator uses evidence-based heuristics over repository files.
- Always communicate that results are "best-effort inference" and should be reviewed by maintainers.
