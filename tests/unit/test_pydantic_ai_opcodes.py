"""Tests for pydantic_ai opcodes."""

import importlib.util
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from lexflow import default_registry

pytestmark = pytest.mark.asyncio


PYDANTIC_AI_AVAILABLE = importlib.util.find_spec("pydantic_ai") is not None

# Try to import helper functions for testing
try:
    from lexflow.opcodes.opcodes_pydantic_ai import (
        _normalize_messages,
        _format_messages_for_prompt,
        _validate_tools_exist,
        _create_tool_wrapper,
        _create_output_model,
        _tool_call_context,
        _is_workflow_tool,
        _get_workflow_name,
        _validate_workflow_tools_exist,
        _create_workflow_wrapper,
    )

    HELPERS_AVAILABLE = True
except ImportError:
    HELPERS_AVAILABLE = False


def inject_workflow_manager(registry, manager):
    """Helper to inject a workflow manager into the registry for testing."""

    async def get_manager():
        return manager

    registry.inject("_get_workflow_manager", get_manager)


def clear_workflow_manager_injection(registry):
    """Helper to clear the workflow manager injection."""
    registry.clear_injection("_get_workflow_manager")


@pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
class TestPydanticAIOpcodes:
    """Tests for pydantic_ai opcodes when pydantic-ai is installed."""

    async def test_create_vertex_model_basic(self):
        """Test creating a Vertex AI model with basic parameters."""
        with (
            patch(
                "lexflow.opcodes.opcodes_pydantic_ai.GoogleProvider"
            ) as mock_provider_class,
            patch(
                "lexflow.opcodes.opcodes_pydantic_ai.GoogleModel"
            ) as mock_model_class,
        ):
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_model = Mock()
            mock_model_class.return_value = mock_model

            result = await default_registry.call(
                "pydantic_ai_create_vertex_model", ["gemini-1.5-flash"]
            )

            mock_provider_class.assert_called_once_with(vertexai=True)
            mock_model_class.assert_called_once_with(
                "gemini-1.5-flash", provider=mock_provider
            )
            assert result == mock_model

    async def test_create_vertex_model_with_project_and_location(self):
        """Test creating a Vertex AI model with project and location."""
        with (
            patch(
                "lexflow.opcodes.opcodes_pydantic_ai.GoogleProvider"
            ) as mock_provider_class,
            patch(
                "lexflow.opcodes.opcodes_pydantic_ai.GoogleModel"
            ) as mock_model_class,
        ):
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider
            mock_model = Mock()
            mock_model_class.return_value = mock_model

            result = await default_registry.call(
                "pydantic_ai_create_vertex_model",
                ["gemini-1.5-pro", "my-project", "asia-east1"],
            )

            mock_provider_class.assert_called_once_with(
                vertexai=True, project="my-project", location="asia-east1"
            )
            mock_model_class.assert_called_once_with(
                "gemini-1.5-pro", provider=mock_provider
            )
            assert result == mock_model

    async def test_create_agent_minimal(self):
        """Test creating an agent with minimal parameters."""
        with patch("lexflow.opcodes.opcodes_pydantic_ai.Agent") as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent", [mock_model]
            )

            mock_agent_class.assert_called_once_with(model=mock_model)
            assert result == mock_agent

    async def test_create_agent_with_instructions(self):
        """Test creating an agent with instructions."""
        with patch("lexflow.opcodes.opcodes_pydantic_ai.Agent") as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent", [mock_model, "Be helpful and concise"]
            )

            mock_agent_class.assert_called_once_with(
                model=mock_model, instructions="Be helpful and concise"
            )
            assert result == mock_agent

    async def test_create_agent_with_instructions_and_system_prompt(self):
        """Test creating an agent with both instructions and system prompt."""
        with patch("lexflow.opcodes.opcodes_pydantic_ai.Agent") as mock_agent_class:
            mock_model = Mock()
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent

            result = await default_registry.call(
                "pydantic_ai_create_agent",
                [mock_model, "Be helpful", "You are an AI assistant"],
            )

            mock_agent_class.assert_called_once_with(
                model=mock_model,
                instructions="Be helpful",
                system_prompt="You are an AI assistant",
            )
            assert result == mock_agent

    async def test_run_sync(self):
        """Test running an agent synchronously."""
        mock_agent = AsyncMock()
        mock_result = Mock()
        mock_result.output = "The answer is 4"
        mock_agent.run.return_value = mock_result

        result = await default_registry.call(
            "pydantic_ai_run_sync", [mock_agent, "What is 2+2?"]
        )

        mock_agent.run.assert_called_once_with("What is 2+2?")
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
            "pydantic_ai_run", [mock_agent, "Explain quantum computing"]
        )

        assert result == "Quantum computing uses quantum mechanics"


