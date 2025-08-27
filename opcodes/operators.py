from core.opcodes import opcode, BaseOpcode


@opcode("operator_equals")
class OperatorEquals(BaseOpcode):
    def execute(self, state, node, engine):
        op2 = state.pop()
        op1 = state.pop()

        print(f"OP1: {op1}, OP2: {op2}")
        if op1 == op2:
            state.push(True)
        else:
            state.push(False)

        return True
