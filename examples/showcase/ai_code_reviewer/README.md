# AI-Powered Code Reviewer

This example demonstrates LexFlow's ability to integrate GitHub APIs with AI to provide intelligent, automated code reviews for pull requests.

## What This Example Demonstrates

- **GitHub Integration**: Uses LexFlow's built-in GitHub opcodes to fetch PR metadata, file lists, and diffs via the `gh` CLI
- **AI-Powered Analysis**: Leverages Google Vertex AI (Gemini) through pydantic-ai to analyze code changes
- **Structured Output**: Produces professional, actionable code review feedback
- **Real-World Utility**: A practical workflow developers can actually use in their daily work

## Prerequisites

### 1. Install LexFlow with AI Support

```bash
pip install lexflow[ai]
```

### 2. Install and Authenticate GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
apt install gh

# Authenticate
gh auth login
```

### 3. Set Up Google Cloud Authentication

```bash
# Option 1: Application Default Credentials (recommended for local dev)
gcloud auth application-default login

# Option 2: Service account (for CI/CD)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

You'll also need a GCP project with Vertex AI API enabled.

## Usage

### Basic Usage

```bash
lexflow examples/showcase/ai_code_reviewer/review_pr.yaml \
  --input owner=anthropics \
  --input repo=claude-code \
  --input pr=123 \
  --input project=YOUR_GCP_PROJECT
```

### With Custom Location

```bash
lexflow examples/showcase/ai_code_reviewer/review_pr.yaml \
  --input owner=microsoft \
  --input repo=vscode \
  --input pr=12345 \
  --input project=my-gcp-project \
  --input location=europe-west1
```

### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `owner` | Yes | - | Repository owner (e.g., "anthropics") |
| `repo` | Yes | - | Repository name (e.g., "claude-code") |
| `pr` | Yes | - | Pull request number |
| `project` | Yes | - | Google Cloud project ID |
| `location` | No | us-central1 | GCP region for Vertex AI |

## Sample Output

```
================================================================================
                    AI-POWERED CODE REVIEWER
================================================================================

Fetching PR #42 from anthropics/lex-flow...

PULL REQUEST: Add new string manipulation opcodes
Author: @developer
URL: https://github.com/anthropics/lex-flow/pull/42
Branch: feature/string-opcodes -> main

--------------------------------------------------------------------------------
                         CHANGED FILES
--------------------------------------------------------------------------------

  lexflow-core/src/lexflow/opcodes.py (modified: +45/-3)
  tests/unit/test_opcodes.py (modified: +120/-0)
  docs/OPCODE_REFERENCE.md (modified: +25/-0)

Total: 3 files changed, +190 additions, -3 deletions

--------------------------------------------------------------------------------
                         AI CODE REVIEW
--------------------------------------------------------------------------------

Initializing AI reviewer...
Analyzing code changes...

## Overall Assessment

This PR adds well-implemented string manipulation opcodes with good test coverage.

## Bugs & Issues

- **Line 142**: The `string_substring` function doesn't handle negative indices. Consider adding validation or documenting the expected behavior.

## Security Concerns

- No significant security issues found. String operations are properly bounded.

## Code Quality

**Positive:**
- Clean, consistent naming following existing patterns
- Good docstrings with examples
- Comprehensive error messages

**Suggestions:**
- Consider extracting the validation logic in lines 150-155 into a helper function
- The test file could benefit from parameterized tests to reduce duplication

## Best Practices

- Tests cover happy paths and edge cases
- Documentation updated alongside code changes
- No breaking changes to public API

## Recommendation

**APPROVE** - This is a solid PR with minor suggestions for improvement that don't block merging.

================================================================================
                         REVIEW COMPLETE
================================================================================
```

## How It Works

### Workflow Steps

1. **Fetch PR Data**: Uses `github_get_pr_info`, `github_get_pr_files`, and `github_get_pr_diff` opcodes to retrieve all PR information
2. **Display Summary**: Shows PR metadata and a summary of changed files with line counts
3. **Initialize AI**: Creates a Vertex AI model and configures a specialized code reviewer agent
4. **Analyze Changes**: Sends the full diff to the AI with instructions to review for bugs, security, quality, and best practices
5. **Output Review**: Displays the AI's structured feedback with a final recommendation

### Key Opcodes Used

| Opcode | Purpose |
|--------|---------|
| `github_get_pr_info` | Fetch PR title, author, branches, URL |
| `github_get_pr_files` | Get list of changed files with stats |
| `github_get_pr_diff` | Fetch the unified diff |
| `pydantic_ai_create_vertex_model` | Initialize Gemini model |
| `pydantic_ai_create_agent` | Create agent with review instructions |
| `pydantic_ai_run` | Execute the review analysis |

## Customization

### Modify Review Criteria

Edit the `create_reviewer` node's `instructions` to customize what the AI focuses on:

```yaml
create_reviewer:
  opcode: pydantic_ai_create_agent
  isReporter: true
  inputs:
    model:
      variable: model
    instructions:
      literal: |
        You are a security-focused code reviewer. Focus primarily on:
        - Authentication and authorization flaws
        - Input validation vulnerabilities
        - Cryptographic issues
        - Data exposure risks

        For each issue found, provide:
        - Severity (Critical/High/Medium/Low)
        - Location in the code
        - Recommended fix
```

### Use a Different AI Model

Change the model in the `create_model` node:

```yaml
create_model:
  opcode: pydantic_ai_create_vertex_model
  isReporter: true
  inputs:
    model_name:
      literal: "gemini-2.5-pro"  # Use Pro for more detailed analysis
    project:
      variable: project
    location:
      variable: location
```

### Add Review to PR as Comment

You could extend this workflow to post the review as a PR comment using GitHub's API (requires additional opcodes or custom implementation).

## Troubleshooting

### "GitHub CLI (gh) is not installed"

Install the GitHub CLI and authenticate:
```bash
brew install gh  # or apt install gh
gh auth login
```

### "Failed to authenticate with Vertex AI"

Ensure you're authenticated with Google Cloud:
```bash
gcloud auth application-default login
```

Or check that your service account has the required permissions.

### "PR not found"

Verify:
- The repository exists and is accessible
- The PR number is correct
- Your `gh` CLI has access to the repository (for private repos)

### Large Diffs

Very large PRs may exceed the AI model's context window. Consider:
- Reviewing smaller, focused PRs
- Modifying the workflow to review files individually
- Using a model with a larger context window

## Related Examples

- `examples/showcase/multi_agent_debate/` - Multi-agent AI interaction
- `examples/integrations/pydantic_ai/` - Basic Vertex AI usage
