from core.models import Workflow, InputTypes
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

        return Program(
            variables=self.workflow.variables,
            workflows=workflows,
            main=StatementList(statements=main_statements),
            node_map=self.nodes,
        )

    def _parse_workflow(self, workflow_data: Workflow) -> WorkflowDef:
        body_nodes = workflow_data.nodes

        start_node_id = None
        for node_id, node_data in body_nodes.items():
            if node_data.opcode == "workflow_start":
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
            node_data={node_id: node.__dict__ for node_id, node in body_nodes.items()},
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
