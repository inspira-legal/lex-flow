from core.ast import Program, Statement, Value, ValueType
from core.state import WorkflowState
from core.opcodes import OpcodeRegistry, ControlFlow
from core.models import Node
from core.parser import Parser
from core.models import InputTypes
from core.errors import RuntimeError as LexFlowRuntimeError, WorkflowNotFoundError

from core.models import Workflow


class Engine:
    _state: WorkflowState
    _opcode_registry: OpcodeRegistry

    def __init__(self, program: Program):
        self._state = WorkflowState(program)
        self._opcode_registry = OpcodeRegistry()
        self._opcode_registry.discover_opcodes("opcodes")

        self._current_workflow = "main"
        self._current_node_id = None
        self._call_stack_trace = []

    async def _evaluate_input(self, value: Value):
        if value.type == ValueType.LITERAL:
            return value.data
        elif value.type == ValueType.VARIABLE:
            return self._state._variables[value.data][1]
        elif value.type == ValueType.NODE_REF:
            return await self._execute_reporter(value.data)
        elif value.type == ValueType.BRANCH_REF:
            return value.data
        elif value.type == ValueType.WORKFLOW_CALL:
            return await self._call_workflow(value.data)

    async def _execute_reporter(self, node_id: str):
        node = self._state.program.node_map[node_id]

        inputs = {}
        for name, (input_type, value) in (node.inputs or {}).items():
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
        try:
            await self._evaluate_inputs(stmt)

            if not self._opcode_registry.has_opcode(stmt.opcode):
                raise LexFlowRuntimeError(
                    f"Unknown opcode '{stmt.opcode}'",
                    self._current_workflow,
                    self._current_node_id,
                    stmt.opcode,
                    self._call_stack_trace.copy(),
                )

            opcode_cls = self._opcode_registry.get(stmt.opcode)
            opcode = opcode_cls()
            result = await opcode.execute(self._state, stmt, self)

            if result is False and stmt.opcode != "workflow_return":
                raise LexFlowRuntimeError(
                    f"Opcode '{stmt.opcode}' execution failed",
                    self._current_workflow,
                    self._current_node_id,
                    stmt.opcode,
                    self._call_stack_trace.copy(),
                )
            return result

        except LexFlowRuntimeError:
            raise
        except Exception as e:
            raise LexFlowRuntimeError(
                f"Unexpected error in opcode '{stmt.opcode}': {e}",
                self._current_workflow,
                self._current_node_id,
                stmt.opcode,
                self._call_stack_trace.copy(),
                self._state._variables,
            )

    async def _execute_branch_from_node(self, node_id: str):
        dummy_workflow = Workflow(name="dummy", nodes=self._state.program.node_map)
        parser = Parser(dummy_workflow)
        statements = parser._parse_chain(node_id)
        
        for stmt in statements:
            control_result = await self._execute_statement(stmt)
            
            if control_result == ControlFlow.HALT:
                return ControlFlow.HALT
            elif control_result == ControlFlow.REPEAT:
                return ControlFlow.REPEAT
        
        return ControlFlow.CONTINUE

    async def _call_workflow(self, workflow_name: str):
        if workflow_name not in self._state.program.workflows:
            raise WorkflowNotFoundError(workflow_name, self._current_workflow)

        workflow_def = self._state.program.workflows[workflow_name]

        args = []
        for _ in workflow_def.inputs:
            args.insert(0, self._state.pop())

        local_vars = workflow_def.variables.copy()
        for i, param_name in enumerate(workflow_def.inputs):
            var_id = None
            for vid, (name, _) in local_vars.items():
                if name == param_name:
                    var_id = vid
                    break
            if var_id:
                local_vars[var_id] = [param_name, args[i]]

        saved_variables = self._state._variables
        saved_node_map = self._state.program.node_map
        saved_pc = self._state._pc

        self._state.push_frame(return_pc=saved_pc, locals=local_vars)
        self._state._variables = local_vars

        workflow_nodes = {}

        for node_id, node_data in workflow_def.node_data.items():
            workflow_nodes[node_id] = Node(
                opcode=node_data["opcode"],
                next=node_data.get("next"),
                inputs=node_data.get("inputs", {}),
            )

        self._state.program.node_map = workflow_nodes
        self._state._pc = 0

        try:
            for stmt in workflow_def.body.statements:
                result = await self._execute_statement(stmt)
                if result is False:
                    break
        finally:
            self._state._variables = saved_variables
            self._state.program.node_map = saved_node_map
            self._state._pc = saved_pc
            self._state.pop_frame()

        return self._state.pop() if len(self._state._data_stack) > 0 else None

    async def step(self) -> bool:
        if self._state.is_finished():
            return False

        current_stmt = self._state.current_statement()

        if hasattr(current_stmt, "node_id"):
            self._current_node_id = current_stmt.node_id

        control_result = await self._execute_statement(current_stmt)

        if control_result == ControlFlow.REPEAT:
            pass
        elif control_result == ControlFlow.HALT:
            self._state._pc = len(self._state.program.main.statements)
        elif control_result in [True, ControlFlow.CONTINUE, None]:
            self._state._pc += 1
        else:
            raise LexFlowRuntimeError(
                f"Invalid control flow result: {control_result}",
                self._current_workflow,
                self._current_node_id,
                current_stmt.opcode if hasattr(current_stmt, 'opcode') else "unknown",
                self._call_stack_trace.copy(),
            )

        return True
