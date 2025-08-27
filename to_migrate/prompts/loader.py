import aiofiles


async def load_prompt(path: str) -> str:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        content = await f.read()
    return content
