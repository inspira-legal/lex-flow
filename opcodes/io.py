from core.opcodes import opcode, BaseOpcode


@opcode("io_print")
class PrintOpcode(BaseOpcode):
    def execute(self, state, node):
        value = state.pop()
        print(value, end="")

        return True


@opcode("io_input")
class InputOpcode(BaseOpcode):
    def execute(self, state, node):
        value = input()
        state.push(value)

        return True