@pytest.mark.skipif(
    PYDANTIC_AI_AVAILABLE, reason="Test only when pydantic-ai is not installed"
)
async def test_import_error_when_not_installed():
    """Test that helpful error is raised when pydantic-ai is not installed."""
    with pytest.raises(ImportError, match="pydantic-ai is not installed"):
        await default_registry.call(
            "pydantic_ai_create_vertex_model", ["gemini-1.5-flash"]
        )


@pytest.mark.skipif(not HELPERS_AVAILABLE, reason="pydantic-ai helpers not available")
class TestAiAgentWithToolsHelpers:
    """Tests for ai_agent_with_tools helper functions."""

    def test_normalize_messages_string(self):
        """String input normalizes to user message."""
        result = _normalize_messages("Hello")
        assert result == [{"role": "user", "content": "Hello"}]

    def test_normalize_messages_list(self):
        """List input passes through unchanged."""
        messages = [{"role": "system", "content": "You are helpful"}]
        result = _normalize_messages(messages)
        assert result == messages

    def test_normalize_messages_complex(self):
        """Complex list with multiple messages."""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"},
        ]
        result = _normalize_messages(messages)
        assert result == messages

    def test_format_messages_for_prompt(self):
        """Messages format correctly as prompt string."""
        messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Hi"},
        ]
        result = _format_messages_for_prompt(messages)
        assert "System: Be helpful" in result
        assert "User: Hi" in result

    def test_validate_tools_exist_success(self):
        """Validation passes for existing tools."""
        # Should not raise - these are built-in opcodes
        _validate_tools_exist(["operator_add", "operator_multiply"], default_registry)

    def test_validate_tools_exist_failure(self):
        """Validation fails for non-existent tools."""
        with pytest.raises(ValueError, match="not found"):
            _validate_tools_exist(["nonexistent_tool_xyz"], default_registry)

    def test_create_output_model_none(self):
        """None input returns None."""
        result = _create_output_model(None)
        assert result is None

    @pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
    def test_create_output_model_simple(self):
        """Simple schema creates valid model."""
        schema = {"text": "string"}
        model = _create_output_model(schema)
        assert model is not None
        # Verify model has expected fields
        assert "text" in model.model_fields

    @pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
    def test_create_output_model_with_data(self):
        """Schema with data creates nested model."""
        schema = {"text": "string", "data": {"value": "int", "name": "string"}}
        model = _create_output_model(schema)
        assert model is not None
        assert "text" in model.model_fields
        assert "data" in model.model_fields


