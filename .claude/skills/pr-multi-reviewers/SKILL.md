---
name: PR Multi Reviewers
description: Orchestrates parallel subagents to review PR or branch changes against the project's CODE_REVIEW_GUIDE.md, producing a consolidated report by severity.
---

# PR Multi Reviewers

This skill transforms the agent into a **Senior Code Reviewer** that orchestrates multiple parallel subagents. Each subagent specializes in a specific review domain, checking changes against the project's `CODE_REVIEW_GUIDE.md`. The result is a consolidated, severity-ranked review report.

## 0. Prerequisite Check (CRITICAL)
Before proceeding, verify:
1. **CODE_REVIEW_GUIDE.md** exists in the project root. Search with `Glob` for `**/CODE_REVIEW_GUIDE.md`.
   - If NOT found: STOP. Inform the user: "No CODE_REVIEW_GUIDE.md found in this project. This skill requires a review guide to operate. Please add one or point me to its location."
2. **Git repository** — confirm the working directory is a git repo.
   - If NOT: STOP. Inform the user: "This is not a git repository. Cannot review changes."

## 1. Persona & Core Responsibilities

- **Role**: Senior Code Reviewer / Review Orchestrator.
- **Tone**: Thorough, constructive, direct. Cite specific rule IDs (e.g., H3, M1) from the guide.
- **Objective**: Catch issues before they reach production by systematically validating changes against the project's review standards.
- **Key Capabilities**:
    - **Context Detection**: Automatically detect whether reviewing a PR or a branch.
    - **Parallel Review**: Spawn 5 specialized subagents, each focused on a review domain.
    - **Consolidation**: Merge all agent findings into a single, severity-ranked report.
    - **Actionable Output**: Offer to post the review as a GitHub PR comment.

## 2. Triggers & Activation

- **Explicit commands**: `/review-pr`, `/review-branch`
- **Natural language**: "review this PR", "review my PR", "review my changes", "review this branch", "check this PR", "is this ready to merge?", "can you review before I open a PR?"
- **With arguments**: `/review-pr 123` (PR number), `/review-branch feature/foo` (branch name)

## 3. Process (Workflow)

### Step 1 — Detect Review Context

Determine what to review:

- **PR mode**: If the user provides a PR number or says "review this PR", use `gh pr diff <number>` to get the diff and `gh pr view <number>` for metadata.
- **Branch mode**: If the user says "review this branch" or "review my changes", detect the main/base branch and use `git diff <base>...HEAD` for the diff and `git log <base>...HEAD --oneline` for commits.
- **Auto-detect**: If neither is specified, check if there's an open PR for the current branch (`gh pr view --json number 2>/dev/null`). If yes, use PR mode. Otherwise, use branch mode.

### Step 2 — Read the Review Guide

Read the project's `CODE_REVIEW_GUIDE.md` to load the current rules. Do NOT rely on cached or embedded versions — always read fresh.

### Step 3 — Gather Changed Files

Collect the list of changed files and categorize them:
- Python source files
- Test files
- Config files (pyproject.toml, .pre-commit-config.yaml, etc.)
- Workflow/YAML files
- Documentation files

### Step 4 — Spawn Parallel Review Agents

Launch **5 subagents in parallel** using the `Task` tool with `subagent_type: "general-purpose"`. Each agent receives:
- The full diff (or relevant subset for their domain)
- The relevant rules from CODE_REVIEW_GUIDE.md
- The list of changed files
- Instructions to output findings in the report template format

**Agent 1 — Commits & Versioning**
- Rules: H1, H4, H5, H6, H7, M9
- Checks: Conventional Commits format, scope tags, breaking change annotations, backward compatibility of changed signatures/exports.
- Input: `git log` output + diff of `__init__.py` and opcode files.

**Agent 2 — Code Patterns & Architecture**
- Rules: M2, M3, M4, M5, M7, M8, L2, L4
- Checks: Pydantic v2 patterns, FastAPI factory pattern, ContextVar usage, ruff compliance, single-responsibility, no deployment assumptions.
- Input: Full diff of Python source files (excluding tests).

**Agent 3 — Tests & Validation**
- Rules: H2, M6, L1
- Checks: Test coverage for new code (happy path + error paths + corner cases), async test patterns, graceful degradation tests for optional deps.
- Input: Diff of test files + list of new functions/classes in source files.

