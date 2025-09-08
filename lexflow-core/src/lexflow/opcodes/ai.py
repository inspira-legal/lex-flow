import aiofiles
from ..core.opcodes import opcode, BaseOpcode, params
from pydantic_ai import Agent, DocumentUrl, BinaryContent
from pydantic_ai.models import Model
from pydantic_ai.models.google import GoogleModel, GoogleProvider
from lexflow.utils.ai import StructuredAnswer, format_structured_answer
from pathlib import Path


@params(
    agent={"type": Agent, "description": "AI agent to call"},
    user_input={"type": "Any", "description": "Input to send to the agent"},
)
@opcode("ai_call_agent")
class AiCallAgent(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._call_agent(params["agent"], params["user_input"])
        state.push(result)
        return True

    async def _call_agent(self, agent: Agent, user_input):
        if isinstance(user_input, list):
            input = user_input
        else:
            input = [user_input]
        try:
            result = await agent.run(input)
            return result.output
        except Exception as e:
            return f"AI Error: {str(e)}"


@params(
    model={"type": Model, "description": "AI model to use"},
    system_prompt={"type": str, "description": "System prompt for the agent"},
    agent_name={
        "type": str,
        "description": "Optional agent name",
        "required": False,
        "default": None,
    },
    output_type={
        "type": type,
        "description": "Output type class",
        "required": False,
        "default": str,
    },
)
@opcode("ai_create_agent")
class AiCreateAgent(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)

        try:
            agent = await self._create_agent(**params)
            state.push(agent)
        except Exception as e:
            error_response = f"AI Error: {str(e)}"
            state.push(error_response)

        return True

    async def _create_agent(
        self, model, system_prompt: str, agent_name: str = None, output_type: type = str
    ):
        provider = GoogleProvider(vertexai=True)

        if not isinstance(model, Model):
            model = GoogleModel(model, provider=provider)

        return Agent(
            model=model,
            system_prompt=system_prompt,
            output_type=output_type,
            name=agent_name,
        )


@params(model_name={"type": str, "description": "Name of the model to create"})
@opcode("ai_create_model")
class AiCreateModel(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        model = await self._create_model(params["model_name"])
        state.push(model)
        return True

    async def _create_model(self, model_name: str):
        provider = GoogleProvider(vertexai=True)
        return GoogleModel(model_name, provider=provider)


@params(
    mime_type={"type": str, "description": "MIME type of the document"},
    file_path={"type": str, "description": "Path to the document file"},
)
@opcode("ai_load_document")
class AiLoadDocument(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._load_document(params["file_path"], params["mime_type"])
        state.push(result)
        return True

    async def _load_document(self, file_path: str, mime_type: str):
        try:
            async with aiofiles.open(file_path, mode="rb") as f:
                content = await f.read()
                return BinaryContent(data=content, media_type=mime_type)
        except Exception as e:
            return f"File Load Error: {str(e)}"


@params(file_path={"type": str, "description": "Path to the prompt file"})
@opcode("ai_load_prompt")
class AiLoadPrompt(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._load_prompt(params["file_path"])
        state.push(result)
        return True

    async def _load_prompt(self, file_path: str) -> str:
        try:
            return Path(file_path).read_text()
        except Exception as e:
            return f"File Load Error: {str(e)}"


@params(
    system_prompt={"type": str, "description": "System prompt for summarization"},
    document_url={"type": str, "description": "URL of the document to summarize"},
)
@opcode("ai_summary")
class AiSummary(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._summarize_document(
            params["system_prompt"], params["document_url"]
        )
        state.push(result)
        return True

    async def _summarize_document(self, system_prompt: str, document_url: str) -> str:
        document = DocumentUrl(url=document_url, media_type="application/pdf")

        try:
            provider = GoogleProvider(vertexai=True)
            model = GoogleModel("gemini-2.5-flash", provider=provider)

            agent = Agent(
                model=model,
                system_prompt=system_prompt,
                output_type=StructuredAnswer,
            )

            result = await agent.run(["This is the document", document])

            if isinstance(result.output, StructuredAnswer):
                return format_structured_answer(result.output)
            else:
                return str(result.output)

        except Exception as e:
            return f"AI Error: {str(e)}"
