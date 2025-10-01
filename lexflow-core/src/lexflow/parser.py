import json
import yaml
from pathlib import Path
from typing import Any
from .ast import (
    Literal,
    Variable,
    Call,
    Opcode,
    Assign,
    Block,
    If,
    While,
    Return,
    ExprStmt,
    OpStmt,
    Workflow,
    Program,
    Expression,
    Statement,
)


class Parser:
    """Parse JSON workflows into AST."""

    def __init__(self):
        self.current_workflow = None

    def parse_file(self, file_path: str) -> Program:
        """Parse a single JSON or YAML workflow file into a Program."""
        data = self._load_file(file_path)
        return self.parse_json(data)

    def parse_files(self, main_file: str, include_files: list[str] = None) -> Program:
        """Parse multiple workflow files and merge them into a single Program.

        Args:
            main_file: Primary workflow file - its 'main' workflow will be executed
            include_files: Additional workflow files - all their workflows (including 'main')
                          become callable external workflows

        The main workflow comes only from main_file.
        Included files can have 'main' workflows but they're treated as external workflows.
        """
        include_files = include_files or []

        # Parse the main file first
        main_data = self._load_file(main_file)
        main_workflows = main_data.get("workflows", [])
        if not main_workflows:
            raise ValueError(f"No workflows found in main file: {main_file}")

        # Find the main workflow from the primary file
        main_workflow = None
        external_workflows = {}

        for wf_data in main_workflows:
            workflow = self._parse_workflow(wf_data)
            if workflow.name == "main":
                main_workflow = workflow
            else:
                external_workflows[workflow.name] = workflow

        if not main_workflow:
            raise ValueError(f"No 'main' workflow found in primary file: {main_file}")

        # Parse included files - all workflows become externals (including 'main' if present)
        for file_path in include_files:
            include_data = self._load_file(file_path)
            workflows_data = include_data.get("workflows", [])

            if not workflows_data:
                raise ValueError(f"No workflows found in included file: {file_path}")

            for wf_data in workflows_data:
                workflow = self._parse_workflow(wf_data)

                # Check for name conflicts
                if workflow.name in external_workflows:
                    raise ValueError(
                        f"Duplicate workflow name '{workflow.name}' in {file_path}. "
                        f"Already defined in another file."
                    )

                external_workflows[workflow.name] = workflow

        # Extract global variables from main workflow
        globals_dict = main_workflow.locals.copy()

        return Program(
            globals=globals_dict, externals=external_workflows, main=main_workflow
        )

    def _load_file(self, file_path: str) -> dict:
        """Load and parse a JSON or YAML file."""
        path = Path(file_path)

        with open(file_path, "r") as f:
            # Detect file format by extension
            if path.suffix.lower() in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                return json.load(f)
            else:
                # Try JSON first, fallback to YAML
                content = f.read()
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content)

    def parse_json(self, data: dict) -> Program:
        """Parse JSON data into a Program."""
        workflows_data = data.get("workflows", [])

        if not workflows_data:
            raise ValueError("No workflows found in JSON")

        # Find main workflow
        main_workflow = None
        external_workflows = {}

        for wf_data in workflows_data:
            workflow = self._parse_workflow(wf_data)
            if workflow.name == "main":
                main_workflow = workflow
            else:
                external_workflows[workflow.name] = workflow

        if not main_workflow:
            raise ValueError("No 'main' workflow found")

        # Extract global variables from main workflow
        globals_dict = main_workflow.locals.copy()

        return Program(
            globals=globals_dict, externals=external_workflows, main=main_workflow
        )

    def _parse_workflow(self, wf_data: dict) -> Workflow:
        """Parse a single workflow."""
        name = wf_data.get("name", "unnamed")
        self.current_workflow = name

        # Parse interface
        interface = wf_data.get("interface", {})
        params = interface.get("inputs", [])

        # Parse variables - only name-based format supported
        variables = wf_data.get("variables", {})

        # Parse nodes
        nodes = wf_data.get("nodes", {})
        body = self._parse_nodes(nodes)

        # Variables are now always in format: {"var_name": default_value}
        locals_dict = variables.copy()

        return Workflow(name=name, params=params, body=body, locals=locals_dict)

    def _parse_nodes(self, nodes: dict) -> Statement:
        """Parse nodes into a Block statement."""
        # Find the start node
        if "start" not in nodes:
            raise ValueError("No 'start' node found in workflow")

        # Follow the node chain
        statements = []
        current_node_id = nodes["start"].get("next")

        while current_node_id:
            node = nodes.get(current_node_id)
            if not node:
                break

            # Parse the node into a statement
            stmt = self._parse_node(current_node_id, node, nodes)
            if stmt:
                statements.append(stmt)

            # Move to next node
            current_node_id = node.get("next")

        return Block(stmts=statements)

    def _parse_node(
        self, node_id: str, node: dict, all_nodes: dict
    ) -> Statement | None:
        """Parse a single node into a statement."""
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Handle special opcodes
        if opcode in ["workflow_start", "start"]:
            # Skip start node
            return None

        elif opcode in ["workflow_return", "return"]:
            # Convert to Return statement
            value_expr = None
            if "VALUE" in inputs:
                value_expr = self._parse_input(inputs["VALUE"], all_nodes)
            return Return(value=value_expr)

        elif opcode in ["data_set_variable_to", "assign"]:
            # Convert to Assign statement
            var_input = inputs.get("VARIABLE", {})
            value_input = inputs.get("VALUE", {})

            # Variable name is in the literal field of the input object
            if isinstance(var_input, dict) and "literal" in var_input:
                var_name = var_input["literal"]
            else:
                raise ValueError("Invalid VARIABLE input in data_set_variable_to")

            value_expr = self._parse_input(value_input, all_nodes)
            return Assign(name=var_name, value=value_expr)

        elif opcode == "control_if_else":
            # Convert to If statement
            cond_expr = self._parse_input(inputs.get("CONDITION", []), all_nodes)
            then_branch = self._parse_branch(inputs.get("BRANCH1", []), all_nodes)
            else_branch = self._parse_branch(inputs.get("BRANCH2", []), all_nodes)
            return If(cond=cond_expr, then=then_branch, else_=else_branch)

        elif opcode == "control_while":
            # Convert to While statement
            cond_expr = self._parse_input(inputs.get("CONDITION", []), all_nodes)
            body_branch = self._parse_branch(inputs.get("SUBSTACK", []), all_nodes)
            return While(cond=cond_expr, body=body_branch)

        elif opcode in ["workflow_call", "call"]:
            # Convert to Call expression wrapped in ExprStmt
            workflow_name_input = inputs.get("WORKFLOW", {})
            if (
                isinstance(workflow_name_input, dict)
                and "literal" in workflow_name_input
            ):
                workflow_name = workflow_name_input["literal"]
            else:
                raise ValueError("Invalid WORKFLOW input in workflow_call")

            # Get arguments
            args = []
            i = 1
            while f"ARG{i}" in inputs:
                arg_expr = self._parse_input(inputs[f"ARG{i}"], all_nodes)
                args.append(arg_expr)
                i += 1

            call_expr = Call(name=workflow_name, args=args)
            return ExprStmt(expr=call_expr)

        else:
            # Regular opcode - convert to OpStmt
            args = []
            for param_name, param_input in inputs.items():
                arg_expr = self._parse_input(param_input, all_nodes)
                args.append(arg_expr)

            return OpStmt(name=opcode, args=args)

    def _parse_input(self, input_data: Any, all_nodes: dict) -> Expression:
        """Parse an input value into an expression."""
        # New object notation format: {"literal": value} or {"node": "id"} etc.
        if isinstance(input_data, dict):
            if "literal" in input_data:
                # Literal value
                return Literal(value=input_data["literal"])

            elif "node" in input_data:
                # Node reference (reporter node)
                return self._parse_reporter_node(input_data["node"], all_nodes)

            elif "variable" in input_data:
                # Variable reference by name
                return Variable(name=input_data["variable"])

            elif "branch" in input_data:
                # Branch reference - shouldn't be here, handled by control flow
                raise ValueError("Branch reference should not be parsed as expression")

            elif "workflow_call" in input_data:
                # Workflow call as an expression (parameterless call)
                # Example: {"workflow_call": "get_value"}
                workflow_name = input_data["workflow_call"]
                return Call(name=workflow_name, args=[])

            else:
                raise ValueError(
                    f"Unknown input type in object: {list(input_data.keys())}"
                )

        else:
            # Fallback: treat as literal if not in expected format
            return Literal(value=input_data)

    def _parse_reporter_node(self, node_id: str, all_nodes: dict) -> Expression:
        """Parse a reporter node into an expression."""
        node = all_nodes.get(node_id)
        if not node:
            raise ValueError(f"Reporter node '{node_id}' not found")

        # Allow nodes to be treated as expressions even if not explicitly marked as reporter
        # This handles cases where nodes are referenced as [2, node_id] in the workflow
        # if not node.get("isReporter", False):
        #     raise ValueError(f"Node '{node_id}' is not a reporter node")

        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Handle special opcodes
        if opcode == "data_get_variable":
            # Convert to Variable reference
            var_input = inputs.get("VARIABLE", {})
            if isinstance(var_input, dict) and "literal" in var_input:
                var_name = var_input["literal"]
                return Variable(name=var_name)
            else:
                raise ValueError("Invalid VARIABLE input in data_get_variable")

        # Parse inputs into argument expressions
        args = []
        for param_name, param_input in inputs.items():
            arg_expr = self._parse_input(param_input, all_nodes)
            args.append(arg_expr)

        # Return as Opcode expression
        return Opcode(name=opcode, args=args)

    def _parse_branch(self, branch_input: Any, all_nodes: dict) -> Statement | None:
        """Parse a branch reference into a statement."""
        if not isinstance(branch_input, dict):
            return None

        if "branch" not in branch_input:
            raise ValueError("Expected branch reference with 'branch' key")

        branch_node_id = branch_input["branch"]

        # Follow the branch chain
        statements = []
        current_node_id = branch_node_id

        while current_node_id:
            node = all_nodes.get(current_node_id)
            if not node:
                break

            stmt = self._parse_node(current_node_id, node, all_nodes)
            if stmt:
                statements.append(stmt)

            current_node_id = node.get("next")

        if not statements:
            return None

        return Block(stmts=statements) if len(statements) > 1 else statements[0]
