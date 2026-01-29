"""Visualization service for converting workflows to tree structures."""

from typing import Any


def workflow_to_tree(workflow_data: dict) -> dict:
    """Convert workflow dict to tree structure for web rendering."""
    workflows = workflow_data.get("workflows", [])

    if not workflows:
        # Check if it's a single implicit workflow (keys at root)
        if "nodes" in workflow_data:
            return {
                "type": "project",
                "workflows": [_build_workflow_tree(workflow_data)],
            }
        return {"error": "No workflows found"}

    # Build tree for all workflows
    workflow_trees = []
    main_interface = {"inputs": [], "outputs": []}

    for w in workflows:
        tree = _build_workflow_tree(w)
        workflow_trees.append(tree)
        if tree.get("name") == "main" or not main_interface["inputs"]:
            main_interface = tree.get("interface", {})

    return {"type": "project", "workflows": workflow_trees, "interface": main_interface}


def _build_workflow_tree(workflow: dict) -> dict:
    """Build tree for a single workflow."""
    nodes = workflow.get("nodes", {})
    interface = workflow.get("interface", {})

    tree = {
        "type": "workflow",
        "name": workflow.get("name", "main"),
        "interface": {
            "inputs": interface.get("inputs", []),
            "outputs": interface.get("outputs", []),
        },
        "variables": workflow.get("variables", {}),
        "children": [],
        "orphans": [],
    }

    # Track all visited nodes (including branch nodes and reporters)
    all_visited = set()

    # Follow node chain from start
    start_node = nodes.get("start", {})
    current_id = start_node.get("next")

    while current_id and current_id not in all_visited:
        all_visited.add(current_id)
        node = nodes.get(current_id)
        if not node:
            break

        tree_node = _node_to_tree(current_id, node, nodes, all_visited)
        tree["children"].append(tree_node)
        current_id = node.get("next")

    # Find orphan nodes (nodes not in the connected chain)
    # First, collect reporter IDs from ALL potential orphan nodes
    # This ensures that if orphan A references orphan B as a reporter,
    # B won't appear as a separate orphan
    all_node_ids = set(nodes.keys()) - {"start"}
    potential_orphan_ids = all_node_ids - all_visited

    for node_id in potential_orphan_ids:
        node = nodes.get(node_id, {})
        _collect_reporter_ids(node.get("inputs", {}), nodes, all_visited)

    # Now recalculate orphan_ids with reporter references accounted for
    orphan_ids = all_node_ids - all_visited

    # Build orphan chains: find chain heads (orphans not pointed to by other orphans)
    # and follow their next pointers to maintain chain order
    orphan_next_targets = set()
    for node_id in orphan_ids:
        node = nodes.get(node_id, {})
        next_id = node.get("next")
        if next_id and next_id in orphan_ids:
            orphan_next_targets.add(next_id)

    # Chain heads are orphans that no other orphan points to
    orphan_heads = [oid for oid in orphan_ids if oid not in orphan_next_targets]

    # Process each orphan chain starting from its head
    processed_orphans = set()
    for head_id in sorted(orphan_heads):
        current_id = head_id
        while current_id and current_id not in processed_orphans:
            node = nodes.get(current_id)
            if not node:
                break
            # Skip reporter nodes (they're embedded in other nodes)
            if node.get("isReporter"):
                processed_orphans.add(current_id)
                current_id = (
                    node.get("next") if node.get("next") in orphan_ids else None
                )
                continue

            processed_orphans.add(current_id)
            orphan_tree = _node_to_tree(current_id, node, nodes, all_visited)

            # Include next pointer if it points to another orphan (for chain visualization)
            next_id = node.get("next")
            if next_id and next_id in orphan_ids:
                orphan_tree["next"] = next_id

            tree["orphans"].append(orphan_tree)
            current_id = next_id if next_id in orphan_ids else None

    return tree