@pytest.mark.skipif(not HELPERS_AVAILABLE, reason="pydantic-ai helpers not available")
class TestToolWrapper:
    """Tests for tool wrapper functionality."""

    async def test_tool_wrapper_kwargs_to_args(self):
        """Tool wrapper correctly maps kwargs to positional args."""
        wrapper = _create_tool_wrapper(
            "operator_add", default_registry, {"operator_add"}
        )

        # Setup context
        ctx = {"count": 0, "max": 10, "allowlist": {"operator_add"}}
        token = _tool_call_context.set(ctx)

        try:
            result = await wrapper(left=5, right=3)
            assert result == 8
        finally:
            _tool_call_context.reset(token)

    async def test_tool_wrapper_permission_denied(self):
        """Tool wrapper raises PermissionError when tool not in allowlist."""
        wrapper = _create_tool_wrapper(
            "operator_add",
            default_registry,
            {"operator_add"},  # In wrapper's knowledge
        )

        # Setup context with EMPTY allowlist
        ctx = {"count": 0, "max": 10, "allowlist": set()}  # Not in context allowlist
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(PermissionError, match="not in allowlist"):
                await wrapper(left=5, right=3)
        finally:
            _tool_call_context.reset(token)

    async def test_tool_wrapper_max_calls_exceeded(self):
        """Tool wrapper raises RuntimeError when max_tool_calls exceeded."""
        wrapper = _create_tool_wrapper(
            "operator_add", default_registry, {"operator_add"}
        )

        # Setup context with max=1
        ctx = {"count": 1, "max": 1, "allowlist": {"operator_add"}}
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(RuntimeError, match="Maximum tool calls"):
                await wrapper(left=5, right=3)
        finally:
            _tool_call_context.reset(token)

    async def test_tool_wrapper_missing_required_param(self):
        """Tool wrapper raises ValueError for missing required parameter."""
        wrapper = _create_tool_wrapper(
            "operator_add", default_registry, {"operator_add"}
        )

        ctx = {"count": 0, "max": 10, "allowlist": {"operator_add"}}
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(ValueError, match="Missing required parameter"):
                await wrapper(left=5)  # Missing 'right'
        finally:
            _tool_call_context.reset(token)


@pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
class TestAiAgentWithToolsOpcode:
    """Integration tests for ai_agent_with_tools opcode."""

    async def test_basic_call_structure(self):
        """Test that opcode returns expected structure."""
        # Create mock agent
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = "Test instructions"

        # Mock Agent and Tool at pydantic_ai level (where they're imported from)
        with (
            patch("pydantic_ai.Agent") as MockAgent,
            patch("pydantic_ai.Tool") as MockTool,
        ):
            mock_result = MagicMock()
            mock_result.output = "Test response"

            mock_instance = AsyncMock()
            mock_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_instance
            MockTool.return_value = MagicMock()

            result = await default_registry.call(
                "ai_agent_with_tools", [mock_agent, "Test prompt", ["operator_add"]]
            )

            assert "text" in result
            assert "data" in result
            assert result["text"] == "Test response"

    async def test_timeout_error(self):
        """Test timeout raises TimeoutError."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()

        with (
            patch("pydantic_ai.Agent") as MockAgent,
            patch("pydantic_ai.Tool") as MockTool,
        ):

            async def slow_run(prompt):
                await asyncio.sleep(10)
                return MagicMock(output="done")

            mock_instance = MagicMock()
            mock_instance.run = slow_run
            MockAgent.return_value = mock_instance
            MockTool.return_value = MagicMock()

            with pytest.raises(TimeoutError):
                await default_registry.call(
                    "ai_agent_with_tools",
                    [
                        mock_agent,
                        "Test",
                        ["operator_add"],
                        None,  # output
                        10,  # max_tool_calls
                        0.1,  # timeout_seconds (very short)
                    ],
                )

    async def test_invalid_tools_raises_valueerror(self):
        """Test that non-existent tools raise ValueError."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()

        with pytest.raises(ValueError, match="not found"):
            await default_registry.call(
                "ai_agent_with_tools", [mock_agent, "Test", ["fake_nonexistent_opcode"]]
            )

    async def test_messages_string_normalization(self):
        """Test that string messages are normalized correctly."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = None
        mock_agent._system_prompt = None

        with (
            patch("pydantic_ai.Agent") as MockAgent,
            patch("pydantic_ai.Tool") as MockTool,
        ):
            mock_result = MagicMock()
            mock_result.output = "Response"

            mock_instance = AsyncMock()
            mock_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_instance
            MockTool.return_value = MagicMock()

            await default_registry.call(
                "ai_agent_with_tools", [mock_agent, "Hello world", ["operator_add"]]
            )

            # Check that run was called with formatted message
            mock_instance.run.assert_called_once()
            call_args = mock_instance.run.call_args[0][0]
            assert "User: Hello world" in call_args

    async def test_messages_list_normalization(self):
        """Test that list messages are formatted correctly."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = None
        mock_agent._system_prompt = None

        with (
            patch("pydantic_ai.Agent") as MockAgent,
            patch("pydantic_ai.Tool") as MockTool,
        ):
            mock_result = MagicMock()
            mock_result.output = "Response"

            mock_instance = AsyncMock()
            mock_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_instance
            MockTool.return_value = MagicMock()

            messages = [
                {"role": "system", "content": "Be helpful"},
                {"role": "user", "content": "Hi there"},
            ]

            await default_registry.call(
                "ai_agent_with_tools", [mock_agent, messages, ["operator_add"]]
            )

            # Check that run was called with formatted messages
            mock_instance.run.assert_called_once()
            call_args = mock_instance.run.call_args[0][0]
            assert "System: Be helpful" in call_args
            assert "User: Hi there" in call_args


