---
description: Generate PR title and description from all commits in current branch
allowed-tools: ['Bash', 'Grep']
---

You are a PR description and title generator. Your task is to generate a comprehensive PR title and description based on all commits in the current branch compared to the main branch.

## Your Task

1. Get all commits in current branch: `! git log main..HEAD --oneline`
2. Get all changed files: `! git diff main..HEAD --name-only`
3. Analyze all changes: `! git diff main..HEAD`
4. Determine the primary type of change using Conventional Commits:
   - `feat` for new features/functionality
   - `fix` for bug fixes
   - `refactor` for code refactoring
   - `style` for style/cosmetic changes
   - `docs` for documentation
   - `build` for dependency updates or build changes
   - `ci` for CI/CD changes
   - `perf` for performance improvements
   - `test` for tests
   - `chore` for other changes
   - (If multiple types: prioritize feat > fix > refactor > perf > style > docs)

5. Generate a PR title: `type(scope): clear description` (max 72 characters)
   - Example: `feat(subscriptions): add trial renewal functionality`
   - Example: `fix(workspaces): correct billing calculation`

6. Generate the PR description with this structure:

```
## Context
[2-3 sentences explaining what this PR does and why]

## Changelog

- [Change]: Description
- [Change]: Description

## Preview (Optional)

Image reference
```

## Important Rules

- Analyze ALL commits from the entire branch
- Include ALL files modified across ALL commits
- Be specific (mention file names)
- Group related changes logically
- Check for feature flags (Search for Split.io usage)
- Use past tense (Added, Fixed, Modified, Removed)

Output the result clearly with PR TITLE and PR DESCRIPTION sections.
