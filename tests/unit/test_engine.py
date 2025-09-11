import pytest
from unittest.mock import AsyncMock, Mock
from lexflow.core.engine import Engine
from lexflow.core.state import WorkflowState
from lexflow.core.errors import RuntimeError as LexFlowRuntimeError


class TestEngine:
    """Essential tests for Engine core functionality."""

    def test_engine_initialization(self, simple_ast_program):
        """Test engine initialization."""
        engine = Engine(simple_ast_program)

        assert isinstance(engine._state, WorkflowState)
        assert engine._state.program == simple_ast_program
        assert engine._opcode_registry is not None
        assert engine._current_workflow == "main"

    @pytest.mark.asyncio
    async def test_step_when_finished(self, engine):
        """Test step execution when program is finished."""
        # Set PC beyond available statements
        engine._state._pc = len(engine._state.program.main.statements)

        result = await engine.step()
        assert result is False

    @pytest.mark.asyncio
    async def test_execute_statement_unknown_opcode(self, engine):
        """Test executing statement with unknown opcode raises error."""
        from lexflow.core.ast import Statement

        stmt = Statement(opcode="unknown_opcode", inputs={})

        engine._opcode_registry.has_opcode = Mock(return_value=False)

        with pytest.raises(LexFlowRuntimeError) as exc_info:
            await engine._execute_statement(stmt)

        assert "Unknown opcode 'unknown_opcode'" in str(exc_info.value)
        assert exc_info.value.opcode == "unknown_opcode"

    @pytest.mark.asyncio
    async def test_execute_statement_opcode_failure(self, engine):
        """Test executing statement when opcode returns False."""
        from lexflow.core.ast import Statement

        stmt = Statement(opcode="test_opcode", inputs={})

        # Mock opcode that returns False
        mock_opcode = AsyncMock()
        mock_opcode.execute.return_value = False

        engine._opcode_registry.has_opcode = Mock(return_value=True)
        engine._opcode_registry.get = Mock(return_value=lambda: mock_opcode)

        with pytest.raises(LexFlowRuntimeError) as exc_info:
            await engine._execute_statement(stmt)

        assert "execution failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_statement_exception_handling(self, engine):
        """Test that unexpected exceptions are wrapped in LexFlowRuntimeError."""
        from lexflow.core.ast import Statement

        stmt = Statement(opcode="test_opcode", inputs={})

        # Mock opcode that raises exception
        mock_opcode = AsyncMock()
        mock_opcode.execute.side_effect = ValueError("Test error")

        engine._opcode_registry.has_opcode = Mock(return_value=True)
        engine._opcode_registry.get = Mock(return_value=lambda: mock_opcode)

        with pytest.raises(LexFlowRuntimeError) as exc_info:
            await engine._execute_statement(stmt)

        assert "Unexpected error" in str(exc_info.value)
        assert "Test error" in str(exc_info.value)

    def test_call_stack_context_tracking(self, engine):
        """Test that engine tracks call stack for error context."""
        assert engine._call_stack_trace == []

        # Context should be maintained for error reporting
        engine._current_workflow = "test_workflow"
        engine._current_node_id = "test_node"

        assert engine._current_workflow == "test_workflow"
        assert engine._current_node_id == "test_node"


class TestEngineWorkflowCalls:
    """Test engine workflow call functionality."""

    @pytest.mark.asyncio
    async def test_call_workflow_missing_workflow(self, engine):
        """Test calling non-existent workflow raises error."""
        from lexflow.core.errors import WorkflowNotFoundError

        with pytest.raises(WorkflowNotFoundError) as exc_info:
            await engine._call_workflow("nonexistent_workflow")

        assert "nonexistent_workflow" in str(exc_info.value)