def _node_to_tree(node_id: str, node: dict, all_nodes: dict, all_visited: set) -> dict:
    """Convert a single node to tree node.

    Args:
        all_visited: Set that accumulates ALL visited node IDs (mutated in place)
    """
    opcode = node.get("opcode", "")
    inputs = node.get("inputs", {})
    is_reporter = node.get("isReporter", False)

    # Track reporter nodes referenced in inputs
    _collect_reporter_ids(inputs, all_nodes, all_visited)

    tree_node = {
        "id": node_id,
        "type": _get_node_type(opcode),
        "opcode": opcode,
        "isReporter": is_reporter,
        "inputs": _format_inputs(inputs, all_nodes),
        "children": [],
    }

    # Handle control flow branches
    if opcode in ("control_for", "control_foreach", "control_while"):
        tree_node["config"] = _extract_loop_config(opcode, inputs, all_nodes)
        body_input = inputs.get("BODY", inputs.get("body", {}))
        body_branch = body_input.get("branch") if isinstance(body_input, dict) else None
        if body_branch:
            tree_node["children"].append(
                _build_branch("BODY", body_branch, all_nodes, all_visited)
            )

    elif opcode in ("control_if", "control_if_else"):
        then_input = inputs.get("THEN", inputs.get("then", {}))
        then_branch = then_input.get("branch") if isinstance(then_input, dict) else None
        if then_branch:
            tree_node["children"].append(
                _build_branch("THEN", then_branch, all_nodes, all_visited)
            )

        else_input = inputs.get("ELSE", inputs.get("else", {}))
        else_branch = else_input.get("branch") if isinstance(else_input, dict) else None
        if else_branch:
            tree_node["children"].append(
                _build_branch("ELSE", else_branch, all_nodes, all_visited)
            )

    elif opcode == "control_fork":
        tree_node["children"] = _extract_fork_branches(inputs, all_nodes, all_visited)

    elif opcode == "control_try":
        tree_node["children"] = _extract_try_branches(inputs, all_nodes, all_visited)

    return tree_node


def _collect_reporter_ids(inputs: dict, all_nodes: dict, all_visited: set) -> None:
    """Collect all reporter node IDs referenced in inputs."""
    for value in inputs.values():
        if isinstance(value, dict):
            if "node" in value:
                node_id = value["node"]
                if node_id not in all_visited:
                    all_visited.add(node_id)
                    node = all_nodes.get(node_id, {})
                    # Recursively collect from reporter's inputs
                    node_inputs = node.get("inputs", {})
                    _collect_reporter_ids(node_inputs, all_nodes, all_visited)
            elif "branch" in value:
                # Branch references are handled separately
                pass


def _get_node_type(opcode: str) -> str:
    """Determine node type from opcode."""
    if opcode.startswith("control_"):
        return "control_flow"
    elif opcode.startswith("data_"):
        return "data"
    elif opcode.startswith("io_"):
        return "io"
    elif opcode.startswith("operator_"):
        return "operator"
    elif opcode.startswith("workflow_"):
        return "workflow_op"
    return "opcode"


def _format_inputs(inputs: dict, all_nodes: dict) -> dict:
    """Format inputs for display, resolving references."""
    formatted = {}
    for key, value in inputs.items():
        # Skip branch inputs for control flow (handled separately)
        if key in ("BODY", "body", "THEN", "then", "ELSE", "else", "TRY", "FINALLY"):
            continue
        if key.startswith("CATCH") or key.startswith("BRANCH"):
            continue
        if key in ("HANDLERS", "handlers", "BRANCHES", "branches"):
            continue

        formatted[key] = _format_value(value, all_nodes)
    return formatted


def _format_value(value: Any, all_nodes: dict, depth: int = 0) -> dict:
    """Format a value for display. No depth limit - show full reporter tree."""

    if isinstance(value, dict):
        if "literal" in value:
            return {"type": "literal", "value": value["literal"]}
        elif "variable" in value:
            return {"type": "variable", "name": value["variable"]}
        elif "node" in value:
            node_id = value["node"]
            node = all_nodes.get(node_id, {})
            opcode = node.get("opcode", "")
            node_inputs = node.get("inputs", {})
            return {
                "type": "reporter",
                "id": node_id,
                "opcode": opcode,
                "inputs": {
                    k: _format_value(v, all_nodes, depth + 1)
                    for k, v in node_inputs.items()
                    if not k.startswith("CATCH") and k not in ("BODY", "THEN", "ELSE")
                },
            }
        elif "branch" in value:
            return {"type": "branch", "target": value["branch"]}
        elif "workflow_call" in value:
            return {"type": "workflow_call", "name": value["workflow_call"]}
        else:
            return {"type": "dict", "value": value}
    else:
        return {"type": "literal", "value": value}


