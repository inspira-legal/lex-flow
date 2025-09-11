import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from .models import Program, Workflow, WORKFLOW_START_OPCODE
from .errors import JSONParseError, WorkflowValidationError, WorkflowNotFoundError
from .preprocessor import WorkflowPreprocessor


class WorkflowLoader:
    def __init__(self):
        self.all_workflows: Dict[str, Workflow] = {}
        self.file_sources: Dict[str, str] = {}
        self.preprocessor = WorkflowPreprocessor()

    def load_files_with_main(
        self, main_file: Union[str, Path], import_files: List[Union[str, Path]]
    ) -> Dict[str, Workflow]:
        self.all_workflows.clear()
        self.file_sources.clear()

        all_files = [main_file] + list(import_files)
        for file_path in all_files:
            self._load_file(file_path)

        self._validate_dependencies()
        return self.all_workflows

    def get_main_workflow_from_file(
        self, main_file: Union[str, Path], explicit_workflow: Optional[str] = None
    ) -> str:
        main_file = str(main_file)
        main_workflows = [
            name
            for name, _ in self.all_workflows.items()
            if self.file_sources[name] == main_file
        ]

        if not main_workflows:
            raise WorkflowValidationError(
                "No workflows found in main file", "unknown", main_file
            )

        if explicit_workflow:
            if explicit_workflow not in main_workflows:
                raise WorkflowNotFoundError(
                    f"Workflow '{explicit_workflow}' not found in main file {Path(main_file).name}"
                )
            return explicit_workflow

        if "main" in main_workflows:
            return "main"

        if len(main_workflows) == 1:
            return main_workflows[0]

        raise WorkflowValidationError(
            f"Multiple workflows found in main file ({', '.join(main_workflows)}). Please specify workflow with --workflow flag",
            "unknown",
            main_file,
        )

    def _load_file(self, file_path: Union[str, Path]):
        file_path = Path(file_path)

        if not file_path.exists():
            raise JSONParseError("File not found", str(file_path))

        if file_path.suffix not in [".json", ".yaml", ".yml"]:
            raise JSONParseError("Expected .json, .yaml, or .yml file", str(file_path))

        try:
            with open(file_path, "r") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                else:
                    data = json.loads(f.read())
        except json.JSONDecodeError as e:
            raise JSONParseError(
                f"Invalid JSON: {e.msg}", str(file_path), line=e.lineno, column=e.colno
            )
        except yaml.YAMLError as e:
            raise JSONParseError(f"Invalid YAML: {e}", str(file_path))
        except Exception as e:
            raise JSONParseError(f"Failed to read file: {e}", str(file_path))

        data = self.preprocessor.preprocess_workflow(data)
        self._extract_workflows(data, str(file_path))

    def _extract_workflows(self, data: Dict[str, Any], file_path: str):
        if "workflows" not in data or not isinstance(data["workflows"], list):
            raise JSONParseError("Missing or invalid 'workflows' field", file_path)

        try:
            program = Program.model_validate(data)
            for workflow in program.workflows:
                if workflow.name in self.all_workflows:
                    existing_file = self.file_sources[workflow.name]
                    raise WorkflowValidationError(
                        f"Duplicate workflow name '{workflow.name}' (also defined in {Path(existing_file).name})",
                        workflow.name,
                        file_path,
                    )

                if not any(
                    node.opcode == WORKFLOW_START_OPCODE
                    for node in workflow.nodes.values()
                ):
                    raise WorkflowValidationError(
                        "Missing 'workflow_start' node", workflow.name, file_path
                    )

                self.all_workflows[workflow.name] = workflow
                self.file_sources[workflow.name] = file_path

        except Exception as e:
            if isinstance(e, (JSONParseError, WorkflowValidationError)):
                raise
            raise JSONParseError(f"Failed to parse workflow data: {e}", file_path)

    def _validate_dependencies(self):
        for workflow_name, workflow in self.all_workflows.items():
            for node in workflow.nodes.values():
                if (
                    node.opcode == "workflow_call"
                    and node.inputs
                    and "WORKFLOW" in node.inputs
                ):
                    input_type, called_workflow = node.inputs["WORKFLOW"]
                    if input_type == 1 and called_workflow not in self.all_workflows:
                        raise WorkflowNotFoundError(called_workflow, workflow_name)
