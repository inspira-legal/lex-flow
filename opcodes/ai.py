import aiofiles
from core.opcodes import opcode, BaseOpcode, params
from pydantic_ai import Agent, DocumentUrl, BinaryContent
from pydantic_ai.models import Model
from pydantic_ai.models.google import GoogleModel, GoogleProvider
from utils.ai import StructuredAnswer, format_structured_answer
from pathlib import Path


@opcode("ai_call_agent")
class AiCallAgent(BaseOpcode):
    async def execute(self, state, stmt, engine):
        user_input = state.pop()
        agent: Agent = state.pop()

        if isinstance(user_input, list):
            input = user_input
        else:
            input = [user_input]
        try:
            result = await agent.run(input)
            state.push(result.output)

        except Exception as e:
            error_response = f"AI Error: {str(e)}"
            state.push(error_response)

        return True


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


@opcode("ai_create_model")
class AiCreateModel(BaseOpcode):
    async def execute(self, state, stmt, engine):
        model_name = state.pop()

        provider = GoogleProvider(vertexai=True)
        state.push(GoogleModel(model_name, provider=provider))

        return True


@opcode("ai_load_document")
class AiLoadDocument(BaseOpcode):
    async def execute(self, state, stmt, engine):
        file_path = state.pop()
        mime_type = state.pop()

        try:
            async with aiofiles.open(file_path, mode="rb") as f:
                content = await f.read()
                b_content = BinaryContent(data=content, media_type=mime_type)
                state.push(b_content)
        except Exception as e:
            error_response = f"File Load Error: {str(e)}"
            state.push(error_response)

        return True


@opcode("ai_load_prompt")
class AiLoadPrompt(BaseOpcode):
    async def execute(self, state, stmt, engine):
        file_path = state.pop()

        try:
            content = Path(file_path).read_text()
            state.push(content)
        except Exception as e:
            error_response = f"File Load Error: {str(e)}"
            state.push(error_response)

        return True


@opcode("ai_summary")
class AiSummary(BaseOpcode):
    async def execute(self, state, stmt, engine):
        document_url = state.pop()
        system_prompt = state.pop()

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
                output = format_structured_answer(result.output)
                state.push(output)
            else:
                state.push(str(result.output))

        except Exception as e:
            error_response = f"AI Error: {str(e)}"
            state.push(error_response)

        return True
