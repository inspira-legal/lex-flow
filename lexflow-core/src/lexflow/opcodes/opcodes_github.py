"""GitHub opcodes for LexFlow using the gh CLI.

This module provides opcodes for interacting with GitHub PRs and repositories
using the GitHub CLI (gh). This approach avoids authentication complexity since
gh handles all authentication.

Installation:
    GitHub CLI must be installed and authenticated:
        brew install gh  # or apt install gh
        gh auth login

Usage:
    These opcodes are automatically registered when this module is imported.
    They use the gh CLI tool to interact with GitHub.
"""

import asyncio
import base64
import json
import shutil
from typing import Any, Dict, List

from .opcodes import opcode

# Check if gh CLI is available
GH_AVAILABLE = shutil.which("gh") is not None


def _check_gh():
    """Check if gh CLI is available and raise helpful error if not."""
    if not GH_AVAILABLE:
        raise RuntimeError(
            "GitHub CLI (gh) is not installed or not in PATH. Install it with:\n"
            "  brew install gh  # macOS\n"
            "  apt install gh   # Ubuntu/Debian\n"
            "Then authenticate with:\n"
            "  gh auth login"
        )


async def _run_gh_command(args: List[str], check: bool = True) -> str:
    """Run a gh command and return its output.

    Args:
        args: Command arguments (without 'gh' prefix)
        check: If True, raise on non-zero exit code

    Returns:
        Command stdout as string

    Raises:
        RuntimeError: If command fails and check is True
    """
    _check_gh()

    process = await asyncio.create_subprocess_exec(
        "gh",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if check and process.returncode != 0:
        error_msg = stderr.decode().strip() if stderr else "Unknown error"
        raise RuntimeError(f"gh command failed: {error_msg}")

    return stdout.decode()


# ============================================================================
# PR Information
# ============================================================================


@opcode()
async def github_get_pr_info(owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """Get PR metadata from GitHub.

    Args:
        owner: Repository owner (e.g., "anthropics")
        repo: Repository name (e.g., "lex-flow")
        pr_number: Pull request number

    Returns:
        Dict with PR metadata:
        - title: PR title
        - body: PR description/body
        - author: PR author username
        - state: PR state (OPEN, CLOSED, MERGED)
        - base_branch: Target branch
        - head_branch: Source branch
        - url: PR web URL

    Raises:
        RuntimeError: If gh command fails (e.g., PR not found, auth issues)

    Example:
        pr_info = github_get_pr_info("anthropics", "claude-code", 123)
        # Returns: {
        #     "title": "Add new feature",
        #     "body": "This PR adds...",
        #     "author": "octocat",
        #     "state": "OPEN",
        #     "base_branch": "main",
        #     "head_branch": "feature/new-thing",
        #     "url": "https://github.com/anthropics/claude-code/pull/123"
        # }
    """
    output = await _run_gh_command(
        [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "title,body,author,state,baseRefName,headRefName,url",
        ]
    )

    data = json.loads(output)

    return {
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "author": data.get("author", {}).get("login", ""),
        "state": data.get("state", ""),
        "base_branch": data.get("baseRefName", ""),
        "head_branch": data.get("headRefName", ""),
        "url": data.get("url", ""),
    }


@opcode()
async def github_get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Get the full diff of a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        The PR diff as a string in unified diff format

    Raises:
        RuntimeError: If gh command fails

    Example:
        diff = github_get_pr_diff("anthropics", "claude-code", 123)
        # Returns: "diff --git a/file.py b/file.py\n..."
    """
    output = await _run_gh_command(
        [
            "pr",
            "diff",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
        ]
    )

    return output


@opcode()
async def github_get_pr_files(
    owner: str, repo: str, pr_number: int
) -> List[Dict[str, Any]]:
    """Get list of files changed in a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of dicts, each containing:
        - path: File path relative to repo root
        - additions: Number of lines added
        - deletions: Number of lines deleted
        - status: Change status (added, modified, removed, renamed)

    Raises:
        RuntimeError: If gh command fails

    Example:
        files = github_get_pr_files("anthropics", "claude-code", 123)
        # Returns: [
        #     {"path": "src/main.py", "additions": 10, "deletions": 2, "status": "modified"},
        #     {"path": "README.md", "additions": 5, "deletions": 0, "status": "added"}
        # ]
    """
    output = await _run_gh_command(
        [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "files",
        ]
    )

    data = json.loads(output)
    files = data.get("files", [])

    result = []
    for f in files:
        # Map gh status values to our simplified statuses
        path = f.get("path", "")
        additions = f.get("additions", 0)
        deletions = f.get("deletions", 0)

        # Determine status based on additions/deletions if not provided
        # gh provides additions/deletions but not always explicit status
        if deletions == 0 and additions > 0:
            status = "added"
        elif additions == 0 and deletions > 0:
            status = "removed"
        else:
            status = "modified"

        result.append(
            {
                "path": path,
                "additions": additions,
                "deletions": deletions,
                "status": status,
            }
        )

    return result


# ============================================================================
# File Content
# ============================================================================


@opcode()
async def github_get_file_content(
    owner: str, repo: str, path: str, ref: str = "HEAD"
) -> str:
    """Get file content from a repository at a specific ref.

    Args:
        owner: Repository owner
        repo: Repository name
        path: File path relative to repo root
        ref: Git reference (branch, tag, or commit SHA). Default: "HEAD"

    Returns:
        File content as a string (UTF-8 decoded)

    Raises:
        RuntimeError: If file not found or gh command fails

    Example:
        content = github_get_file_content("anthropics", "claude-code", "README.md")
        # Returns: "# Claude Code\n\nThis project..."

        # Get file from specific branch
        content = github_get_file_content(
            "anthropics", "claude-code", "src/main.py", ref="feature-branch"
        )
    """
    # Use gh api to fetch file content
    # The GitHub API returns base64-encoded content
    output = await _run_gh_command(
        [
            "api",
            f"repos/{owner}/{repo}/contents/{path}",
            "-q",
            ".content",
            "--jq",
            ".content",
            "-H",
            "Accept: application/vnd.github.v3+json",
            "-f",
            f"ref={ref}",
        ]
    )

    # The content is base64-encoded with newlines
    content_b64 = output.strip().replace("\n", "")

    if not content_b64:
        raise RuntimeError(f"File not found or empty: {path}")

    try:
        content_bytes = base64.b64decode(content_b64)
        return content_bytes.decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to decode file content: {e}")


# ============================================================================
# PR Comments
# ============================================================================


@opcode()
async def github_list_pr_comments(
    owner: str, repo: str, pr_number: int
) -> List[Dict[str, Any]]:
    """Get all comments on a PR.

    This includes both review comments (on specific lines) and issue comments
    (general PR discussion).

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of comment dicts, each containing:
        - id: Comment ID
        - author: Comment author username
        - body: Comment text
        - created_at: ISO timestamp of when comment was created
        - type: "review" or "issue" indicating comment type

    Raises:
        RuntimeError: If gh command fails

    Example:
        comments = github_list_pr_comments("anthropics", "claude-code", 123)
        # Returns: [
        #     {
        #         "id": "123456",
        #         "author": "reviewer",
        #         "body": "Looks good!",
        #         "created_at": "2024-01-15T10:30:00Z",
        #         "type": "issue"
        #     }
        # ]
    """
    # Get issue comments (general PR discussion)
    output = await _run_gh_command(
        [
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "comments",
        ]
    )

    data = json.loads(output)
    comments_data = data.get("comments", [])

    result = []
    for c in comments_data:
        result.append(
            {
                "id": str(c.get("id", "")),
                "author": c.get("author", {}).get("login", ""),
                "body": c.get("body", ""),
                "created_at": c.get("createdAt", ""),
                "type": "issue",
            }
        )

    # Also get review comments using the API
    try:
        review_output = await _run_gh_command(
            [
                "api",
                f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
                "--jq",
                ".[].id, .[].user.login, .[].body, .[].created_at",
            ]
        )

        # Parse review comments if any exist
        if review_output.strip():
            review_api_output = await _run_gh_command(
                [
                    "api",
                    f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
                ]
            )

            review_comments = json.loads(review_api_output)
            for c in review_comments:
                result.append(
                    {
                        "id": str(c.get("id", "")),
                        "author": c.get("user", {}).get("login", ""),
                        "body": c.get("body", ""),
                        "created_at": c.get("created_at", ""),
                        "type": "review",
                    }
                )
    except RuntimeError:
        # If review comments API fails, just return issue comments
        pass

    return result


# ============================================================================
# Utility Functions
# ============================================================================


@opcode()
async def github_is_available() -> bool:
    """Check if GitHub CLI is available and authenticated.

    Returns:
        True if gh CLI is installed and can make API calls, False otherwise

    Example:
        if github_is_available():
            pr_info = github_get_pr_info(...)
        else:
            print("GitHub CLI not available")
    """
    if not GH_AVAILABLE:
        return False

    try:
        # Try a simple API call to verify authentication
        await _run_gh_command(["auth", "status"])
        return True
    except RuntimeError:
        return False


@opcode()
async def github_get_repo_info(owner: str, repo: str) -> Dict[str, Any]:
    """Get repository metadata.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Dict with repo metadata:
        - name: Repository name
        - full_name: Full name (owner/repo)
        - description: Repository description
        - default_branch: Default branch name
        - url: Repository web URL
        - is_private: Whether repo is private

    Raises:
        RuntimeError: If gh command fails

    Example:
        repo_info = github_get_repo_info("anthropics", "claude-code")
        # Returns: {
        #     "name": "claude-code",
        #     "full_name": "anthropics/claude-code",
        #     "description": "Claude Code CLI",
        #     "default_branch": "main",
        #     "url": "https://github.com/anthropics/claude-code",
        #     "is_private": False
        # }
    """
    output = await _run_gh_command(
        [
            "repo",
            "view",
            f"{owner}/{repo}",
            "--json",
            "name,owner,description,defaultBranchRef,url,isPrivate",
        ]
    )

    data = json.loads(output)

    return {
        "name": data.get("name", ""),
        "full_name": f"{owner}/{repo}",
        "description": data.get("description", ""),
        "default_branch": data.get("defaultBranchRef", {}).get("name", "main"),
        "url": data.get("url", ""),
        "is_private": data.get("isPrivate", False),
    }
