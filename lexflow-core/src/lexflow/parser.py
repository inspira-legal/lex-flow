import json
import yaml
from pathlib import Path
from typing import Any, Optional, List
from abc import ABC, abstractmethod
from .ast import (
    Literal,
    Variable,
    Call,
    Opcode,
    Assign,
    Block,
    If,
    While,
    For,
    ForEach,
    Fork,
    Return,
    ExprStmt,
    OpStmt,
    Try,
    Catch,
    Throw,
    Workflow,
    Program,
    Expression,
    Statement,
)


# ============= Error Handling =============

class ParseError(Exception):
    """Base exception for parsing errors with context."""

    def __init__(self, message: str, context: Optional[dict] = None):
        self.context = context or {}
        super().__init__(message)


# ============= Parse Context =============

class ParseContext:
    """Context object passed during parsing operations."""

    def __init__(self, parser: 'Parser', all_nodes: dict):
        self.parser = parser
        self.all_nodes = all_nodes
        self.current_workflow = None


# ============= Node Handler Strategy Pattern =============

class NodeHandler(ABC):
    """Abstract base class for node handlers."""

    @abstractmethod
    def can_handle(self, opcode: str) -> bool:
        """Check if this handler can process the given opcode."""
        pass

    @abstractmethod
    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        """Process the node and return a statement."""
        pass


# ============= Expression Parser =============

class ExpressionParser:
    """Handles parsing of expressions from input data."""

    def parse(self, input_data: Any, context: ParseContext) -> Expression:
        """Parse input data into an expression."""
        if not isinstance(input_data, dict):
            return Literal(value=input_data)

        if "literal" in input_data:
            return Literal(value=input_data["literal"])

        elif "variable" in input_data:
            return Variable(name=input_data["variable"])

        elif "workflow_call" in input_data:
            return Call(name=input_data["workflow_call"], args=[])

        elif "node" in input_data:
            return self._parse_node_reference(input_data, context)

        elif "branch" in input_data:
            raise ParseError("Branch reference cannot be parsed as expression")

        else:
            raise ParseError(f"Unknown input type: {list(input_data.keys())}", {"input": input_data})

    def _parse_node_reference(self, data: dict, context: ParseContext) -> Expression:
        """Parse a reporter node reference."""
        node_id = data["node"]
        node = context.all_nodes.get(node_id)

        if not node:
            raise ParseError(f"Reporter node '{node_id}' not found")

        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Special case: variable getter
        if opcode == "data_get_variable":
            var_input = inputs.get("VARIABLE", {})
            if isinstance(var_input, dict) and "literal" in var_input:
                return Variable(name=var_input["literal"])
            raise ParseError("Invalid VARIABLE input in data_get_variable")

        # Special case: workflow call as expression
        if opcode in ("workflow_call", "call"):
            workflow_name = self._extract_workflow_name(inputs)
            args = self._extract_call_arguments(inputs, context)
            return Call(name=workflow_name, args=args)

        # Default: opcode expression
        args = []
        for param_name, param_input in inputs.items():
            arg_expr = self.parse(param_input, context)
            args.append(arg_expr)

        return Opcode(name=opcode, args=args)

    def _extract_workflow_name(self, inputs: dict) -> str:
        """Extract workflow name from WORKFLOW input."""
        workflow_input = inputs.get("WORKFLOW", {})
        if isinstance(workflow_input, dict) and "literal" in workflow_input:
            return workflow_input["literal"]
        raise ParseError("Invalid WORKFLOW input in call", {"input": workflow_input})

    def _extract_call_arguments(self, inputs: dict, context: ParseContext) -> List[Expression]:
        """Extract ARG1, ARG2, ... arguments from inputs."""
        args = []
        i = 1
        while f"ARG{i}" in inputs:
            arg_expr = self.parse(inputs[f"ARG{i}"], context)
            args.append(arg_expr)
            i += 1
        return args


# ============= Concrete Node Handlers =============

