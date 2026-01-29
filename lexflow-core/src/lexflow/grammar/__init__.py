"""Grammar schema loader for LexFlow language constructs.

This module provides the single source of truth for all LexFlow language
constructs including control flow opcodes, their inputs, branches, and colors.
"""

import json
from pathlib import Path
from typing import Any

# Type aliases for grammar structures
Grammar = dict[str, Any]
Construct = dict[str, Any]
Category = dict[str, Any]

_grammar: Grammar | None = None


def get_grammar() -> Grammar:
    """Load and cache the grammar schema."""
    global _grammar
    if _grammar is None:
        path = Path(__file__).parent.parent / "grammar.json"
        _grammar = json.loads(path.read_text())
    return _grammar


def get_construct(opcode: str) -> Construct | None:
    """Get construct definition by opcode name."""
    for c in get_grammar()["constructs"]:
        if c["opcode"] == opcode:
            return c
    return None


def get_category(category_id: str) -> Category | None:
    """Get category definition by ID."""
    for c in get_grammar()["categories"]:
        if c["id"] == category_id:
            return c
    return None


def get_control_flow_opcodes() -> set[str]:
    """Get all opcodes that are control flow constructs (have branches)."""
    return {
        c["opcode"]
        for c in get_grammar()["constructs"]
        if c.get("branches") and len(c["branches"]) > 0
    }


def get_branch_color(branch_name: str) -> str:
    """Get the color for a branch by name."""
    colors = get_grammar().get("branch_colors", {})
    # Check for CATCH prefix
    if branch_name.startswith("CATCH"):
        return colors.get("CATCH", colors.get("default", "#9C27B0"))
    # Check for BRANCH prefix
    if branch_name.startswith("BRANCH"):
        return colors.get("BRANCH", colors.get("default", "#9C27B0"))
    return colors.get(branch_name, colors.get("default", "#9C27B0"))


def get_node_color(node_type: str) -> str:
    """Get the color for a node type."""
    colors = get_grammar().get("node_colors", {})
    return colors.get(node_type, colors.get("opcode", "#64748B"))


def get_reporter_color(opcode: str) -> str:
    """Get the reporter pill color based on opcode prefix."""
    colors = get_grammar().get("reporter_colors", {})
    for category in get_grammar()["categories"]:
        if opcode.startswith(category["prefix"]):
            return colors.get(category["id"], colors.get("default", "#64748B"))
    return colors.get("default", "#64748B")


def get_construct_branches(opcode: str) -> list[dict[str, Any]]:
    """Get branch definitions for a construct."""
    construct = get_construct(opcode)
    if construct:
        return construct.get("branches", [])
    return []


def get_construct_inputs(opcode: str) -> list[dict[str, Any]]:
    """Get input definitions for a construct."""
    construct = get_construct(opcode)
    if construct:
        return construct.get("inputs", [])
    return []


def is_control_flow_opcode(opcode: str) -> bool:
    """Check if an opcode is a control flow construct."""
    construct = get_construct(opcode)
    if construct:
        branches = construct.get("branches", [])
        return len(branches) > 0
    return False
