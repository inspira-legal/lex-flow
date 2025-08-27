from core.ast import Program, Statement, Value, ValueType
from core.state import WorkflowState
from core.opcodes import OpcodeRegistry
from core.parser import Parser


class Engine:
    _state: WorkflowState
    _opcode_registry: OpcodeRegistry

    def __init__(self, program: Program):
        self._state = WorkflowState(program)
        self._opcode_registry = OpcodeRegistry()
        self._opcode_registry.discover_opcodes("opcodes")

    def _evaluate_input(self, value: Value):
        if value.type == ValueType.LITERAL:
            return value.data
        elif value.type == ValueType.VARIABLE:
            return self._state._variables[value.data][1]
        elif value.type == ValueType.NODE_REF:
            return self._execute_reporter(value.data)
        elif value.type == ValueType.BRANCH_REF:
            return value.data
    
    def _execute_reporter(self, node_id: str):
        node = self._state.program.node_map[node_id]
        
        inputs = {}
        for name, (input_type, value) in (node.inputs or {}).items():
            from core.models import InputTypes
            if input_type == InputTypes.LITERAL.value:
                inputs[name] = Value(type=ValueType.LITERAL, data=value)
            elif input_type == InputTypes.VARIABLE_REF.value:
                inputs[name] = Value(type=ValueType.VARIABLE, data=value)
            elif input_type == InputTypes.NODE_REF.value:
                inputs[name] = Value(type=ValueType.NODE_REF, data=value)
            elif input_type == InputTypes.BRANCH_REF.value:
                inputs[name] = Value(type=ValueType.BRANCH_REF, data=value)
        
        reporter_stmt = Statement(opcode=node.opcode, inputs=inputs)
        
        saved_pc = self._state._pc
        self._execute_statement(reporter_stmt)
        self._state._pc = saved_pc
        
        return self._state.pop()

    def _evaluate_inputs(self, stmt: Statement):
        for name, value in stmt.inputs.items():
            result = self._evaluate_input(value)
            self._state.push(result)

    def _execute_statement(self, stmt: Statement):
        self._evaluate_inputs(stmt)
        
        opcode_cls = self._opcode_registry.get(stmt.opcode)
        opcode = opcode_cls()
        if not opcode.execute(self._state, stmt, self):
            print(f"Failure to run opcode {stmt.opcode}")

    def _parse_branch_chain(self, node_id: str) -> list[Statement]:
        from core.models import Workflow
        dummy_workflow = Workflow(name="dummy", nodes=self._state.program.node_map)
        parser = Parser(dummy_workflow)
        return parser._parse_chain(node_id)
    
    def _execute_branch(self, statements: list[Statement]):
        for stmt in statements:
            self._execute_statement(stmt)

    def step(self) -> bool:
        if self._state.is_finished():
            return False

        current_stmt = self._state.current_statement()
        self._execute_statement(current_stmt)
        
        self._state._pc += 1
        return True
