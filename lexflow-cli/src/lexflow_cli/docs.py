"""Documentation generation from code introspection."""

import inspect
import json
from pathlib import Path
from lexflow.opcodes import default_registry
from lexflow.grammar import get_grammar


def _get_control_flow_opcodes() -> dict[str, str]:
    """Get control flow opcodes from grammar schema."""
    grammar = get_grammar()
    return {c["opcode"]: c["description"] for c in grammar["constructs"]}


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

    sig = default_registry.signatures.get(name)
    is_varargs = False
    if sig:
        params = list(sig.parameters.values())
        if params and params[-1].kind == inspect.Parameter.VAR_POSITIONAL:
            is_varargs = True

    # Get category from registry
    cat = default_registry.get_category(name)
    category_id = cat.id if cat else "other"

    return {
        "name": name,
        "parameters": interface.get("parameters", []),
        "return_type": interface.get("return_type", "Any"),
        "doc": interface.get("doc", ""),
        "is_varargs": is_varargs,
        "category": category_id,
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
    categories_data: dict[str, list] = {}
    for name in default_registry.list_opcodes():
        meta = get_opcode_metadata(name)
        if meta:
            cat = meta["category"]
            if cat not in categories_data:
                categories_data[cat] = []
            categories_data[cat].append(meta)

    # Get categories from registry (sorted by order)
    registry_categories = default_registry.list_categories()

    # Generate table of contents
    lines.append("## Table of Contents")
    lines.append("")
    for cat in registry_categories:
        if cat.id in categories_data:
            anchor = (
                cat.label.lower().replace(" ", "-").replace("(", "").replace(")", "")
            )
            requires_note = (
                f" *(requires `lexflow[{cat.requires}]`)*" if cat.requires else ""
            )
            lines.append(f"- [{cat.icon} {cat.label}](#{anchor}){requires_note}")
    lines.append("")

    # Generate sections
    total_count = 0
    for cat in registry_categories:
        if cat.id not in categories_data:
            continue

        # Section header with optional requires note
        requires_note = ""
        if cat.requires:
            requires_note = f"\n\n> **Requires:** `pip install lexflow[{cat.requires}]`"

        lines.append(f"## {cat.icon} {cat.label}{requires_note}")
        lines.append("")

        opcodes = sorted(categories_data[cat.id], key=lambda x: x["name"])
        total_count += len(opcodes)

        for op in opcodes:
            sig = _format_signature(op["name"], op["parameters"], op["is_varargs"])
            lines.append(f"### {sig}")
            lines.append("")

            if op["doc"]:
                lines.append(inspect.cleandoc(op["doc"]))
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

    # Categories summary
    lines.append("### Categories")
    lines.append("")
    lines.append("| Category | Opcodes | Requires |")
    lines.append("|:---------|--------:|:---------|")
    for cat in registry_categories:
        if cat.id in categories_data:
            count = len(categories_data[cat.id])
            requires = f"`lexflow[{cat.requires}]`" if cat.requires else "-"
            lines.append(f"| {cat.icon} {cat.label} | {count} | {requires} |")
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

    for construct in grammar["constructs"]:
        cat = construct.get("category", "other")
        if cat == "control" or cat == "async":
            control_flow.append(construct)
        elif cat == "data":
            data_ops.append(construct)
        elif cat == "workflow":
            workflow_ops.append(construct)

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


def sync_grammar_categories(grammar_path: Path = None, dry_run: bool = False) -> dict:
    """Sync categories from opcode registry to grammar.json.

    Args:
        grammar_path: Path to grammar.json (default: auto-detect)
        dry_run: If True, don't write changes, just return what would change

    Returns:
        Dict with 'added', 'updated', 'unchanged' lists of category IDs
    """
    # Find grammar.json
    if grammar_path is None:
        # Try to find it relative to lexflow package
        import lexflow

        pkg_path = Path(lexflow.__file__).parent
        grammar_path = pkg_path / "grammar.json"

    if not grammar_path.exists():
        raise FileNotFoundError(f"grammar.json not found at {grammar_path}")

    # Load current grammar
    with open(grammar_path, "r") as f:
        grammar = json.load(f)

    # Get current categories from grammar
    grammar_cats = {c["id"]: c for c in grammar.get("categories", [])}

    # Get categories from registry
    registry_cats = default_registry.list_categories()

    # Track changes
    result = {"added": [], "updated": [], "unchanged": []}

    # Build new categories list
    new_categories = []
    for cat in registry_cats:
        cat_dict = cat.to_dict()

        if cat.id in grammar_cats:
            # Check if different
            existing = grammar_cats[cat.id]
            if cat_dict != existing:
                result["updated"].append(cat.id)
            else:
                result["unchanged"].append(cat.id)
        else:
            result["added"].append(cat.id)

        new_categories.append(cat_dict)

    # Update grammar
    grammar["categories"] = new_categories

    # Write back if not dry run
    if not dry_run:
        with open(grammar_path, "w") as f:
            json.dump(grammar, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return result
