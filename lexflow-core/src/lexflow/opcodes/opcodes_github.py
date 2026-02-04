"""GitHub opcodes for LexFlow using the gh CLI.

This module provides opcodes for interacting with GitHub PRs and repositories
using the GitHub CLI (gh). This approach avoids authentication complexity since
gh handles all authentication.

Requires:
    GitHub CLI must be installed and authenticated:
        brew install gh  # or apt install gh
        gh auth login
"""

import asyncio
import base64
import json
import shutil
from typing import Any, Dict, List

from .opcodes import opcode, register_category

# Check if gh CLI is available
GH_AVAILABLE = shutil.which("gh") is not None

# Register category at module load time
register_category(
    id="github",
    label="GitHub Operations",
    prefix="github_",
    color="#24292F",
    icon="🐙",
    order=260,
)


def _check_gh():
    """Check if gh CLI is available."""
    if not GH_AVAILABLE:
        raise RuntimeError(
            "GitHub CLI (gh) is not installed. Install with:\n"
            "  brew install gh  # macOS\n"
            "  apt install gh   # Ubuntu/Debian\n"
            "Then authenticate: gh auth login"
        )


async def _run_gh_command(args: List[str], check: bool = True) -> str:
    """Run a gh command and return its output."""
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


@opcode(category="github")
async def github_get_pr_info(owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
    """Get PR metadata from GitHub.

    Args:
        owner: Repository owner (e.g., "anthropics")
        repo: Repository name (e.g., "lex-flow")
        pr_number: Pull request number

    Returns:
        Dict with: title, body, author, state, base_branch, head_branch, url
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


@opcode(category="github")
async def github_get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """Get the full diff of a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        The PR diff as a string in unified diff format
    """
    return await _run_gh_command(
        ["pr", "diff", str(pr_number), "--repo", f"{owner}/{repo}"]
    )


@opcode(category="github")
async def github_get_pr_files(
    owner: str, repo: str, pr_number: int
) -> List[Dict[str, Any]]:
    """Get list of files changed in a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of dicts with: path, additions, deletions, status
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
        path = f.get("path", "")
        additions = f.get("additions", 0)
        deletions = f.get("deletions", 0)

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


@opcode(category="github")
async def github_get_file_content(
    owner: str, repo: str, path: str, ref: str = "HEAD"
) -> str:
    """Get file content from a repository at a specific ref.

    Args:
        owner: Repository owner
        repo: Repository name
        path: File path relative to repo root
        ref: Git reference (branch, tag, or commit SHA)

    Returns:
        File content as a string (UTF-8 decoded)
    """
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

    content_b64 = output.strip().replace("\n", "")

    if not content_b64:
        raise RuntimeError(f"File not found or empty: {path}")

    try:
        content_bytes = base64.b64decode(content_b64)
        return content_bytes.decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"Failed to decode file content: {e}")


@opcode(category="github")
async def github_list_pr_comments(
    owner: str, repo: str, pr_number: int
) -> List[Dict[str, Any]]:
    """Get all comments on a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of comment dicts with: id, author, body, created_at, type
    """
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

    try:
        review_api_output = await _run_gh_command(
            ["api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments"]
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
        pass

    return result


@opcode(category="github")
async def github_is_available() -> bool:
    """Check if GitHub CLI is available and authenticated.

    Returns:
        True if gh CLI is installed and authenticated
    """
    if not GH_AVAILABLE:
        return False

    try:
        await _run_gh_command(["auth", "status"])
        return True
    except RuntimeError:
        return False


@opcode(category="github")
async def github_get_repo_info(owner: str, repo: str) -> Dict[str, Any]:
    """Get repository metadata.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        Dict with: name, full_name, description, default_branch, url, is_private
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
