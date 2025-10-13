"""Pydantic AI bindings for LexFlow.

This module provides opcodes for using pydantic_ai agents with Google Vertex AI.

Installation:
    pip install lexflow[ai]

Authentication:
    Vertex AI requires Google Cloud authentication:
    - gcloud auth application-default login
    - Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
"""

from typing import Any, Optional
from .opcodes import default_registry

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.google import GoogleModel
    from pydantic_ai.providers.google import GoogleProvider

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False


def _check_availability():
    """Check if pydantic_ai is available and raise helpful error if not."""
    if not PYDANTIC_AI_AVAILABLE:
        raise ImportError(
            "pydantic-ai is not installed. Install it with:\n"
            "  pip install lexflow[ai]\n"
            "or:\n"
            "  pip install 'pydantic-ai-slim[google]'"
        )


def register_pydantic_ai_opcodes():
    """Register pydantic_ai opcodes to the default registry."""
    if not PYDANTIC_AI_AVAILABLE:
        return

    @default_registry.register()
    async def pydantic_ai_create_vertex_model(
        model_name: str, project: Optional[str] = None, location: Optional[str] = None
    ) -> Any:
        """Create a Google Vertex AI model instance.

        Args:
            model_name: Name of the model (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
            project: Optional GCP project ID (uses default if not specified)
            location: Optional region (e.g., "us-central1", "asia-east1")

        Returns:
            GoogleModel instance configured for Vertex AI

        Example:
            model_name: "gemini-1.5-flash"
            location: "us-central1"

        Authentication:
            Requires Google Cloud authentication via:
            - gcloud auth application-default login
            - Or GOOGLE_APPLICATION_CREDENTIALS environment variable
        """
        _check_availability()

        kwargs = {"vertexai": True}
        if project:
            kwargs["project"] = project
        if location:
            kwargs["location"] = location

        provider = GoogleProvider(**kwargs)
        model = GoogleModel(model_name, provider=provider)
        return model

    @default_registry.register()
    async def pydantic_ai_create_agent(
        model: Any, instructions: str = "", system_prompt: str = ""
    ) -> Any:
        """Create a pydantic_ai Agent.

        Args:
            model: Model instance (from pydantic_ai_create_vertex_model)
            instructions: Optional instructions for the agent
            system_prompt: Optional static system prompt

        Returns:
            Agent instance ready to use

        Example:
            model: { node: vertex_model }
            instructions: "You are a helpful assistant. Be concise."
        """
        _check_availability()

        kwargs = {"model": model}
        if instructions:
            kwargs["instructions"] = instructions
        if system_prompt:
            kwargs["system_prompt"] = system_prompt

        agent = Agent(**kwargs)
        return agent

    @default_registry.register()
    async def pydantic_ai_run_sync(agent: Any, prompt: str) -> str:
        """Run agent with a prompt.

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt/query to send to the agent

        Returns:
            String output from the agent

        Example:
            agent: { node: my_agent }
            prompt: "What is 2+2?"

        Note:
            Both pydantic_ai_run_sync and pydantic_ai_run work identically
            in LexFlow (both are async). The _sync suffix is kept for
            backward compatibility.
        """
        _check_availability()

        result = await agent.run(prompt)
        return result.output

    @default_registry.register()
    async def pydantic_ai_run(agent: Any, prompt: str) -> str:
        """Run agent asynchronously with a prompt.

        Args:
            agent: Agent instance (from pydantic_ai_create_agent)
            prompt: User prompt/query to send to the agent

        Returns:
            String output from the agent

        Example:
            agent: { node: my_agent }
            prompt: "Explain quantum computing in one sentence."
        """
        _check_availability()

        result = await agent.run(prompt)
        return result.output
