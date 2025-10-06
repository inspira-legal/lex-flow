"""Tests for pydantic_ai opcodes."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from lexflow import default_registry

pytestmark = pytest.mark.asyncio


try:
    import pydantic_ai
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False


@pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
class TestPydanticAIOpcodes:
    """Tests for pydantic_ai opcodes when pydantic-ai is installed."""

    async def test_create_vertex_model_basic(self):
        """Test creating a Vertex AI model with basic parameters."""
        with patch('lexflow.opcodes_pydantic_ai.GoogleProvider') as mock_provider_class, \
             patch('lexflow.opcodes_pydantic_ai.GoogleModel') as mock_model_class:

            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_model = Mock()
            mock_model_class.return_value = mock_model

            result = await default_registry.call(
                "pydantic_ai_create_vertex_model",
                ["gemini-1.5-flash"]
            )

            mock_provider_class.assert_called_once_with(vertexai=True)
            mock_model_class.assert_called_once_with("gemini-1.5-flash", provider=mock_provider)
            assert result == mock_model

    async def test_create_vertex_model_with_project_and_location(self):
        """Test creating a Vertex AI model with project and location."""
        with patch('lexflow.opcodes_pydantic_ai.GoogleProvider') as mock_provider_class, \
             patch('lexflow.opcodes_pydantic_ai.GoogleModel') as mock_model_class:

            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_model = Mock()
            mock_model_class.return_value = mock_model

            result = await default_registry.call(
                "pydantic_ai_create_vertex_model",
                ["gemini-1.5-pro", "my-project", "asia-east1"]
            )

            mock_provider_class.assert_called_once_with(
                vertexai=True,
                project="my-project",
                location="asia-east1"
            )
            mock_model_class.assert_called_once_with("gemini-1.5-pro", provider=mock_provider)
            assert result == mock_model

    async def test_create_agent_minimal(self):
        """Test creating an agent with minimal parameters."""
        with patch('lexflow.opcodes_pydantic_ai.Agent') as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent",
                [mock_model]
            )

            mock_agent_class.assert_called_once_with(model=mock_model)
            assert result == mock_agent

    async def test_create_agent_with_instructions(self):
        """Test creating an agent with instructions."""
        with patch('lexflow.opcodes_pydantic_ai.Agent') as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent",
                [mock_model, "Be helpful and concise"]
            )

            mock_agent_class.assert_called_once_with(
                model=mock_model,
                instructions="Be helpful and concise"
            )
            assert result == mock_agent

    async def test_create_agent_with_instructions_and_system_prompt(self):
        """Test creating an agent with both instructions and system prompt."""
        with patch('lexflow.opcodes_pydantic_ai.Agent') as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent",
                [mock_model, "Be helpful", "You are an AI assistant"]
            )

            mock_agent_class.assert_called_once_with(
                model=mock_model,
                instructions="Be helpful",
                system_prompt="You are an AI assistant"
            )
            assert result == mock_agent

    async def test_run_sync(self):
        """Test running an agent synchronously."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.output = "The answer is 4"
        mock_agent.run_sync.return_value = mock_result

        result = await default_registry.call(
            "pydantic_ai_run_sync",
            [mock_agent, "What is 2+2?"]
        )

        mock_agent.run_sync.assert_called_once_with("What is 2+2?")
        assert result == "The answer is 4"

    async def test_run_async(self):
        """Test running an agent asynchronously."""
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.output = "Quantum computing uses quantum mechanics"

        async def mock_run(prompt):
            return mock_result

        mock_agent.run = mock_run

        result = await default_registry.call(
            "pydantic_ai_run",
            [mock_agent, "Explain quantum computing"]
        )

        assert result == "Quantum computing uses quantum mechanics"


@pytest.mark.skipif(PYDANTIC_AI_AVAILABLE, reason="Test only when pydantic-ai is not installed")
async def test_import_error_when_not_installed():
    """Test that helpful error is raised when pydantic-ai is not installed."""
    with pytest.raises(ImportError, match="pydantic-ai is not installed"):
        await default_registry.call(
            "pydantic_ai_create_vertex_model",
            ["gemini-1.5-flash"]
        )