@pytest.mark.skipif(not HELPERS_AVAILABLE, reason="pydantic-ai helpers not available")
class TestWorkflowToolHelpers:
    """Tests for workflow tool helper functions."""

    def test_is_workflow_tool_string(self):
        """String tool spec is not a workflow tool."""
        assert _is_workflow_tool("operator_add") is False

    def test_is_workflow_tool_dict_with_workflow(self):
        """Dict with workflow key is a workflow tool."""
        assert _is_workflow_tool({"workflow": "my_workflow"}) is True

    def test_is_workflow_tool_dict_without_workflow(self):
        """Dict without workflow key is not a workflow tool."""
        assert _is_workflow_tool({"other": "value"}) is False

    def test_get_workflow_name(self):
        """Extract workflow name from tool spec."""
        result = _get_workflow_name({"workflow": "my_workflow"})
        assert result == "my_workflow"

    def test_validate_workflow_tools_exist_success(self):
        """Validation passes when workflows exist."""
        mock_manager = Mock()
        mock_manager.workflows = {"workflow_a": Mock(), "workflow_b": Mock()}

        # Should not raise
        _validate_workflow_tools_exist(
            [{"workflow": "workflow_a"}, {"workflow": "workflow_b"}],
            mock_manager,
        )

    def test_validate_workflow_tools_exist_failure(self):
        """Validation fails when workflow doesn't exist."""
        mock_manager = Mock()
        mock_manager.workflows = {"workflow_a": Mock()}

        with pytest.raises(ValueError, match="Workflows not found"):
            _validate_workflow_tools_exist(
                [{"workflow": "nonexistent_workflow"}],
                mock_manager,
            )


