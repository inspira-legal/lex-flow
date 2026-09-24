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
    """Get the color for a branch by name (legacy UPPERCASE names included)."""
    colors = get_grammar().get("branch_colors", {})
    name = branch_name.lower()
    # Legacy numbered branches: catch1, branch2, ...
    if name.startswith("catch"):
        name = "catch"
    elif name.startswith("branch"):
        name = "args"
    return colors.get(name, colors.get("default", "#9C27B0"))


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


# Alias opcodes that read the same slots as the construct they stand for
SLOT_ALIASES = {
    "assign": "data_set_variable_to",
    "return": "workflow_return",
    "call": "workflow_call",
    "try_catch": "control_try",
}

# Slots a handler reads that the grammar does not declare as such
OVERRIDE_SLOTS = {
    "workflow_return": {"value"},
    "data_get_variable": {"variable"},
}

# Constructs whose extra keywords are meaningful (a callee's parameters)
OPEN_SLOT_OPCODES = {"workflow_call", "call"}


def get_construct_slots(opcode: str) -> set[str] | None:
    """The named slots a construct accepts, or None when any name is allowed.

    Single source of truth for the parser, which rejects anything else, and for
    the migration, which must drop what the legacy reader never read.
    """
    if opcode in OPEN_SLOT_OPCODES:
        return None

    name = SLOT_ALIASES.get(opcode, opcode)
    if name in OVERRIDE_SLOTS:
        return set(OVERRIDE_SLOTS[name])

    construct = get_construct(name)
    if construct is None:
        return None

    slots = {i["name"] for i in construct.get("inputs", [])}
    slots |= {b["name"] for b in construct.get("branches", [])}
    slots.discard("args")  # a positional family, not a named slot
    return slots


# Constructs that read a positional 'args' list: fork's branches, return's
# values and a call's arguments. On any other construct 'args' is read by nobody.
ARGS_FAMILY_OPCODES = {"control_fork", "workflow_return", "workflow_call"}


def construct_takes_args(opcode: str) -> bool:
    """True when a construct reads a positional 'args' list."""
    if get_construct_slots(opcode) is None and opcode not in OVERRIDE_SLOTS:
        return True  # not a construct: an ordinary opcode binds positionally
    return SLOT_ALIASES.get(opcode, opcode) in ARGS_FAMILY_OPCODES
