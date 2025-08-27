from core.opcodes import opcode, BaseOpcode


@opcode("void")
class Void(BaseOpcode):
    def execute(self, state, node):
        return True
