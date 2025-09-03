from typing import Dict, Any, List, Union
from copy import deepcopy
from .errors import WorkflowValidationError


class WorkflowPreprocessor:
    INPUT_TYPE_MAP = {
        "literal": 1,
        "node": 2,
        "variable": 3,
        "branch": 4,
        "workflow_call": 5,
    }

    def preprocess_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        processed = deepcopy(workflow_data)

        if "workflows" in processed:
            for workflow in processed["workflows"]:
                self._process_workflow_nodes(workflow)

        return processed

    def _process_workflow_nodes(self, workflow: Dict[str, Any]) -> None:
        if "nodes" not in workflow:
            return

        for node in workflow["nodes"].values():
            if "inputs" in node and node["inputs"]:
                node["inputs"] = self._process_inputs(node["inputs"])

    def _process_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        processed_inputs = {}

        for key, value in inputs.items():
            processed_inputs[key] = self._normalize_input_value(value)

        return processed_inputs

    def _normalize_input_value(self, value: Union[List, Dict, Any]) -> List:
        if isinstance(value, dict):
            return self._process_nested_input(value)

        if isinstance(value, list) and len(value) == 2:
            type_identifier, data = value
            if (
                isinstance(type_identifier, str)
                and type_identifier in self.INPUT_TYPE_MAP
            ):
                return [self.INPUT_TYPE_MAP[type_identifier], data]
            elif isinstance(type_identifier, str):
                # String identifier but unknown type
                valid_types = ", ".join(f'"{t}"' for t in self.INPUT_TYPE_MAP.keys())
                raise WorkflowValidationError(
                    f'Unknown input type "{type_identifier}". '
                    f"Valid input types are: {valid_types}. "
                    f'Example: ["literal", "value"] or ["variable", "var_name"]',
                    "preprocessor",
                    None
                )
            elif isinstance(type_identifier, int):
                # Numeric type identifier - this is valid (legacy format)
                return value
            else:
                raise WorkflowValidationError(
                    f"Invalid input format: first element must be string or integer, got {type(type_identifier).__name__}. "
                    f'Example: ["literal", "value"] or [1, "value"]',
                    "preprocessor", 
                    None
                )
        
        elif isinstance(value, list):
            # List but not 2 elements
            raise WorkflowValidationError(
                f"Invalid input format: list inputs must have exactly 2 elements [type, value], got {len(value)} elements. "
                f'Example: ["literal", "value"]',
                "preprocessor",
                None
            )

        # Non-dict, non-list values are treated as literals (legacy support)
        return value

    def _process_nested_input(self, input_dict: Dict[str, Any]) -> List:
        for type_name, data in input_dict.items():
            if type_name in self.INPUT_TYPE_MAP:
                return [self.INPUT_TYPE_MAP[type_name], data]

        # If we reach here, no valid input type was found
        valid_types = ", ".join(f'"{t}"' for t in self.INPUT_TYPE_MAP.keys())
        invalid_types = ", ".join(f'"{t}"' for t in input_dict.keys())
        raise WorkflowValidationError(
            f"Unknown input type(s): {invalid_types}. "
            f"Valid input types are: {valid_types}. "
            f"Example: {{'literal': 'value'}} or {{'variable': 'var_name'}}",
            "preprocessor",
            None
        )
