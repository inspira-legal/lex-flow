from core.models import Workflow, InputTypes, WORKFLOW_START_OPCODE
from core.ast import Program, StatementList, Statement, Value, ValueType, WorkflowDef


class Parser:
    def __init__(self, workflow: Workflow, workflows_data: list = None):
        self.workflow = workflow
        self.nodes = workflow.nodes
        self.workflows_data = workflows_data or []

    def parse(self) -> Program:
        start_id, start_node = self.workflow.get_start_node()
        main_statements = self._parse_chain(start_id)

        workflows = {}
        for workflow_data in self.workflows_data:
            if workflow_data.name != self.workflow.name:
                workflows[workflow_data.name] = self._parse_workflow(workflow_data)

        branches = self._discover_all_branches()
        reporters = self._discover_all_reporters()

        # Also discover reporters from all workflows
        for workflow_data in self.workflows_data:
            workflow_reporters = self._discover_reporters_from_workflow(workflow_data)
            reporters.update(workflow_reporters)

        return Program(
            variables=self.workflow.variables,
            workflows=workflows,
            main=StatementList(statements=main_statements),
            node_map=self.nodes,
            branches=branches,
            reporters=reporters,
        )

    def _parse_workflow(self, workflow_data: Workflow) -> WorkflowDef:
        body_nodes = workflow_data.nodes

        start_node_id = None
        for node_id, node_data in body_nodes.items():
            if node_data.opcode == WORKFLOW_START_OPCODE:
                start_node_id = node_id
                break

        if start_node_id is None:
            raise ValueError(
                f"Workflow '{workflow_data.name}' must have a workflow_start node"
            )

        body_statements = self._parse_workflow_chain(start_node_id, body_nodes)

        return WorkflowDef(
            name=workflow_data.name,
            inputs=workflow_data.interface.inputs,
            outputs=workflow_data.interface.outputs,
            body=StatementList(statements=body_statements),
            variables=workflow_data.variables,
            nodes={node_id: node for node_id, node in body_nodes.items()},
        )

    def _parse_workflow_chain(self, node_id: str, nodes: dict) -> list[Statement]:
        statements = []
        current_id = node_id

        while current_id and current_id in nodes:
            node = nodes[current_id]
            stmt = self._parse_workflow_node(current_id, node)
            statements.append(stmt)
            current_id = getattr(node, "next", None)

        return statements

    def _parse_workflow_node(self, node_id: str, node) -> Statement:
        inputs = {}
        for name, (input_type, value) in (node.inputs or {}).items():
            inputs[name] = self._resolve_input(input_type, value)

        return Statement(opcode=node.opcode, inputs=inputs)

    def _parse_chain(self, node_id: str) -> list[Statement]:
        statements = []
        current_id = node_id

        while current_id:
            node = self.nodes[current_id]
            stmt = self._parse_node(current_id, node)
            statements.append(stmt)
            current_id = node.next

        return statements

    def _parse_node(self, node_id: str, node) -> Statement:
        inputs = {}
        for name, (input_type, value) in (node.inputs or {}).items():
            inputs[name] = self._resolve_input(input_type, value)

        return Statement(opcode=node.opcode, inputs=inputs)

    def _discover_all_branches(self) -> dict[str, list[Statement]]:
        branches = {}

        for node_id, node in self.nodes.items():
            if node.inputs:
                for input_name, (input_type, value) in node.inputs.items():
                    if input_type == InputTypes.BRANCH_REF.value:
                        if value not in branches:
                            branches[value] = self._parse_chain(value)

        return branches

    def _discover_all_reporters(self) -> dict[str, Statement]:
        reporters = {}
        referenced_nodes = set()

        # Find all nodes referenced via NODE_REF
        for node_id, node in self.nodes.items():
            if node.inputs:
                for input_name, (input_type, value) in node.inputs.items():
                    if input_type == InputTypes.NODE_REF.value:
                        referenced_nodes.add(value)

        # Include nodes marked as reporters OR referenced as NODE_REF
        for node_id, node in self.nodes.items():
            if node.is_reporter or node_id in referenced_nodes:
                reporters[node_id] = self._parse_node(node_id, node)

        return reporters

    def _discover_reporters_from_workflow(
        self, workflow_data: Workflow
    ) -> dict[str, Statement]:
        reporters = {}
        referenced_nodes = set()

        # Find all nodes referenced via NODE_REF in this workflow
        for node_id, node in workflow_data.nodes.items():
            if node.inputs:
                for input_name, (input_type, value) in node.inputs.items():
                    if input_type == InputTypes.NODE_REF.value:
                        referenced_nodes.add(value)

        # Include nodes marked as reporters OR referenced as NODE_REF
        for node_id, node in workflow_data.nodes.items():
            if node.is_reporter or node_id in referenced_nodes:
                reporters[node_id] = self._parse_workflow_node(node_id, node)

        return reporters

    def _resolve_input(self, input_type: int, value) -> Value:
        if input_type == InputTypes.LITERAL.value:
            return Value(type=ValueType.LITERAL, data=value)
        elif input_type == InputTypes.VARIABLE_REF.value:
            return Value(type=ValueType.VARIABLE, data=value)
        elif input_type == InputTypes.NODE_REF.value:
            return Value(type=ValueType.NODE_REF, data=value)
        elif input_type == InputTypes.BRANCH_REF.value:
            return Value(type=ValueType.BRANCH_REF, data=value)
        elif input_type == 5:  # WORKFLOW_CALL
            return Value(type=ValueType.WORKFLOW_CALL, data=value)
