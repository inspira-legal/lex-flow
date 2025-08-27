from core.models import Workflow, InputTypes
from core.ast import Program, StatementList, Statement, Value, ValueType, FunctionDef


class Parser:
    def __init__(self, workflow: Workflow, functions_data: dict = None):
        self.workflow = workflow
        self.nodes = workflow.nodes
        self.functions_data = functions_data or {}

    def parse(self) -> Program:
        start_id, start_node = self.workflow.get_start_node()
        main_statements = self._parse_chain(start_id)

        functions = {}
        for func_name, func_data in self.functions_data.items():
            functions[func_name] = self._parse_function(func_name, func_data)

        return Program(
            variables=self.workflow.variables,
            functions=functions,
            main=StatementList(statements=main_statements),
            node_map=self.nodes,
        )

    def _parse_function(self, name: str, func_data: dict) -> FunctionDef:
        body_nodes = func_data["body"]["nodes"]

        start_node_id = list(body_nodes.keys())[0]
        body_statements = self._parse_function_chain(start_node_id, body_nodes)

        return FunctionDef(
            name=name,
            inputs=func_data.get("inputs", []),
            outputs=func_data.get("outputs", []),
            body=StatementList(statements=body_statements),
            variables=func_data["body"].get("variables", {}),
        )

    def _parse_function_chain(self, node_id: str, nodes: dict) -> list[Statement]:
        statements = []
        current_id = node_id

        while current_id and current_id in nodes:
            node = nodes[current_id]
            stmt = self._parse_function_node(current_id, node)
            statements.append(stmt)
            current_id = node.get("next")

        return statements

    def _parse_function_node(self, node_id: str, node) -> Statement:
        inputs = {}
        for name, (input_type, value) in (node.get("inputs", {})).items():
            inputs[name] = self._resolve_input(input_type, value)

        return Statement(opcode=node["opcode"], inputs=inputs)

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
        elif input_type == 5:  # FUNCTION_CALL
            return Value(type=ValueType.FUNCTION_CALL, data=value)

