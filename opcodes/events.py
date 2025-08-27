from core.opcodes import BaseOpcode, opcode


@opcode("event_start")
class EventStartOpcode(BaseOpcode):
    def execute(self, state, stmt, engine):
        return True
