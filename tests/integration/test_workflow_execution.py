import pytest
import json
from io import StringIO
from contextlib import redirect_stdout

from lexflow.core.loader import WorkflowLoader
from lexflow.core.parser import Parser
from lexflow.core.engine import Engine


class TestWorkflowExecution:
    """Integration tests for full workflow execution pipeline."""

    @pytest.mark.asyncio
    async def test_simple_hello_world_execution(self, integration_path):
        """Test execution of simple hello world workflow."""
        workflow_file = integration_path / "simple_hello.json"

        # Load workflow
        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        # Parse to AST
        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        # Execute with output capture
        engine = Engine(program)
        output = StringIO()

        with redirect_stdout(output):
            step_count = 0
            while not engine._state.is_finished() and step_count < 10:
                await engine.step()
                step_count += 1

        result_output = output.getvalue()
        assert "Hello, World!" in result_output
        assert step_count > 0

    @pytest.mark.asyncio
    async def test_function_call_execution(self, integration_path):
        """Test execution of workflow with function calls."""
        workflow_file = integration_path / "test_functions.json"

        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)
        output = StringIO()

        with redirect_stdout(output):
            step_count = 0
            while not engine._state.is_finished() and step_count < 20:
                await engine.step()
                step_count += 1

        result_output = output.getvalue()
        assert "Function result!" in result_output

    @pytest.mark.asyncio
    async def test_conditional_execution(self, integration_path):
        """Test execution of workflow with conditional logic."""
        workflow_file = integration_path / "test_simple_if_else.json"

        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)
        output = StringIO()

        with redirect_stdout(output):
            step_count = 0
            while not engine._state.is_finished() and step_count < 20:
                await engine.step()
                step_count += 1

        result_output = output.getvalue()
        # Should execute one branch of the conditional
        assert len(result_output.strip()) > 0

    @pytest.mark.asyncio
    async def test_variable_manipulation(self, integration_path):
        """Test execution of workflow with variable operations."""
        workflow_file = integration_path / "test_file_content.json"

        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)

        # Execute workflow
        step_count = 0
        while not engine._state.is_finished() and step_count < 30:
            await engine.step()
            step_count += 1

        # Workflow should complete without errors
        assert engine._state.is_finished()
        assert step_count > 0

    @pytest.mark.asyncio
    async def test_loop_execution(self, integration_path):
        """Test execution of workflow with loops."""
        workflow_file = integration_path / "test_simple_while.json"

        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)
        output = StringIO()

        with redirect_stdout(output):
            step_count = 0
            while (
                not engine._state.is_finished() and step_count < 100
            ):  # Higher limit for loops
                await engine.step()
                step_count += 1

        result_output = output.getvalue()
        # Loop should produce some output
        assert len(result_output.strip()) > 0

    @pytest.mark.asyncio
    async def test_workflow_with_optional_return(self, integration_path):
        """Test execution of workflow with optional return values."""
        workflow_file = integration_path / "test_optional_return.json"

        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)

        step_count = 0
        while not engine._state.is_finished() and step_count < 20:
            await engine.step()
            step_count += 1

        assert engine._state.is_finished()


class TestMultiFileWorkflows:
    """Integration tests for multi-file workflow projects."""

    @pytest.mark.asyncio
    async def test_multi_file_execution(self, tmp_path):
        """Test execution of multi-file workflow project."""
        # Create main workflow file
        main_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {"1": ["result", 0]},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "next": "call_helper",
                            "inputs": {},
                        },
                        "call_helper": {
                            "opcode": "workflow_call",
                            "next": "print_result",
                            "inputs": {"WORKFLOW": [1, "helper"], "VALUE": [1, 42]},
                        },
                        "print_result": {
                            "opcode": "io_print",
                            "next": None,
                            "inputs": {"STRING": [2, "call_helper"]},
                        },
                    },
                }
            ]
        }

        # Create helper workflow file
        helper_data = {
            "workflows": [
                {
                    "name": "helper",
                    "interface": {"inputs": ["value"], "outputs": ["result"]},
                    "variables": {"1": ["value", 0]},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "next": "return_value",
                            "inputs": {},
                        },
                        "return_value": {
                            "opcode": "workflow_return",
                            "next": None,
                            "inputs": {"VALUE": [3, "1"]},
                        },
                    },
                }
            ]
        }

        # Write files
        main_file = tmp_path / "main.json"
        helper_file = tmp_path / "helper.json"

        main_file.write_text(json.dumps(main_data, indent=2))
        helper_file.write_text(json.dumps(helper_data, indent=2))

        # Load and execute
        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(main_file, [helper_file])
        main_workflow_name = loader.get_main_workflow_from_file(main_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        engine = Engine(program)
        output = StringIO()

        with redirect_stdout(output):
            step_count = 0
            while not engine._state.is_finished() and step_count < 20:
                await engine.step()
                step_count += 1

        result_output = output.getvalue()
        assert "42" in result_output  # Should print the returned value


class TestErrorHandling:
    """Integration tests for error handling during execution."""

    @pytest.mark.asyncio
    async def test_missing_workflow_dependency_error(self, tmp_path):
        """Test error handling for missing workflow dependencies."""
        from lexflow.core.errors import WorkflowNotFoundError

        # Create workflow that calls non-existent workflow
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "next": None,
                            "inputs": {},
                        }
                    },
                }
            ]
        }

        workflow_file = tmp_path / "test.json"
        workflow_file.write_text(json.dumps(workflow_data))

        # This should fail at load time due to validation
        loader = WorkflowLoader()

        # Add a workflow call to non-existent workflow
        workflow_data["workflows"][0]["nodes"]["call_missing"] = {
            "opcode": "workflow_call",
            "next": None,
            "inputs": {"WORKFLOW": [1, "missing_workflow"]},
        }
        workflow_data["workflows"][0]["nodes"]["start"]["next"] = "call_missing"

        workflow_file.write_text(json.dumps(workflow_data))

        with pytest.raises(WorkflowNotFoundError):
            loader.load_files_with_main(workflow_file, [])

    @pytest.mark.asyncio
    async def test_invalid_opcode_error(self, tmp_path):
        """Test error handling for invalid opcodes."""
        from lexflow.core.errors import RuntimeError as LexFlowRuntimeError

        # Create workflow with invalid opcode
        workflow_data = {
            "workflows": [
                {
                    "name": "main",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "next": "invalid",
                            "inputs": {},
                        },
                        "invalid": {
                            "opcode": "definitely_invalid_opcode",
                            "next": None,
                            "inputs": {},
                        },
                    },
                }
            ]
        }

        workflow_file = tmp_path / "invalid.json"
        workflow_file.write_text(json.dumps(workflow_data))

        # Load and parse should work
        loader = WorkflowLoader()
        workflows = loader.load_files_with_main(workflow_file, [])
        main_workflow_name = loader.get_main_workflow_from_file(workflow_file)
        main_workflow = workflows[main_workflow_name]

        parser = Parser(main_workflow, list(workflows.values()))
        program = parser.parse()

        # Execution should fail on invalid opcode
        engine = Engine(program)

        # First step (workflow_start) should work
        await engine.step()

        # Second step (invalid opcode) should raise error
        with pytest.raises(LexFlowRuntimeError) as exc_info:
            await engine.step()

        assert "Unknown opcode" in str(exc_info.value)
        assert "definitely_invalid_opcode" in str(exc_info.value)
