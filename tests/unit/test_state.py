from lexflow.core.state import Frame


class TestWorkflowState:
    """Essential tests for WorkflowState core functionality."""

    def test_stack_operations(self, workflow_state):
        """Test basic stack operations."""
        workflow_state.push("test_value")
        workflow_state.push(42)
        workflow_state.push(True)

        assert workflow_state.pop() is True
        assert workflow_state.pop() == 42
        assert workflow_state.pop() == "test_value"

    def test_peek_operation(self, workflow_state):
        """Test peek operation."""
        workflow_state.push("peek_value")

        # Peek should return value without removing it
        assert workflow_state.peek() == "peek_value"
        assert workflow_state.peek() == "peek_value"  # Still there

        # Pop should still work
        assert workflow_state.pop() == "peek_value"

    def test_variable_operations(self, workflow_state):
        """Test variable storage and retrieval."""
        # Set up some variables
        workflow_state._variables = {
            "1": ["test_var", "test_value"],
            "2": ["number", 42],
            "3": ["flag", True],
        }

        # Test variable access
        assert workflow_state._variables["1"][1] == "test_value"
        assert workflow_state._variables["2"][1] == 42
        assert workflow_state._variables["3"][1] is True

    def test_call_frame_management(self, workflow_state):
        """Test call frame push and pop operations."""
        # Push a new frame
        workflow_state.push_frame(return_pc=10, locals={"test": "value"})

        # Should have a call frame now
        assert len(workflow_state._call_stack) == 1
        frame = workflow_state.peek_frame()
        assert frame._return_pc == 10
        assert frame._locals == {"test": "value"}

        # Pop the frame
        popped_frame = workflow_state.pop_frame()

        # Should be back to original state
        assert len(workflow_state._call_stack) == 0
        assert popped_frame._return_pc == 10

    def test_is_finished(self, workflow_state):
        """Test is_finished() basic behavior."""
        # Add statements to test with
        from lexflow.core.ast import Statement

        statements = [
            Statement(opcode="test1", inputs={}),
            Statement(opcode="test2", inputs={}),
        ]
        workflow_state.program.main.statements = statements

        # At start, not finished
        workflow_state._pc = 0
        assert not workflow_state.is_finished()

        # At end without call stack, finished
        workflow_state._pc = 2
        assert workflow_state.is_finished()

        # With call stack, not finished even at end
        workflow_state.push_frame(return_pc=0)
        assert not workflow_state.is_finished()


class TestFrame:
    """Test Frame creation and basic attributes."""

    def test_frame_creation(self):
        """Test Frame creation and attributes."""
        locals_dict = {"test": "value"}
        frame = Frame(return_pc=5, locals=locals_dict)

        assert frame._return_pc == 5
        assert frame._locals == locals_dict