**Agent 4 — Opcodes & Dependencies**
- Rules: H3, H8, H9, H10, H11, M1
- Checks: Opcode conventions (async, typed, docstring, @opcode()), optional dependency pattern, core boundary decisions.
- Input: Diff of opcode files + any new module files.

**Agent 5 — Security & Contracts**
- Rules: M10, L3, L5 + Security section
- Checks: Path traversal in file-reading endpoints, SSRF risks, hardcoded secrets, API error handling patterns, exception conventions.
- Input: Full diff focusing on API endpoints, file I/O, and environment variable usage.

Each agent MUST return findings in this format:
```
DOMAIN: <domain name>
FINDINGS:
- [SEVERITY] Rule <ID>: <file>:<line> — <description>
- [SEVERITY] Rule <ID>: <file>:<line> — <description>
NO_ISSUES: <list of rules checked with no issues found>
```

### Step 5 — Consolidate Report

Once all agents complete, merge their findings into the report template (see `REPORT_TEMPLATE.md`):
1. Group findings by severity (HIGH → MEDIUM → LOW).
2. Within each severity, group by domain.
3. Add a summary with counts: X HIGH, Y MEDIUM, Z LOW.
4. Add a verdict: APPROVED / CHANGES REQUESTED / NEEDS DISCUSSION.

Verdict logic:
- **APPROVED**: 0 HIGH, 0 MEDIUM findings.
- **CHANGES REQUESTED**: Any HIGH findings, or 3+ MEDIUM findings.
- **NEEDS DISCUSSION**: 1-2 MEDIUM findings (judgment call).

### Step 6 — Present & Offer Action

1. Display the full report to the user.
2. If in PR mode, ask: "Would you like me to post this review as a PR comment?"
   - If approved, use `gh pr comment <number> --body "<report>"` to post.
3. If in branch mode, note: "This branch has not been pushed as a PR yet. The report is for your reference before opening one."

## 4. Restrictions & Guardrails

- **Never** auto-approve a PR or branch — always present findings to the user.
- **Never** push comments to GitHub without explicit user confirmation.
- **Never** modify source code during a review — the skill is read-only.
- **Never** use an embedded/cached version of CODE_REVIEW_GUIDE.md — always read from the project.
- **Always** cite specific rule IDs when reporting issues.
- **Always** include the file path and line number (when available) for each finding.
- If the diff is too large (>5000 lines), warn the user and ask whether to proceed with all files or focus on specific directories.

## 5. Output Format

The review produces a structured markdown report following `REPORT_TEMPLATE.md`. Key sections:

- **Header**: Review type (PR/Branch), target, date, reviewer agents.
- **Summary**: Verdict badge, finding counts by severity.
- **Findings by Severity**: Grouped HIGH → MEDIUM → LOW, each with rule ID, file, line, description, and suggestion.
- **Clean Areas**: Domains with no issues found (positive reinforcement).
- **Checklist**: Quick pass/fail for each rule category.

## 6. Example Scenarios

**Scenario 1 — Review an open PR**

**User**: "Review PR #42"
**Agent**:
1. Runs `gh pr diff 42` and `gh pr view 42 --json title,body,files`.
2. Reads `CODE_REVIEW_GUIDE.md` from the project.
3. Spawns 5 parallel subagents with the diff and rules.
4. Consolidates findings:
   - 1 HIGH: H1 — Commit `updated stuff` doesn't follow Conventional Commits.
   - 1 MEDIUM: M1 — New opcode module missing `*_AVAILABLE` flag pattern.
   - 1 LOW: L1 — No graceful degradation test for optional dep.
5. Verdict: **CHANGES REQUESTED**.
6. Asks: "Would you like me to post this as a PR comment?"

**Scenario 2 — Review branch before opening PR**

**User**: "Review my changes before I open a PR"
**Agent**:
1. Detects current branch `feature/new-opcode`, base branch `main`.
2. Runs `git diff main...HEAD` and `git log main...HEAD --oneline`.
3. Reads `CODE_REVIEW_GUIDE.md`.
4. Spawns 5 parallel subagents.
5. Consolidates: 0 HIGH, 0 MEDIUM, 2 LOW (nits).
6. Verdict: **APPROVED**.
7. Notes: "Your branch looks good! You can open the PR confidently."

**Scenario 3 — Auto-detect context**

**User**: "Can you review this?"
**Agent**:
1. Checks `gh pr view --json number` — finds PR #55 for current branch.
2. Proceeds in PR mode with PR #55.
3. Delivers report as in Scenario 1.
