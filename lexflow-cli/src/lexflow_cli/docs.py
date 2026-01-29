"""Documentation generation from code introspection."""

import inspect
from typing import Any, get_type_hints

from lexflow.opcodes import default_registry

# Control flow opcodes (handled by parser, not callable via registry)
CONTROL_FLOW_OPCODES = {
    "workflow_start": "Entry point for workflow execution",
    "workflow_call": "Call another workflow by name with arguments",
    "control_if": "Conditional branching (if only)",
    "control_if_else": "Conditional branching (if/else)",
    "control_while": "While loop",
    "control_for": "For loop with counter",
    "control_foreach": "Iterate over collection",
    "control_fork": "Execute branches concurrently",
    "control_try": "Exception handling (try/catch/finally)",
    "control_throw": "Raise an exception",
    "control_return": "Return from workflow",
    "control_break": "Break from loop",
    "control_continue": "Continue to next iteration",
    "control_spawn": "Spawn background task",
    "control_async_foreach": "Async iteration over stream",
    "async_timeout": "Timeout wrapper with fallback",
    "control_with": "Async context manager",
}

# Category order and display names
CATEGORY_ORDER = [
    ("io", "I/O Operations"),
    ("operator", "Operators"),
    ("math", "Math Operations"),
    ("string", "String Operations"),
    ("list", "List Operations"),
    ("dict", "Dictionary Operations"),
    ("object", "Object Operations"),
    ("type", "Type Conversions"),
    ("throw", "Exception Operations"),
    ("assert", "Assertion Operations"),
    ("workflow", "Workflow Operations"),
    ("data", "Data Operations"),
    ("control", "Control Flow"),
    ("async", "Async Operations"),
    ("http", "HTTP Operations"),
    ("pydantic_ai", "AI Operations (Pydantic AI)"),
    ("chat", "Chat Operations"),
    ("cli", "CLI Operations"),
    ("github", "GitHub Operations"),
    ("rag", "RAG Operations"),
    ("pygame", "Pygame Operations"),
    ("task", "Task Operations"),
    ("other", "Other Operations"),
]


def _get_category(name: str) -> str:
    """Determine category from opcode name prefix."""
    # Type conversions are special - they don't have a prefix
    if name in ("str", "int", "float", "bool", "len", "range"):
        return "type"

    # Check for known prefixes
    prefixes = [
        "io_",
        "operator_",
        "math_",
        "string_",
        "list_",
        "dict_",
        "object_",
        "throw_",
        "throw",
        "assert_",
        "workflow_",
        "data_",
        "control_",
        "async_",
        "http_",
        "pydantic_ai_",
        "chat_",
        "cli_",
        "github_",
        "rag_",
        "pygame_",
        "task_",
    ]

    for prefix in prefixes:
        if name.startswith(prefix):
            return prefix.rstrip("_")

    return "other"


def _format_type(type_hint: Any) -> str:
    """Format a type hint for display."""
    if type_hint is None:
        return "None"
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__
    return str(type_hint).replace("typing.", "")


def _format_signature(name: str, params: list, is_varargs: bool = False) -> str:
    """Format function signature."""
    parts = []
    for p in params:
        if p["name"] == "args" and is_varargs:
            parts.append(f"*{p['name']}")
        elif p.get("required", True):
            parts.append(p["name"])
        else:
            default = p.get("default", "None")
            if isinstance(default, str):
                default = f'"{default}"'
            parts.append(f"{p['name']}={default}")
    return f"`{name}({', '.join(parts)})`"


def get_opcode_metadata(name: str) -> dict:
    """Extract metadata from opcode function."""
    interface = default_registry.get_interface(name)
    if "error" in interface:
        return None

    # Check if it uses *args
    sig = default_registry.signatures.get(name)
    is_varargs = False
    if sig:
        params = list(sig.parameters.values())
        if params and params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
            is_varargs = True

    return {
        "name": name,
        "parameters": interface.get("parameters", []),
        "return_type": interface.get("return_type", "Any"),
        "doc": interface.get("doc", ""),
        "is_varargs": is_varargs,
        "category": _get_category(name),
    }


def generate_opcode_reference() -> str:
    """Generate OPCODE_REFERENCE.md content from registry introspection."""
    lines = []
    lines.append("# LexFlow Opcode Reference")
    lines.append("")
    lines.append("Quick reference for all available opcodes in LexFlow.")
    lines.append("")
    lines.append(
        "> **Note:** This file is auto-generated. Run `lexflow docs generate` to update."
    )
    lines.append("")

    # Group opcodes by category
    categories: dict[str, list] = {}
    for name in default_registry.list_opcodes():
        meta = get_opcode_metadata(name)
        if meta:
            cat = meta["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(meta)

    # Generate table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for cat_key, cat_name in CATEGORY_ORDER:
        if cat_key in categories:
            anchor = (
                cat_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
            )
            lines.append(f"- [{cat_name}](#{anchor})")
    lines.append("")

    # Generate sections
    total_count = 0
    for cat_key, cat_name in CATEGORY_ORDER:
        if cat_key not in categories:
            continue

        lines.append(f"## {cat_name}")
        lines.append("")

        opcodes = sorted(categories[cat_key], key=lambda x: x["name"])
        total_count += len(opcodes)

        for op in opcodes:
            sig = _format_signature(op["name"], op["parameters"], op["is_varargs"])
            lines.append(f"### {sig}")
            lines.append("")

            if op["doc"]:
                lines.append(op["doc"])
                lines.append("")

            # Parameters table if multiple params
            if len(op["parameters"]) > 1:
                lines.append("**Parameters:**")
                lines.append("")
                for p in op["parameters"]:
                    ptype = p.get("type", "Any")
                    required = "required" if p.get("required", True) else "optional"
                    default_str = ""
                    if not p.get("required", True):
                        default = p.get("default", "None")
                        if isinstance(default, str):
                            default = f'"{default}"'
                        default_str = f", default: `{default}`"
                    lines.append(f"- `{p['name']}` ({ptype}, {required}{default_str})")
                lines.append("")

            # Return type
            lines.append(f"**Returns:** `{op['return_type']}`")
            lines.append("")
            lines.append("---")
            lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"**Total opcodes:** {total_count}")
    lines.append("")

    return "\n".join(lines)
