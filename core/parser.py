from core.models import Workflow, InputTypes
from core.ast import Program, StatementList, Statement, Value, ValueType


class Parser:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.nodes = workflow.nodes
        
    def parse(self) -> Program:
        start_id, start_node = self.workflow.get_start_node()
        main_statements = self._parse_chain(start_id)
        
        return Program(
            variables=self.workflow.variables,
            main=StatementList(statements=main_statements),
            node_map=self.nodes
        )
    
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