@pytest.mark.skipif(not HELPERS_AVAILABLE, reason="pydantic-ai helpers not available")
class TestWorkflowWrapper:
    """Tests for workflow wrapper functionality."""

    async def test_workflow_wrapper_basic(self):
        """Workflow wrapper correctly calls manager."""
        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.params = ["x", "y"]
        mock_workflow.locals = {}
        mock_workflow.description = "Test workflow description"

        # Create mock manager
        mock_manager = AsyncMock()
        mock_manager.call = AsyncMock(return_value=42)

        wrapper = _create_workflow_wrapper(
            "test_workflow",
            mock_workflow,
            mock_manager,
            {"test_workflow"},
        )

        # Setup context
        ctx = {"count": 0, "max": 10, "allowlist": {"test_workflow"}}
        token = _tool_call_context.set(ctx)

        try:
            result = await wrapper(x=10, y=20)
            assert result == 42
            mock_manager.call.assert_called_once_with("test_workflow", [10, 20])
        finally:
            _tool_call_context.reset(token)

    async def test_workflow_wrapper_with_defaults(self):
        """Workflow wrapper uses defaults from workflow.locals."""
        mock_workflow = Mock()
        mock_workflow.params = ["x", "y"]
        mock_workflow.locals = {"y": 100}
        mock_workflow.description = None

        mock_manager = AsyncMock()
        mock_manager.call = AsyncMock(return_value=110)

        wrapper = _create_workflow_wrapper(
            "test_workflow",
            mock_workflow,
            mock_manager,
            {"test_workflow"},
        )

        ctx = {"count": 0, "max": 10, "allowlist": {"test_workflow"}}
        token = _tool_call_context.set(ctx)

        try:
            # Only provide x, y should use default
            result = await wrapper(x=10)
            assert result == 110
            mock_manager.call.assert_called_once_with("test_workflow", [10, 100])
        finally:
            _tool_call_context.reset(token)

    async def test_workflow_wrapper_permission_denied(self):
        """Workflow wrapper raises PermissionError when not in allowlist."""
        mock_workflow = Mock()
        mock_workflow.params = ["x"]
        mock_workflow.locals = {}
        mock_workflow.description = None

        mock_manager = AsyncMock()

        wrapper = _create_workflow_wrapper(
            "test_workflow",
            mock_workflow,
            mock_manager,
            {"test_workflow"},
        )

        # Context with empty allowlist
        ctx = {"count": 0, "max": 10, "allowlist": set()}
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(PermissionError, match="not in allowlist"):
                await wrapper(x=10)
        finally:
            _tool_call_context.reset(token)

    async def test_workflow_wrapper_max_calls_exceeded(self):
        """Workflow wrapper raises RuntimeError when max_tool_calls exceeded."""
        mock_workflow = Mock()
        mock_workflow.params = ["x"]
        mock_workflow.locals = {}
        mock_workflow.description = None

        mock_manager = AsyncMock()

        wrapper = _create_workflow_wrapper(
            "test_workflow",
            mock_workflow,
            mock_manager,
            {"test_workflow"},
        )

        ctx = {"count": 1, "max": 1, "allowlist": {"test_workflow"}}
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(RuntimeError, match="Maximum tool calls"):
                await wrapper(x=10)
        finally:
            _tool_call_context.reset(token)

    async def test_workflow_wrapper_missing_required_param(self):
        """Workflow wrapper raises ValueError for missing required parameter."""
        mock_workflow = Mock()
        mock_workflow.params = ["x", "y"]
        mock_workflow.locals = {}  # No defaults
        mock_workflow.description = None

        mock_manager = AsyncMock()

        wrapper = _create_workflow_wrapper(
            "test_workflow",
            mock_workflow,
            mock_manager,
            {"test_workflow"},
        )

        ctx = {"count": 0, "max": 10, "allowlist": {"test_workflow"}}
        token = _tool_call_context.set(ctx)

        try:
            with pytest.raises(ValueError, match="Missing required parameter"):
                await wrapper(x=10)  # Missing 'y'
        finally:
            _tool_call_context.reset(token)

    def test_workflow_wrapper_signature(self):
        """Workflow wrapper has correct signature for PydanticAI."""
        mock_workflow = Mock()
        mock_workflow.params = ["a", "b"]
        mock_workflow.locals = {"b": 42}
        mock_workflow.description = "Custom description"

        mock_manager = Mock()

        wrapper = _create_workflow_wrapper(
            "my_workflow",
            mock_workflow,
            mock_manager,
            {"my_workflow"},
        )

        # Check signature
        import inspect

        sig = inspect.signature(wrapper)
        params = list(sig.parameters.keys())
        assert params == ["a", "b"]
        assert sig.parameters["a"].default is inspect.Parameter.empty
        assert sig.parameters["b"].default == 42

        # Check docstring
        assert wrapper.__doc__ == "Custom description"
        assert wrapper.__name__ == "my_workflow"

    def test_workflow_wrapper_default_description(self):
        """Workflow wrapper uses default description when none provided."""
        mock_workflow = Mock()
        mock_workflow.params = []
        mock_workflow.locals = {}
        mock_workflow.description = None

        mock_manager = Mock()

        wrapper = _create_workflow_wrapper(
            "my_workflow",
            mock_workflow,
            mock_manager,
            {"my_workflow"},
        )

        assert wrapper.__doc__ == "Execute workflow my_workflow"


