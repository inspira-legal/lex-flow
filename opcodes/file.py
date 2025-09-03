from core.opcodes import opcode, BaseOpcode, params

import aiofiles


@params(file_path={"type": str, "description": "Path to the file to read"})
@opcode("file_read")
class FileRead(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        content = await self._read_file(params["file_path"])
        state.push(content)
        return True

    async def _read_file(self, file_path: str) -> str:
        try:
            async with aiofiles.open(file_path, mode="r") as f:
                return await f.read()
        except Exception as e:
            return f"File Load Error: {str(e)}"
