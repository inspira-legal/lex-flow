from core.opcodes import opcode, BaseOpcode


@opcode("function_return")
class FunctionReturn(BaseOpcode):
    def execute(self, state, stmt, engine):
        return True


@opcode("function_call")
class FunctionCallOpcode(BaseOpcode):
    def execute(self, state, stmt, engine):
        inputs = list(stmt.inputs.keys())

        values = []
        for _ in inputs:
            values.append(state.pop())
        values.reverse()

        function_name = values[0]
        args = values[1:]

        for arg in args:
            state.push(arg)

        engine._call_function(function_name)

        return True

