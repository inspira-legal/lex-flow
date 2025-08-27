from core.opcodes import BaseOpcode, opcode


@opcode("event_start")
class EventStartOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        return True
