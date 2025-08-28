from core.opcodes import opcode, BaseOpcode


@opcode("function_start")
class FunctionStart(BaseOpcode):
    async def execute(self, state, stmt, engine):
        # Function start - parameters should already be set up in variables
        # This is just a marker for clear function entry point
        return True


@opcode("function_return")
class FunctionReturn(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return True


@opcode("function_call")
class FunctionCallOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        inputs = list(stmt.inputs.keys())

        values = []
        for _ in inputs:
            values.append(state.pop())
        values.reverse()

        function_name = values[0]
        args = values[1:]

        for arg in args:
            state.push(arg)

        result = await engine._call_function(function_name)

        # Push the function result back onto the stack
        if result is not None:
            state.push(result)

        return True
