from core.opcodes import opcode, BaseOpcode


@opcode("workflow_start")
class WorkflowStart(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return True


@opcode("workflow_return")
class WorkflowReturn(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return True


@opcode("workflow_call")
class WorkflowCallOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        inputs = list(stmt.inputs.keys())

        values = []
        for _ in inputs:
            values.append(state.pop())
        values.reverse()

        workflow_name = values[0]
        args = values[1:]

        for arg in args:
            state.push(arg)

        result = await engine._call_workflow(workflow_name)

        if result is not None:
            state.push(result)

        return True
