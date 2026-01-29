"""Documentation generation from code introspection."""

import inspect
from typing import Any, get_type_hints

from lexflow.opcodes import default_registry
from lexflow.grammar import get_grammar


def _get_control_flow_opcodes() -> dict[str, str]:
    """Get control flow opcodes from grammar schema."""
    grammar = get_grammar()
    return {c["opcode"]: c["description"] for c in grammar["constructs"]}


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

    # Try grammar categories first
    grammar = get_grammar()
    for category in grammar["categories"]:
        if name.startswith(category["prefix"]):
            return category["id"]

    # Fallback prefixes not in grammar
    fallback_prefixes = [
        "object_",
        "throw_",
        "throw",
        "assert_",
        "http_",
        "pydantic_ai_",
        "chat_",
        "cli_",
        "github_",
        "rag_",
        "pygame_",
        "task_",
    ]

    for prefix in fallback_prefixes:
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


def generate_grammar_reference() -> str:
    """Generate GRAMMAR_REFERENCE.md content from grammar.json schema."""
    grammar = get_grammar()
    lines = []

    lines.append("# LexFlow Grammar Reference")
    lines.append("")
    lines.append(
        "Reference for all LexFlow language constructs (control flow, data operations, etc.)."
    )
    lines.append("")
    lines.append(
        "> **Note:** This file is auto-generated from `grammar.json`. "
        "Run `lexflow docs generate --grammar` to update."
    )
    lines.append("")

    # Version
    lines.append(f"**Grammar Version:** {grammar['version']}")
    lines.append("")

    # Table of contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Categories](#categories)")
    lines.append("- [Control Flow Constructs](#control-flow-constructs)")
    lines.append("- [Data Operations](#data-operations)")
    lines.append("- [Workflow Operations](#workflow-operations)")
    lines.append("- [Colors Reference](#colors-reference)")
    lines.append("")

    # Categories section
    lines.append("## Categories")
    lines.append("")
    lines.append("| ID | Label | Prefix | Color | Icon |")
    lines.append("|:---|:------|:-------|:------|:-----|")
    for cat in grammar["categories"]:
        lines.append(
            f"| `{cat['id']}` | {cat['label']} | `{cat['prefix']}` | "
            f"`{cat['color']}` | {cat['icon']} |"
        )
    lines.append("")

    # Group constructs by category
    control_flow = []
    data_ops = []
    workflow_ops = []
    other_ops = []

    for construct in grammar["constructs"]:
        cat = construct.get("category", "other")
        if cat == "control" or cat == "async":
            control_flow.append(construct)
        elif cat == "data":
            data_ops.append(construct)
        elif cat == "workflow":
            workflow_ops.append(construct)
        else:
            other_ops.append(construct)

    # Control Flow Constructs
    lines.append("## Control Flow Constructs")
    lines.append("")
    for construct in control_flow:
        lines.extend(_format_construct(construct))

    # Data Operations
    if data_ops:
        lines.append("## Data Operations")
        lines.append("")
        for construct in data_ops:
            lines.extend(_format_construct(construct))

    # Workflow Operations
    if workflow_ops:
        lines.append("## Workflow Operations")
        lines.append("")
        for construct in workflow_ops:
            lines.extend(_format_construct(construct))

    # Colors Reference
    lines.append("## Colors Reference")
    lines.append("")

    lines.append("### Branch Colors")
    lines.append("")
    lines.append("| Branch | Color |")
    lines.append("|:-------|:------|")
    for name, color in grammar.get("branch_colors", {}).items():
        lines.append(f"| `{name}` | `{color}` |")
    lines.append("")

    lines.append("### Node Colors")
    lines.append("")
    lines.append("| Node Type | Color |")
    lines.append("|:----------|:------|")
    for name, color in grammar.get("node_colors", {}).items():
        lines.append(f"| `{name}` | `{color}` |")
    lines.append("")

    lines.append("### Reporter Colors")
    lines.append("")
    lines.append("| Category | Color |")
    lines.append("|:---------|:------|")
    for name, color in grammar.get("reporter_colors", {}).items():
        lines.append(f"| `{name}` | `{color}` |")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Categories:** {len(grammar['categories'])}")
    lines.append(f"- **Constructs:** {len(grammar['constructs'])}")
    lines.append(f"- **Control Flow:** {len(control_flow)}")
    lines.append(f"- **Data Operations:** {len(data_ops)}")
    lines.append(f"- **Workflow Operations:** {len(workflow_ops)}")
    lines.append("")

    return "\n".join(lines)


def _format_construct(construct: dict) -> list[str]:
    """Format a single construct for documentation."""
    lines = []

    # Header
    lines.append(f"### `{construct['opcode']}`")
    lines.append("")

    # Display name and description
    lines.append(f"**{construct['display_name']}** - {construct['description']}")
    lines.append("")

    # Metadata
    lines.append(f"- **AST Class:** `{construct['ast_class']}`")
    lines.append(f"- **Category:** `{construct['category']}`")
    lines.append("")

    # Inputs
    if construct.get("inputs"):
        lines.append("**Inputs:**")
        lines.append("")
        lines.append("| Name | Type | Label | Required | Default |")
        lines.append("|:-----|:-----|:------|:---------|:--------|")
        for inp in construct["inputs"]:
            required = "Yes" if inp.get("required", True) else "No"
            default = inp.get("default", "-")
            if default != "-":
                default = f"`{default}`"
            value_type = inp.get("value_type", "-")
            lines.append(
                f"| `{inp['name']}` | `{inp['type']}` ({value_type}) | "
                f"{inp['label']} | {required} | {default} |"
            )
        lines.append("")

    # Branches
    if construct.get("branches"):
        lines.append("**Branches:**")
        lines.append("")
        lines.append("| Name | Label | Color | Required |")
        lines.append("|:-----|:------|:------|:---------|")
        for branch in construct["branches"]:
            required = "Yes" if branch.get("required", True) else "No"
            lines.append(
                f"| `{branch['name']}` | {branch['label']} | "
                f"`{branch['color']}` | {required} |"
            )
        lines.append("")

        if construct.get("dynamic_branches"):
            lines.append("*This construct supports dynamic branches.*")
            lines.append("")

    if construct.get("dynamic_inputs"):
        lines.append(
            "*This construct supports dynamic inputs (e.g., ARG1, ARG2, ...).*"
        )
        lines.append("")

    lines.append("---")
    lines.append("")

    return lines
