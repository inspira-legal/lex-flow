from core.opcodes import opcode, BaseOpcode

import aiofiles


@opcode("file_read")
class FileRead(BaseOpcode):
    async def execute(self, state, stmt, engine):
        file_path = state.pop()

        try:
            async with aiofiles.open(file_path, mode="r") as f:
                content = await f.read()
                state.push(content)
        except Exception as e:
            error_response = f"File Load Error: {str(e)}"
            state.push(error_response)

        return True
