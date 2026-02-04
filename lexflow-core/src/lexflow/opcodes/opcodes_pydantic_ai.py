"""Pydantic AI opcodes for LexFlow.

This module provides opcodes for using pydantic_ai agents with Google Vertex AI.

Installation:
    pip install lexflow[ai]

Authentication:
    Vertex AI requires Google Cloud authentication:
    - gcloud auth application-default login
    - Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
"""

from typing import Any, Optional

from .opcodes import opcode, register_category

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False


def register_pydantic_ai_opcodes():
    """Register pydantic_ai opcodes to the default registry."""
    if not PYDANTIC_AI_AVAILABLE:
        return

    register_category(
        id="pydantic_ai",
        label="AI Operations (Pydantic AI)",
        prefix="pydantic_ai_",
        color="#10B981",
        icon="🤖",
        requires="ai",
        order=200,
    )

    @opcode(category="pydantic_ai")
    async def pydantic_ai_create_vertex_model(
        model_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ) -> Any:
        """Create a Google Vertex AI model instance.

        Args:
            model_name: Model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
            project: Optional GCP project ID (uses default if not specified)
            location: Optional region (e.g., "us-central1")

        Returns:
            GoogleModel instance configured for Vertex AI
        """
        kwargs = {"vertexai": True}
        if project:
            kwargs["project"] = project
        if location:
            kwargs["location"] = location

        provider = GoogleProvider(**kwargs)
        return GoogleModel(model_name, provider=provider)

    @opcode(category="pydantic_ai")
    async def pydantic_ai_create_agent(
        model: Any,
        instructions: str = "",
        system_prompt: str = "",
    ) -> Any:
        """Create a pydantic_ai Agent.

        Args:
            model: Model instance (from pydantic_ai_create_vertex_model)
            instructions: Optional instructions for the agent
            system_prompt: Optional static system prompt

        Returns:
            Agent instance ready to use
        """
        kwargs = {"model": model}
        if instructions:
            kwargs["instructions"] = instructions
        if system_prompt:
            kwargs["system_prompt"] = system_prompt

        return Agent(**kwargs)

    @opcode(category="pydantic_ai")
    async def pydantic_ai_run_sync(agent: Any, prompt: str) -> str:
        """Run agent with a prompt (legacy name, actually async).

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt to send to the agent

        Returns:
            String output from the agent
        """
        result = await agent.run(prompt)
        return result.output

    @opcode(category="pydantic_ai")
    async def pydantic_ai_run(agent: Any, prompt: str) -> str:
        """Run agent asynchronously with a prompt.

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt to send to the agent

        Returns:
            String output from the agent
        """
        result = await agent.run(prompt)
        return result.output
