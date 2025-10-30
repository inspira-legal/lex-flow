"""Workflow visualization using Rich library."""

from typing import Any
from rich.tree import Tree
from rich.panel import Panel
from rich.console import Console


class WorkflowVisualizer:
    """Visualize LexFlow workflows as hierarchical tree structure."""

    def __init__(self):
        """Initialize visualizer with console."""
        self.console = Console()

    def visualize_program(self, program_data: dict) -> str:
        """Visualize a complete program with all workflows.

        Args:
            program_data: Raw program dictionary from YAML/JSON

        Returns:
            String representation of the program visualization
        """
        workflows = program_data.get("workflows", [])

        if not workflows:
            return "No workflows found"

        # Separate main workflow from external workflows
        main_workflow = next((w for w in workflows if w.get("name") == "main"), None)
        external_workflows = [w for w in workflows if w.get("name") != "main"]

        # If no main, treat first workflow as main
        if not main_workflow:
            main_workflow = workflows[0]
            external_workflows = workflows[1:]

        # Render main workflow
        result_parts = []
        result_parts.append(self.visualize_workflow(main_workflow))

        # Render external workflows if any
        if external_workflows:
            for workflow in external_workflows:
                # Add separator
                result_parts.append("\n" + "─" * 70 + "\n")
                result_parts.append(self.visualize_workflow(workflow))

        return "".join(result_parts)

    def visualize_workflow(self, workflow_data: dict) -> str:
        """Visualize a single workflow.

        Args:
            workflow_data: Workflow dictionary

        Returns:
            String representation of workflow visualization
        """
        name = workflow_data.get("name", "unnamed")
        variables = workflow_data.get("variables", {})
        interface = workflow_data.get("interface", {})
        inputs = interface.get("inputs", [])
        nodes = workflow_data.get("nodes", {})

        # Create workflow header
        header_text = f"[bold cyan]WORKFLOW:[/bold cyan] {name}"

        # Show interface if defined
        outputs = interface.get("outputs", [])
        if inputs or outputs:
            interface_parts = []
            if inputs:
                interface_parts.append(f"[yellow]inputs:[/yellow] {', '.join(inputs)}")
            if outputs:
                interface_parts.append(
                    f"[yellow]outputs:[/yellow] {', '.join(outputs)}"
                )
            header_text += f"\n[dim]Interface: {' | '.join(interface_parts)}[/dim]"

        # Show variables if defined
        if variables:
            var_str = ", ".join(
                f"{k}={self._format_value(v)}" for k, v in variables.items()
            )
            if len(var_str) > 60:
                var_str = var_str[:57] + "..."
            header_text += f"\n[dim]Variables: {var_str}[/dim]"

        header_panel = Panel(header_text, border_style="cyan", expand=False)

        # Create main tree
        tree = Tree(header_panel)

        # Render execution flow starting from "start" node
        if "start" in nodes:
            start_node = nodes["start"]
            start_next = start_node.get("next")
            if start_next:
                self._render_flow(tree, start_next, nodes, set())

        # Render to string
        with self.console.capture() as capture:
            self.console.print(tree)

        return capture.get()

    def _render_flow(
        self, parent: Tree, node_id: str, all_nodes: dict, visited: set
    ) -> None:
        """Render main execution flow.

        Args:
            parent: Parent tree node
            node_id: Current node ID
            all_nodes: All nodes in workflow
            visited: Set of visited node IDs to prevent cycles
        """
        current_id = node_id

        while current_id and current_id not in visited:
            visited.add(current_id)
            node = all_nodes.get(current_id)

            if not node:
                break

            # Render this node
            node_tree = self._render_node(current_id, node, all_nodes)
            parent.add(node_tree)

            # Move to next
            current_id = node.get("next")

    def _render_node(self, node_id: str, node: dict, all_nodes: dict) -> Tree | Panel:
        """Render a single node.

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree or Panel representing the node
        """
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Check if this is a control flow node
        if opcode in (
            "control_for",
            "control_foreach",
            "control_while",
            "control_if",
            "control_if_else",
            "control_fork",
            "control_try",
        ):
            return self._render_control_flow(node_id, node, all_nodes)

        # Regular node - create panel
        return self._render_regular_node(node_id, opcode, inputs, all_nodes)

    def _render_regular_node(
        self, node_id: str, opcode: str, inputs: dict, all_nodes: dict
    ) -> Tree | Panel:
        """Render a regular (non-control-flow) node.

        Args:
            node_id: Node identifier
            opcode: Opcode name
            inputs: Input dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree or Panel representing the node
        """
        # Check if any inputs are reporter nodes (nested nodes)
        has_reporters = any(
            isinstance(v, dict) and "node" in v for v in inputs.values()
        )

        # If we have reporters, use Tree structure for nesting
        if has_reporters:
            header = f"[bold]{opcode}[/bold] [dim]({node_id})[/dim]"
            tree = Tree(Panel(header, border_style="green", expand=False))

            # Render inputs with nested reporters
            for key, value in inputs.items():
                if isinstance(value, dict) and "node" in value:
                    # Render reporter as nested node
                    reporter_node_id = value["node"]
                    reporter_node = all_nodes.get(reporter_node_id)
                    if reporter_node:
                        reporter_opcode = reporter_node.get("opcode", "")
                        reporter_inputs = reporter_node.get("inputs", {})

                        input_tree = tree.add(f"[yellow]{key}:[/yellow]")
                        reporter_tree = self._render_regular_node(
                            reporter_node_id,
                            reporter_opcode,
                            reporter_inputs,
                            all_nodes,
                        )
                        input_tree.add(reporter_tree)
                else:
                    # Regular value
                    input_text = self._render_value(value, all_nodes)
                    tree.add(f"[yellow]{key}:[/yellow] {input_text}")

            return tree
        else:
            # Simple panel for nodes without reporters
            content_parts = [f"[bold]{opcode}[/bold] [dim]({node_id})[/dim]"]

            # Render inputs
            if inputs:
                for key, value in inputs.items():
                    input_text = self._render_value(value, all_nodes)
                    content_parts.append(f"  [yellow]{key}:[/yellow] {input_text}")

            content = "\n".join(content_parts)
            return Panel(content, border_style="green", expand=False)

    def _render_control_flow(self, node_id: str, node: dict, all_nodes: dict) -> Tree:
        """Render control flow nodes (if, while, for, foreach, fork).

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree representing the control flow structure
        """
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        if opcode == "control_fork":
            return self._render_fork(node_id, node, all_nodes)
        elif opcode in ("control_for", "control_foreach", "control_while"):
            return self._render_loop(node_id, node, all_nodes)
        elif opcode in ("control_if", "control_if_else"):
            return self._render_if(node_id, node, all_nodes)
        elif opcode == "control_try":
            return self._render_try(node_id, node, all_nodes)

        # Fallback
        return Tree(f"{opcode} ({node_id})")

    def _render_loop(self, node_id: str, node: dict, all_nodes: dict) -> Tree:
        """Render loop nodes (for, foreach, while).

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree representing the loop
        """
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Create header
        header_parts = [f"[bold magenta]{opcode}[/bold magenta] [dim]({node_id})[/dim]"]

        # Add loop-specific inputs (keys are uppercase in YAML)
        if opcode == "control_for":
            var_name = self._render_value(
                inputs.get("VAR", inputs.get("var", "i")), all_nodes
            )
            start = self._render_value(
                inputs.get("START", inputs.get("start", 0)), all_nodes
            )
            end = self._render_value(inputs.get("END", inputs.get("end", 0)), all_nodes)
            step = inputs.get("STEP", inputs.get("step"))

            header_parts.append(f"  [yellow]var:[/yellow] {var_name}")
            header_parts.append(f"  [yellow]start:[/yellow] {start}")
            header_parts.append(f"  [yellow]end:[/yellow] {end}")
            if step is not None:
                header_parts.append(
                    f"  [yellow]step:[/yellow] {self._render_value(step, all_nodes)}"
                )

        elif opcode == "control_foreach":
            var_name = self._render_value(
                inputs.get("VAR", inputs.get("var", "item")), all_nodes
            )
            iterable = self._render_value(
                inputs.get("ITERABLE", inputs.get("iterable", [])), all_nodes
            )
            header_parts.append(f"  [yellow]var:[/yellow] {var_name}")
            header_parts.append(f"  [yellow]iterable:[/yellow] {iterable}")

        elif opcode == "control_while":
            condition = self._render_value(
                inputs.get("CONDITION", inputs.get("condition", True)), all_nodes
            )
            header_parts.append(f"  [yellow]condition:[/yellow] {condition}")

        header = "\n".join(header_parts)
        tree = Tree(Panel(header, border_style="magenta", expand=False))

        # Render body branch (key could be BODY or body)
        body_input = inputs.get("BODY", inputs.get("body", {}))
        body_branch = body_input.get("branch") if isinstance(body_input, dict) else None
        if body_branch:
            body_tree = tree.add("[bold]BODY:[/bold]")
            self._render_branch(body_tree, body_branch, all_nodes, set())
            body_tree.add("[dim]↑ loops back[/dim]")

        return tree

    def _render_fork(self, node_id: str, node: dict, all_nodes: dict) -> Tree:
        """Render fork node (concurrent execution).

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree representing the fork
        """
        inputs = node.get("inputs", {})

        header = f"[bold magenta]control_fork[/bold magenta] [dim]({node_id})[/dim]\n[dim]concurrent execution[/dim]"
        tree = Tree(Panel(header, border_style="magenta", expand=False))

        # Collect all branch keys (BRANCH1, BRANCH2, ..., or branches list)
        branch_inputs = []

        # Try list format first (BRANCHES or branches key)
        branches = inputs.get("BRANCHES", inputs.get("branches", []))
        if branches:
            branch_inputs = [
                (i, branch_ref.get("branch") if isinstance(branch_ref, dict) else None)
                for i, branch_ref in enumerate(branches, 1)
            ]
        else:
            # Try individual keys format (BRANCH1, BRANCH2, etc.)
            i = 1
            while f"BRANCH{i}" in inputs:
                branch_ref = inputs[f"BRANCH{i}"]
                branch_id = (
                    branch_ref.get("branch") if isinstance(branch_ref, dict) else None
                )
                branch_inputs.append((i, branch_id))
                i += 1

        # Render each branch
        for i, branch_id in branch_inputs:
            if branch_id:
                branch_tree = tree.add(f"[bold]BRANCH{i}:[/bold]")
                self._render_branch(branch_tree, branch_id, all_nodes, set())

        tree.add("[dim](waits for all branches to complete)[/dim]")
        return tree

    def _render_if(self, node_id: str, node: dict, all_nodes: dict) -> Tree:
        """Render if/if-else node.

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree representing the conditional
        """
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Create header (keys could be CONDITION or condition)
        condition = self._render_value(
            inputs.get("CONDITION", inputs.get("condition", True)), all_nodes
        )
        header = f"[bold magenta]{opcode}[/bold magenta] [dim]({node_id})[/dim]\n  [yellow]condition:[/yellow] {condition}"

        tree = Tree(Panel(header, border_style="magenta", expand=False))

        # Render THEN branch (keys could be THEN or then)
        then_input = inputs.get("THEN", inputs.get("then", {}))
        then_branch = then_input.get("branch") if isinstance(then_input, dict) else None
        if then_branch:
            then_tree = tree.add("[bold]THEN:[/bold]")
            self._render_branch(then_tree, then_branch, all_nodes, set())

        # Render ELSE branch if present (keys could be ELSE or else)
        else_input = inputs.get("ELSE", inputs.get("else", {}))
        else_branch = else_input.get("branch") if isinstance(else_input, dict) else None
        if else_branch:
            else_tree = tree.add("[bold]ELSE:[/bold]")
            self._render_branch(else_tree, else_branch, all_nodes, set())

        return tree

    def _render_try(self, node_id: str, node: dict, all_nodes: dict) -> Tree:
        """Render try-catch-finally node.

        Args:
            node_id: Node identifier
            node: Node dictionary
            all_nodes: All nodes in workflow

        Returns:
            Tree representing the try block
        """
        inputs = node.get("inputs", {})

        header = f"[bold magenta]control_try[/bold magenta] [dim]({node_id})[/dim]"
        tree = Tree(Panel(header, border_style="magenta", expand=False))

        # Render TRY body (keys could be TRY, BODY, or body)
        try_input = inputs.get("TRY", inputs.get("BODY", inputs.get("body", {})))
        try_branch = try_input.get("branch") if isinstance(try_input, dict) else None
        if try_branch:
            try_tree = tree.add("[bold]TRY:[/bold]")
            self._render_branch(try_tree, try_branch, all_nodes, set())

        # Collect CATCH handlers from both formats
        # Format 1: HANDLERS list
        handlers_list = inputs.get("HANDLERS", inputs.get("handlers", []))

        # Format 2: Individual CATCH1, CATCH2, etc. keys
        catch_handlers = []
        i = 1
        while f"CATCH{i}" in inputs:
            catch_input = inputs[f"CATCH{i}"]
            if isinstance(catch_input, dict):
                # Extract handler info
                exception_type = catch_input.get("exception_type", "Exception")
                var_name = catch_input.get("var", catch_input.get("var_name"))
                body_info = catch_input.get("body", {})
                handler_branch = (
                    body_info.get("branch") if isinstance(body_info, dict) else None
                )

                catch_handlers.append(
                    {
                        "exception_type": exception_type,
                        "var_name": var_name,
                        "branch": handler_branch,
                    }
                )
            i += 1

        # Use whichever format has data
        all_handlers = handlers_list if handlers_list else catch_handlers

        # Render CATCH handlers
        for handler in all_handlers:
            if isinstance(handler, dict):
                handler_branch = handler.get("branch")
                exception_type = handler.get("exception_type", "Exception")
                var_name = handler.get("var_name")

                catch_label = f"[bold]CATCH {exception_type}:[/bold]"
                if var_name:
                    catch_label += f" [dim]as {var_name}[/dim]"

                if handler_branch:
                    catch_tree = tree.add(catch_label)
                    self._render_branch(catch_tree, handler_branch, all_nodes, set())

        # Render FINALLY (keys could be FINALLY or finally)
        finally_input = inputs.get("FINALLY", inputs.get("finally", {}))
        finally_branch = (
            finally_input.get("branch") if isinstance(finally_input, dict) else None
        )
        if finally_branch:
            finally_tree = tree.add("[bold]FINALLY:[/bold]")
            self._render_branch(finally_tree, finally_branch, all_nodes, set())

        return tree

    def _render_branch(
        self, parent: Tree, branch_id: str, all_nodes: dict, visited: set
    ) -> None:
        """Render a branch (sequence of nodes not in main flow).

        Args:
            parent: Parent tree node
            branch_id: Starting node ID of branch
            all_nodes: All nodes in workflow
            visited: Set of visited node IDs
        """
        current_id = branch_id

        while current_id and current_id not in visited:
            visited.add(current_id)
            node = all_nodes.get(current_id)

            if not node:
                break

            # Render this node
            node_tree = self._render_node(current_id, node, all_nodes)
            parent.add(node_tree)

            # Move to next
            current_id = node.get("next")

    def _render_value(self, value: Any, all_nodes: dict, depth: int = 0) -> str:
        """Render a value (literal, variable, or reporter node).

        Args:
            value: Value to render
            all_nodes: All nodes in workflow
            depth: Current nesting depth

        Returns:
            String representation of the value
        """
        # Limit nesting to prevent infinite recursion
        if depth > 3:
            return "[dim]...[/dim]"

        # Check if it's a node reference (reporter)
        if isinstance(value, dict):
            # Literal value
            if "literal" in value:
                return self._format_value(value["literal"])

            # Variable reference
            elif "variable" in value:
                var_name = value["variable"]
                return f"[cyan]Variable({var_name})[/cyan]"

            # Node reference (reporter)
            elif "node" in value:
                node_id = value["node"]
                node = all_nodes.get(node_id)
                if node:
                    opcode = node.get("opcode", "")
                    inputs = node.get("inputs", {})

                    # Render reporter inline
                    input_strs = []
                    for key, val in inputs.items():
                        input_strs.append(
                            f"{key}={self._render_value(val, all_nodes, depth + 1)}"
                        )

                    inputs_repr = ", ".join(input_strs) if input_strs else ""
                    return f"[green]⟨{node_id}⟩ {opcode}({inputs_repr})[/green]"

                return f"[green]⟨{node_id}⟩[/green]"

            # Branch reference
            elif "branch" in value:
                return f"[blue]→branch({value['branch']})[/blue]"

            # Workflow call
            elif "workflow_call" in value:
                return f"[blue]→workflow({value['workflow_call']})[/blue]"

            # Regular dict
            else:
                return self._format_value(value)

        # Regular value
        return self._format_value(value)

    def _format_value(self, value: Any) -> str:
        """Format a value for display.

        Args:
            value: Value to format

        Returns:
            Formatted string representation
        """
        if isinstance(value, str):
            # Escape and truncate long strings
            if len(value) > 50:
                return repr(value[:47] + "...")
            return repr(value)
        elif isinstance(value, (list, tuple)):
            if len(value) > 3:
                items = ", ".join(repr(v) for v in value[:3])
                return f"[{items}, ...]"
            return repr(value)
        elif isinstance(value, dict):
            if len(value) > 3:
                items = list(value.items())[:2]
                items_str = ", ".join(f"{k}={v}" for k, v in items)
                return f"{{{items_str}, ...}}"
            return repr(value)
        else:
            return str(value)
