from ..core.opcodes import opcode, BaseOpcode


@opcode("void")
class Void(BaseOpcode):
    async def execute(self, state, node, engine):
        return True