def _extract_loop_config(opcode: str, inputs: dict, all_nodes: dict) -> dict:
    """Extract loop configuration."""
    config = {}

    if opcode == "control_for":
        config["var"] = _get_raw_value(inputs.get("VAR", inputs.get("var", "i")))
        config["start"] = _get_raw_value(inputs.get("START", inputs.get("start", 0)))
        config["end"] = _get_raw_value(inputs.get("END", inputs.get("end", 0)))
        step = inputs.get("STEP", inputs.get("step"))
        if step is not None:
            config["step"] = _get_raw_value(step)

    elif opcode == "control_foreach":
        config["var"] = _get_raw_value(inputs.get("VAR", inputs.get("var", "item")))
        config["iterable"] = _format_value(
            inputs.get("ITERABLE", inputs.get("iterable", [])), all_nodes
        )

    elif opcode == "control_while":
        config["condition"] = _format_value(
            inputs.get("CONDITION", inputs.get("condition", True)), all_nodes
        )

    return config


def _get_raw_value(value: Any) -> Any:
    """Extract raw value from possible wrapper."""
    if isinstance(value, dict) and "literal" in value:
        return value["literal"]
    return value


def _build_branch(name: str, start_id: str, all_nodes: dict, all_visited: set) -> dict:
    """Build a branch subtree.

    Args:
        all_visited: Set that accumulates ALL visited node IDs (mutated in place)
    """
    branch = {
        "type": "branch",
        "name": name,
        "children": [],
    }

    current_id = start_id
    while current_id and current_id not in all_visited:
        all_visited.add(current_id)
        node = all_nodes.get(current_id)
        if not node:
            break
        branch["children"].append(
            _node_to_tree(current_id, node, all_nodes, all_visited)
        )
        current_id = node.get("next")

    return branch


def _extract_fork_branches(inputs: dict, all_nodes: dict, all_visited: set) -> list:
    """Extract branches from fork node."""
    branches = []

    # Try list format first
    branch_list = inputs.get("BRANCHES", inputs.get("branches", []))
    if branch_list:
        for i, branch_ref in enumerate(branch_list, 1):
            branch_id = (
                branch_ref.get("branch") if isinstance(branch_ref, dict) else None
            )
            if branch_id:
                branches.append(
                    _build_branch(f"BRANCH{i}", branch_id, all_nodes, all_visited)
                )
    else:
        # Try individual keys
        i = 1
        while f"BRANCH{i}" in inputs:
            branch_ref = inputs[f"BRANCH{i}"]
            branch_id = (
                branch_ref.get("branch") if isinstance(branch_ref, dict) else None
            )
            if branch_id:
                branches.append(
                    _build_branch(f"BRANCH{i}", branch_id, all_nodes, all_visited)
                )
            i += 1

    return branches


def _extract_try_branches(inputs: dict, all_nodes: dict, all_visited: set) -> list:
    """Extract branches from try-catch-finally node."""
    branches = []

    # TRY body
    try_input = inputs.get("TRY", inputs.get("BODY", inputs.get("body", {})))
    try_branch = try_input.get("branch") if isinstance(try_input, dict) else None
    if try_branch:
        branches.append(_build_branch("TRY", try_branch, all_nodes, all_visited))

    # CATCH handlers
    handlers = inputs.get("HANDLERS", inputs.get("handlers", []))
    if handlers:
        for i, handler in enumerate(handlers, 1):
            if isinstance(handler, dict):
                handler_branch = handler.get("branch")
                if handler_branch:
                    branch = _build_branch(
                        f"CATCH{i}", handler_branch, all_nodes, all_visited
                    )
                    branch["exception_type"] = handler.get(
                        "exception_type", "Exception"
                    )
                    branch["var_name"] = handler.get("var_name")
                    branches.append(branch)
    else:
        # Try individual CATCH keys
        i = 1
        while f"CATCH{i}" in inputs:
            catch_input = inputs[f"CATCH{i}"]
            if isinstance(catch_input, dict):
                body_info = catch_input.get("body", {})
                handler_branch = (
                    body_info.get("branch") if isinstance(body_info, dict) else None
                )
                if handler_branch:
                    branch = _build_branch(
                        f"CATCH{i}", handler_branch, all_nodes, all_visited
                    )
                    branch["exception_type"] = catch_input.get(
                        "exception_type", "Exception"
                    )
                    branch["var_name"] = catch_input.get(
                        "var", catch_input.get("var_name")
                    )
                    branches.append(branch)
            i += 1

    # FINALLY
    finally_input = inputs.get("FINALLY", inputs.get("finally", {}))
    finally_branch = (
        finally_input.get("branch") if isinstance(finally_input, dict) else None
    )
    if finally_branch:
        branches.append(
            _build_branch("FINALLY", finally_branch, all_nodes, all_visited)
        )

    return branches