class ControlFlowHandler(NodeHandler):
    """Handles control flow nodes (if, while, for, etc.)"""

    OPCODES = {
        "control_if",
        "control_if_else",
        "control_while",
        "control_for",
        "control_foreach",
        "control_fork",
    }

    def can_handle(self, opcode: str) -> bool:
        return opcode in self.OPCODES

    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        handlers = {
            "control_if": lambda i, c: self._handle_if(node_id, i, c),
            "control_if_else": lambda i, c: self._handle_if_else(node_id, i, c),
            "control_while": lambda i, c: self._handle_while(node_id, i, c),
            "control_for": lambda i, c: self._handle_for(node_id, i, c),
            "control_foreach": lambda i, c: self._handle_foreach(node_id, i, c),
            "control_fork": lambda i, c: self._handle_fork(node_id, i, c),
        }

        handler = handlers.get(opcode)
        if handler:
            return handler(inputs, context)
        return None

    def _handle_if(self, node_id: str, inputs: dict, context: ParseContext) -> If:
        cond = context.parser._parse_input(inputs.get("CONDITION", []), context)
        then_branch = context.parser._parse_branch(inputs.get("THEN", []), context)
        return If(cond=cond, then=then_branch, else_=None, node_id=node_id)

    def _handle_if_else(self, node_id: str, inputs: dict, context: ParseContext) -> If:
        cond = context.parser._parse_input(inputs.get("CONDITION", []), context)
        then_branch = context.parser._parse_branch(inputs.get("THEN", []), context)
        else_branch = context.parser._parse_branch(inputs.get("ELSE", []), context)
        return If(cond=cond, then=then_branch, else_=else_branch, node_id=node_id)

    def _handle_while(self, node_id: str, inputs: dict, context: ParseContext) -> While:
        cond = context.parser._parse_input(inputs.get("CONDITION", []), context)
        body = context.parser._parse_branch(inputs.get("BODY", []), context)
        return While(cond=cond, body=body, node_id=node_id)

    def _handle_for(self, node_id: str, inputs: dict, context: ParseContext) -> For:
        var_name = self._extract_variable_name(inputs.get("VAR", {}), "control_for")
        start = context.parser._parse_input(inputs.get("START", {}), context)
        end = context.parser._parse_input(inputs.get("END", {}), context)
        step = context.parser._parse_input(inputs.get("STEP", {}), context) if "STEP" in inputs else None
        body = context.parser._parse_branch(inputs.get("BODY", {}), context)
        return For(var_name=var_name, start=start, end=end, step=step, body=body, node_id=node_id)

    def _handle_foreach(self, node_id: str, inputs: dict, context: ParseContext) -> ForEach:
        var_name = self._extract_variable_name(inputs.get("VAR", {}), "control_foreach")
        iterable = context.parser._parse_input(inputs.get("ITERABLE", {}), context)
        body = context.parser._parse_branch(inputs.get("BODY", {}), context)
        return ForEach(var_name=var_name, iterable=iterable, body=body, node_id=node_id)

    def _handle_fork(self, node_id: str, inputs: dict, context: ParseContext) -> Fork:
        branches = []
        i = 1
        while f"BRANCH{i}" in inputs:
            branch = context.parser._parse_branch(inputs[f"BRANCH{i}"], context)
            if branch:
                branches.append(branch)
            i += 1
        return Fork(branches=branches, node_id=node_id)

    def _extract_variable_name(self, var_input: dict, opcode: str) -> str:
        if isinstance(var_input, dict) and "literal" in var_input:
            return var_input["literal"]
        raise ParseError(f"Invalid VAR input in {opcode}", {"input": var_input})


class DataHandler(NodeHandler):
    """Handles data operations (assign, return)"""

    OPCODES = {"data_set_variable_to", "assign", "workflow_return", "return"}

    def can_handle(self, opcode: str) -> bool:
        return opcode in self.OPCODES

    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        if opcode in ("data_set_variable_to", "assign"):
            return self._handle_assign(node_id, inputs, context)
        elif opcode in ("workflow_return", "return"):
            return self._handle_return(node_id, inputs, context)
        return None

    def _handle_assign(self, node_id: str, inputs: dict, context: ParseContext) -> Assign:
        var_input = inputs.get("VARIABLE", {})
        if not isinstance(var_input, dict) or "literal" not in var_input:
            raise ParseError("Invalid VARIABLE input in assignment", {"input": var_input})

        var_name = var_input["literal"]
        value = context.parser._parse_input(inputs.get("VALUE", {}), context)
        return Assign(name=var_name, value=value, node_id=node_id)

    def _handle_return(self, node_id: str, inputs: dict, context: ParseContext) -> Return:
        values = []

        # Check for multiple return values (VALUE1, VALUE2, ...)
        i = 1
        while f"VALUE{i}" in inputs:
            value_expr = context.parser._parse_input(inputs[f"VALUE{i}"], context)
            values.append(value_expr)
            i += 1

        # Fallback to single VALUE for backward compatibility
        if not values and "VALUE" in inputs:
            value_expr = context.parser._parse_input(inputs["VALUE"], context)
            values.append(value_expr)

        return Return(values=values, node_id=node_id)


