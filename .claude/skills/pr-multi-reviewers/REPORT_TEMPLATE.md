# Code Review Report

| Field | Value |
|-------|-------|
| **Type** | PR #XXX / Branch `branch-name` |
| **Target** | `main` |
| **Date** | YYYY-MM-DD |
| **Agents** | Commits, Patterns, Tests, Opcodes, Security |

---

## Verdict: **APPROVED** | **CHANGES REQUESTED** | **NEEDS DISCUSSION**

| Severity | Count |
|----------|-------|
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |

---

## HIGH Severity

### Domain: <domain name>

| Rule | File | Line | Finding | Suggestion |
|------|------|------|---------|------------|
| H1 | `path/to/file.py` | 42 | Description of the issue | How to fix it |

---

## MEDIUM Severity

### Domain: <domain name>

| Rule | File | Line | Finding | Suggestion |
|------|------|------|---------|------------|
| M1 | `path/to/file.py` | 15 | Description of the issue | How to fix it |

---

## LOW Severity

### Domain: <domain name>

| Rule | File | Line | Finding | Suggestion |
|------|------|------|---------|------------|
| L1 | `path/to/file.py` | 88 | Description of the issue | How to fix it |

---

## Clean Areas

The following domains had **no issues** found:

- **Tests & Validation**: All rules passed (H2, M6, L1)
- **Security & Contracts**: All rules passed (M10, L3, L5)

---

## Checklist

| Category | Status | Rules Checked |
|----------|--------|---------------|
| Commits & Versioning | PASS/FAIL | H1, H4-H7, M9 |
| Code Patterns & Architecture | PASS/FAIL | M2-M5, M7-M8, L2, L4 |
| Tests & Validation | PASS/FAIL | H2, M6, L1 |
| Opcodes & Dependencies | PASS/FAIL | H3, H8-H11, M1 |
| Security & Contracts | PASS/FAIL | M10, L3, L5 |
