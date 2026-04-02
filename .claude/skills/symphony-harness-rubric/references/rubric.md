# Harness Rubric Reference

This skill evaluates codebases against a 12-control weighted scorecard (0-100):

1. Per-task isolated environments/worktrees (10)
2. App bootable/runnable in isolated workspace (10)
3. Agent-driven UI automation capability (8)
4. Local observability access for agents (8)
5. Docs as system-of-record + AGENTS map (12)
6. Docs mechanically enforced (8)
7. Architecture boundary enforcement (12)
8. Taste invariants enforced (6)
9. Plans as versioned first-class artifacts (6)
10. Agent-centered PR loop (10)
11. End-to-end autonomous workflow coverage (6)
12. Entropy control and continuous cleanup (4)

Maturity bands:
- 0-24: Pre-harness
- 25-49: Assisted harness
- 50-69: Harness foundation
- 70-84: Strong harness
- 85-100: Harness-native

Symphony readiness thresholds:
- Tier 1 pilot: score >= 45 and controls 1/2/5/7/10 >= 2
- Tier 2 unattended: score >= 70 and controls 1/2/5/6/7/10 >= 3
- Tier 3 agent-first: score >= 85 and controls 3/4 >= 3

Rubric source context:
- https://openai.com/index/harness-engineering/