class WorkflowHandler(NodeHandler):
    """Handles workflow operations (call)"""

    OPCODES = {"workflow_call", "call"}

    def can_handle(self, opcode: str) -> bool:
        return opcode in self.OPCODES

    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        inputs = node.get("inputs", {})
        workflow_name = self._extract_workflow_name(inputs)
        args = self._extract_arguments(inputs, context)
        call_expr = Call(name=workflow_name, args=args)
        return ExprStmt(expr=call_expr, node_id=node_id)

    def _extract_workflow_name(self, inputs: dict) -> str:
        workflow_input = inputs.get("WORKFLOW", {})
        if isinstance(workflow_input, dict) and "literal" in workflow_input:
            return workflow_input["literal"]
        raise ParseError("Invalid WORKFLOW input in call", {"input": workflow_input})

    def _extract_arguments(self, inputs: dict, context: ParseContext) -> List[Expression]:
        args = []
        i = 1
        while f"ARG{i}" in inputs:
            arg_expr = context.parser._parse_input(inputs[f"ARG{i}"], context)
            args.append(arg_expr)
            i += 1
        return args


class ExceptionHandler(NodeHandler):
    """Handles exception-related nodes (try, throw)"""

    OPCODES = {"control_try", "try_catch", "control_throw"}

    def can_handle(self, opcode: str) -> bool:
        return opcode in self.OPCODES

    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        if opcode in ("control_try", "try_catch"):
            return self._handle_try(node_id, inputs, context)
        elif opcode == "control_throw":
            return self._handle_throw(node_id, inputs, context)
        return None

    def _handle_try(self, node_id: str, inputs: dict, context: ParseContext) -> Try:
        try_body = context.parser._parse_branch(inputs.get("TRY", {}), context)

        handlers = []
        i = 1
        while f"CATCH{i}" in inputs:
            handlers.append(self._parse_catch_handler(inputs[f"CATCH{i}"], context))
            i += 1

        finally_body = None
        if "FINALLY" in inputs:
            finally_body = context.parser._parse_branch(inputs["FINALLY"], context)

        return Try(body=try_body, handlers=handlers, finally_=finally_body, node_id=node_id)

    def _handle_throw(self, node_id: str, inputs: dict, context: ParseContext) -> Throw:
        value = context.parser._parse_input(inputs.get("VALUE", {}), context)
        return Throw(value=value, node_id=node_id)

    def _parse_catch_handler(self, catch_input: dict, context: ParseContext) -> Catch:
        exception_type = catch_input.get("exception_type")
        var_name = catch_input.get("var")
        body = context.parser._parse_branch(catch_input.get("body", {}), context)
        return Catch(exception_type=exception_type, var_name=var_name, body=body)


class DefaultHandler(NodeHandler):
    """Default handler for opcodes without special handling"""

    def can_handle(self, opcode: str) -> bool:
        # Skip special nodes
        return opcode not in ("workflow_start", "start")

    def handle(self, node_id: str, node: dict, context: ParseContext) -> Optional[Statement]:
        opcode = node.get("opcode", "")
        inputs = node.get("inputs", {})

        # Convert regular opcodes to OpStmt
        args = []
        for param_name, param_input in inputs.items():
            arg_expr = context.parser._parse_input(param_input, context)
            args.append(arg_expr)

        return OpStmt(name=opcode, args=args, node_id=node_id)


