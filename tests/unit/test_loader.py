import pytest
import json
from lexflow.core.errors import JSONParseError, WorkflowValidationError, WorkflowNotFoundError


class TestWorkflowLoader:
    """Essential tests for WorkflowLoader core functionality."""

    def test_load_single_file(self, workflow_loader, temp_workflow_file):
        """Test loading a single workflow file."""
        workflows = workflow_loader.load_files_with_main(temp_workflow_file, [])

        assert len(workflows) == 1
        assert "test_workflow" in workflows
        assert workflows["test_workflow"].name == "test_workflow"

    def test_load_nonexistent_file_raises(self, workflow_loader):
        """Test that loading non-existent file raises JSONParseError."""
        with pytest.raises(JSONParseError) as exc_info:
            workflow_loader.load_files_with_main("nonexistent.json", [])

        assert "File not found" in str(exc_info.value)

    def test_load_invalid_json_raises(self, workflow_loader, tmp_path):
        """Test that loading invalid JSON raises JSONParseError."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('{"invalid": json}')  # Missing quotes

        with pytest.raises(JSONParseError) as exc_info:
            workflow_loader.load_files_with_main(json_file, [])

        assert "Invalid JSON" in str(exc_info.value)

    def test_load_missing_workflows_field_raises(self, workflow_loader, tmp_path):
        """Test that missing 'workflows' field raises JSONParseError."""
        json_file = tmp_path / "no_workflows.json"
        json_file.write_text('{"not_workflows": []}')

        with pytest.raises(JSONParseError) as exc_info:
            workflow_loader.load_files_with_main(json_file, [])

        assert "Missing or invalid 'workflows' field" in str(exc_info.value)

    def test_load_workflow_without_start_raises(self, workflow_loader, tmp_path):
        """Test that workflow without workflow_start raises ValidationError."""
        data = {
            "workflows": [
                {
                    "name": "no_start",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "some_node": {
                            "opcode": "io_print",
                            "inputs": {"STRING": [1, "test"]},
                        }
                    },
                }
            ]
        }

        json_file = tmp_path / "no_start.json"
        json_file.write_text(json.dumps(data))

        with pytest.raises(WorkflowValidationError) as exc_info:
            workflow_loader.load_files_with_main(json_file, [])

        assert "Missing 'workflow_start' node" in str(exc_info.value)

    def test_load_with_import_files(
        self, workflow_loader, tmp_path, sample_workflow_data, math_workflow_data
    ):
        """Test loading main file with import files."""
        main_file = tmp_path / "main.json"
        import_file = tmp_path / "math.json"

        main_file.write_text(json.dumps(sample_workflow_data))
        import_file.write_text(json.dumps(math_workflow_data))

        workflows = workflow_loader.load_files_with_main(main_file, [import_file])

        assert len(workflows) == 2
        assert "test_workflow" in workflows
        assert "math_test" in workflows

        # Check file source tracking
        assert workflow_loader.file_sources["test_workflow"] == str(main_file)
        assert workflow_loader.file_sources["math_test"] == str(import_file)

    def test_get_main_workflow_from_file(self, workflow_loader, temp_workflow_file):
        """Test getting main workflow from specific file."""
        workflows = workflow_loader.load_files_with_main(temp_workflow_file, [])

        # Should return the workflow from main file
        main_workflow = workflow_loader.get_main_workflow_from_file(temp_workflow_file)
        assert main_workflow == "test_workflow"

    def test_workflow_dependency_validation(self, workflow_loader, tmp_path):
        """Test validation of workflow dependencies."""
        # Workflow that calls non-existent workflow
        data = {
            "workflows": [
                {
                    "name": "caller",
                    "interface": {"inputs": [], "outputs": []},
                    "variables": {},
                    "nodes": {
                        "start": {
                            "opcode": "workflow_start",
                            "next": "call",
                            "inputs": {},
                        },
                        "call": {
                            "opcode": "workflow_call",
                            "next": None,
                            "inputs": {"WORKFLOW": [1, "nonexistent_workflow"]},
                        },
                    },
                }
            ]
        }

        main_file = tmp_path / "main.json"
        main_file.write_text(json.dumps(data))

        with pytest.raises(WorkflowNotFoundError) as exc_info:
            workflow_loader.load_files_with_main(main_file, [])

        assert "nonexistent_workflow" in str(exc_info.value)
        assert "caller" in str(exc_info.value)

