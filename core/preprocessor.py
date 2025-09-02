from typing import Dict, Any, List, Union
from copy import deepcopy


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

        return value

    def _process_nested_input(self, input_dict: Dict[str, Any]) -> List:
        for type_name, data in input_dict.items():
            if type_name in self.INPUT_TYPE_MAP:
                return [self.INPUT_TYPE_MAP[type_name], data]

        return input_dict