class Parser:
    """Parse JSON workflows into AST using strategy pattern for node handling."""

    def __init__(self):
        self.current_workflow = None
        # Initialize handlers in priority order (DefaultHandler must be last)
        self.handlers: List[NodeHandler] = [
            ControlFlowHandler(),
            DataHandler(),
            WorkflowHandler(),
            ExceptionHandler(),
            DefaultHandler(),  # Must be last as catch-all
        ]
        self.expr_parser = ExpressionParser()

    def parse_file(self, file_path: str) -> Program:
        """Parse a single JSON or YAML workflow file into a Program."""
        data = self._load_file(file_path)
        return self.parse_json(data)

    def parse_dict(self, data: dict) -> Program:
        """Parse a dictionary directly into a Program.

        Args:
            data: Dictionary containing workflow definition (same structure as JSON/YAML files)

        Returns:
            Program: Parsed program ready for execution

        Example:
            >>> workflow_data = {
            ...     "workflows": [
            ...         {
            ...             "name": "main",
            ...             "interface": {"inputs": ["name"], "outputs": []},
            ...             "variables": {"name": "World"},
            ...             "nodes": {...}
            ...         }
            ...     ]
            ... }
            >>> parser = Parser()
            >>> program = parser.parse_dict(workflow_data)
        """
        return self.parse_json(data)

    def parse_dicts(self, main_data: dict, include_data: list[dict] = None) -> Program:
        """Parse multiple dictionaries (main + includes) into a single Program.

        Args:
            main_data: Main workflow dictionary - its 'main' workflow will be executed
            include_data: List of additional workflow dictionaries - all their workflows
                         (including 'main') become callable external workflows

        Returns:
            Program: Merged program with main workflow and externals

        Example:
            >>> main = {"workflows": [{"name": "main", ...}]}
            >>> helpers = {"workflows": [{"name": "helper1", ...}, {"name": "helper2", ...}]}
            >>> parser = Parser()
            >>> program = parser.parse_dicts(main, [helpers])
        """
        include_data = include_data or []

        # Parse main workflows
        main_workflows = main_data.get("workflows", [])
        if not main_workflows:
            raise ValueError("No workflows found in main data")

        # Find the main workflow
        main_workflow = None
        external_workflows = {}

        for wf_data in main_workflows:
            workflow = self._parse_workflow(wf_data)
            if workflow.name == "main":
                main_workflow = workflow
            else:
                external_workflows[workflow.name] = workflow

        if not main_workflow:
            raise ValueError("No 'main' workflow found in main data")

        # Parse included dictionaries - all workflows become externals
        for idx, include_dict in enumerate(include_data):
            workflows_data = include_dict.get("workflows", [])

            if not workflows_data:
                raise ValueError(f"No workflows found in include data at index {idx}")

            for wf_data in workflows_data:
                workflow = self._parse_workflow(wf_data)

                # Check for name conflicts
                if workflow.name in external_workflows:
                    raise ValueError(
                        f"Duplicate workflow name '{workflow.name}' in include data. "
                        f"Already defined in another workflow."
                    )

                external_workflows[workflow.name] = workflow

        # Extract global variables from main workflow
        globals_dict = main_workflow.locals.copy()

        return Program(
            globals=globals_dict, externals=external_workflows, main=main_workflow
        )

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
        """Parse nodes into a Block statement using strategy pattern."""
        # Find the start node
        if "start" not in nodes:
            raise ValueError("No 'start' node found in workflow")

        # Create parse context
        context = ParseContext(self, nodes)
        context.current_workflow = self.current_workflow

        # Follow the node chain
        statements = []
        current_node_id = nodes["start"].get("next")

        while current_node_id:
            node = nodes.get(current_node_id)
            if not node:
                break

            # Parse the node into a statement using handlers
            try:
                stmt = self._parse_node(current_node_id, node, context)
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                # Convert ParseError to ValueError for backwards compatibility
                raise ValueError(str(e)) from e

            # Move to next node
            current_node_id = node.get("next")

        return Block(stmts=statements)

    def _parse_node(
        self, node_id: str, node: dict, context: ParseContext
    ) -> Statement | None:
        """Parse a single node using appropriate handler."""
        opcode = node.get("opcode", "")

        # Try each handler in priority order
        for handler in self.handlers:
            if handler.can_handle(opcode):
                return handler.handle(node_id, node, context)

        # No handler found (shouldn't happen with DefaultHandler)
        return None

    def _parse_input(self, input_data: Any, context: ParseContext) -> Expression:
        """Parse an input value into an expression using ExpressionParser."""
        try:
            return self.expr_parser.parse(input_data, context)
        except ParseError as e:
            # Convert ParseError to ValueError for backwards compatibility
            raise ValueError(str(e)) from e

    def _parse_branch(self, branch_input: Any, context: ParseContext) -> Statement | None:
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
            node = context.all_nodes.get(current_node_id)
            if not node:
                break

            try:
                stmt = self._parse_node(current_node_id, node, context)
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                raise ValueError(str(e)) from e

            current_node_id = node.get("next")

        if not statements:
            return None

        return Block(stmts=statements) if len(statements) > 1 else statements[0]
