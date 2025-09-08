from ..core.opcodes import opcode, BaseOpcode, params


@params(value={"type": "Any", "description": "Value to print"})
@opcode("io_print")
class PrintOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        await self._print_value(params["value"])
        return True

    async def _print_value(self, value):
        print(value, end="")


@opcode("io_input")
class InputOpcode(BaseOpcode):
    async def execute(self, state, stmt, engine):
        value = await self._get_input()
        state.push(value)
        return True

    async def _get_input(self) -> str:
        return input()
