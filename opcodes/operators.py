from core.opcodes import opcode, BaseOpcode


@opcode("operator_equals")
class OperatorEquals(BaseOpcode):
    def execute(self, state, node):
        op2 = state.pop()
        op1 = state.pop()

        if bool(op1) == bool(op2):
            state.push(True)
        else:
            state.push(False)

        return True
