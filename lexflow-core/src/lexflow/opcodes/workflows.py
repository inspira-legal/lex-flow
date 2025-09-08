from ..core.opcodes import opcode, BaseOpcode, ControlFlow


@opcode("workflow_start")
class WorkflowStart(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return ControlFlow.CONTINUE


@opcode("workflow_return")
class WorkflowReturn(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return ControlFlow.CONTINUE


@opcode("workflow_call")
class WorkflowCallOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        param_count = len(stmt.inputs)

        all_params = [state.pop() for _ in range(param_count)]

        workflow_name = all_params[-1]
        args = all_params[:-1]

        for arg in reversed(args):
            state.push(arg)

        result = await engine._call_workflow(workflow_name)

        if result is not None:
            state.push(result)

        return ControlFlow.CONTINUE
