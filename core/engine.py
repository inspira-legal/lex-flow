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

    async def _evaluate_input(self, value: Value):
        if value.type == ValueType.LITERAL:
            return value.data
        elif value.type == ValueType.VARIABLE:
            return self._state._variables[value.data][1]
        elif value.type == ValueType.NODE_REF:
            return await self._execute_reporter(value.data)
        elif value.type == ValueType.BRANCH_REF:
            return value.data
        elif value.type == ValueType.FUNCTION_CALL:
            return await self._call_function(value.data)

    async def _execute_reporter(self, node_id: str):
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
        await self._execute_statement(reporter_stmt)
        self._state._pc = saved_pc

        return self._state.pop()

    async def _evaluate_inputs(self, stmt: Statement):
        for name, value in stmt.inputs.items():
            result = await self._evaluate_input(value)
            self._state.push(result)

    async def _execute_statement(self, stmt: Statement):
        await self._evaluate_inputs(stmt)

        opcode_cls = self._opcode_registry.get(stmt.opcode)
        opcode = opcode_cls()
        if not await opcode.execute(self._state, stmt, self):
            print(f"Failure to run opcode {stmt.opcode}")

    def _parse_branch_chain(self, node_id: str) -> list[Statement]:
        from core.models import Workflow

        dummy_workflow = Workflow(name="dummy", nodes=self._state.program.node_map)
        parser = Parser(dummy_workflow)
        return parser._parse_chain(node_id)

    async def _execute_branch(self, statements: list[Statement]):
        for stmt in statements:
            await self._execute_statement(stmt)

    async def _call_function(self, function_name: str):
        if function_name not in self._state.program.functions:
            raise Exception(f"Unknown function: {function_name}")

        function_def = self._state.program.functions[function_name]

        args = []
        for _ in function_def.inputs:
            args.insert(0, self._state.pop())

        local_vars = function_def.variables.copy()
        for i, param_name in enumerate(function_def.inputs):
            var_id = None
            for vid, (name, _) in local_vars.items():
                if name == param_name:
                    var_id = vid
                    break
            if var_id:
                local_vars[var_id] = [param_name, args[i]]

        self._state.push_frame(return_pc=self._state._pc, locals=local_vars)

        saved_variables = self._state._variables
        self._state._variables = local_vars

        try:
            for stmt in function_def.body.statements:
                await self._execute_statement(stmt)
        finally:
            self._state._variables = saved_variables
            self._state.pop_frame()

        return self._state.pop() if self._state else None

    async def step(self) -> bool:
        if self._state.is_finished():
            return False

        current_stmt = self._state.current_statement()
        await self._execute_statement(current_stmt)

        self._state._pc += 1
        return True