@pytest.mark.skipif(not PYDANTIC_AI_AVAILABLE, reason="pydantic-ai not installed")
class TestAiAgentWithToolsWorkflows:
    """Tests for ai_agent_with_tools with workflow tools."""

    async def test_backward_compatibility_opcodes_only(self):
        """Tools with only opcode strings still works."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = None
        mock_agent._system_prompt = None

        with (
            patch("pydantic_ai.Agent") as MockAgent,
            patch("pydantic_ai.Tool") as MockTool,
        ):
            mock_result = MagicMock()
            mock_result.output = "Response"

            mock_instance = AsyncMock()
            mock_instance.run = AsyncMock(return_value=mock_result)
            MockAgent.return_value = mock_instance
            MockTool.return_value = MagicMock()

            result = await default_registry.call(
                "ai_agent_with_tools",
                [mock_agent, "Test", ["operator_add", "operator_multiply"]],
            )

            assert result["text"] == "Response"

    async def test_workflow_tools_without_context_raises_error(self):
        """Using workflow tools without WorkflowManager context raises RuntimeError."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()

        # Ensure no injection is set
        clear_workflow_manager_injection(default_registry)

        with pytest.raises(RuntimeError, match="Engine context"):
            await default_registry.call(
                "ai_agent_with_tools",
                [mock_agent, "Test", [{"workflow": "some_workflow"}]],
            )

    async def test_workflow_tools_with_context(self):
        """Workflow tools work correctly with WorkflowManager injection."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = None
        mock_agent._system_prompt = None

        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.params = ["x"]
        mock_workflow.locals = {}
        mock_workflow.description = "Double the input"

        # Create mock manager
        mock_manager = Mock()
        mock_manager.workflows = {"double": mock_workflow}

        # Inject workflow manager
        inject_workflow_manager(default_registry, mock_manager)

        try:
            with (
                patch("pydantic_ai.Agent") as MockAgent,
                patch("pydantic_ai.Tool") as MockTool,
            ):
                mock_result = MagicMock()
                mock_result.output = "Response"

                mock_instance = AsyncMock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                MockAgent.return_value = mock_instance
                MockTool.return_value = MagicMock()

                result = await default_registry.call(
                    "ai_agent_with_tools",
                    [mock_agent, "Test", [{"workflow": "double"}]],
                )

                assert result["text"] == "Response"
                # Verify Tool was called for the workflow
                assert MockTool.call_count == 1
        finally:
            clear_workflow_manager_injection(default_registry)

    async def test_mixed_opcode_and_workflow_tools(self):
        """Mix of opcode and workflow tools works correctly."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()
        mock_agent._instructions = None
        mock_agent._system_prompt = None

        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.params = ["x"]
        mock_workflow.locals = {}
        mock_workflow.description = "Custom workflow"

        mock_manager = Mock()
        mock_manager.workflows = {"custom": mock_workflow}

        inject_workflow_manager(default_registry, mock_manager)

        try:
            with (
                patch("pydantic_ai.Agent") as MockAgent,
                patch("pydantic_ai.Tool") as MockTool,
            ):
                mock_result = MagicMock()
                mock_result.output = "Response"

                mock_instance = AsyncMock()
                mock_instance.run = AsyncMock(return_value=mock_result)
                MockAgent.return_value = mock_instance
                MockTool.return_value = MagicMock()

                result = await default_registry.call(
                    "ai_agent_with_tools",
                    [
                        mock_agent,
                        "Test",
                        ["operator_add", {"workflow": "custom"}, "operator_multiply"],
                    ],
                )

                assert result["text"] == "Response"
                # Verify Tool was called for each tool (2 opcodes + 1 workflow)
                assert MockTool.call_count == 3
        finally:
            clear_workflow_manager_injection(default_registry)

    async def test_invalid_workflow_raises_valueerror(self):
        """Non-existent workflow raises ValueError."""
        mock_agent = MagicMock()
        mock_agent._model = MagicMock()

        mock_manager = Mock()
        mock_manager.workflows = {"existing": Mock()}

        inject_workflow_manager(default_registry, mock_manager)

        try:
            with pytest.raises(ValueError, match="Workflows not found"):
                await default_registry.call(
                    "ai_agent_with_tools",
                    [mock_agent, "Test", [{"workflow": "nonexistent"}]],
                )
        finally:
            clear_workflow_manager_injection(default_registry)
