from pydantic import BaseModel, Field
from enum import Enum
from typing import Any
import json


# Opcode constants
WORKFLOW_START_OPCODE = "workflow_start"


class InputTypes(Enum):
    LITERAL = 1
    NODE_REF = 2
    VARIABLE_REF = 3
    BRANCH_REF = 4


class Node(BaseModel):
    opcode: str
    next: str | None = None
    parent: str | None = None
    inputs: dict[str, list] | None = None
    fields: dict | None = None
    is_reporter: bool = Field(default=False, alias="isReporter")


class WorkflowInterface(BaseModel):
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class Workflow(BaseModel):
    name: str
    interface: WorkflowInterface = Field(default_factory=WorkflowInterface)
    variables: dict = Field(default_factory=dict)
    nodes: dict[str, Node] = Field(default_factory=dict)
    comments: dict[str, str] = Field(default_factory=dict)

    def get_start_node(self) -> Node | None:
        for node_id, node in self.nodes.items():
            if node.opcode == WORKFLOW_START_OPCODE:
                return node_id, node
        return None, None


class Program(BaseModel):
    workflows: list[Workflow]
    globals: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)

    @classmethod
    def model_validate(cls, data: Any) -> "Program":
        if isinstance(data, dict) and "workflows" in data:
            return super().model_validate(data)
        return super().model_validate(data)


class RuntimeNode(BaseModel):
    id: str
    node: Node

    @classmethod
    def from_node(cls, node_id: str, node: Node):
        return cls(id=node_id, node=node)

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


class RuntimeWorkflow:
    def __init__(self, workflow: Workflow):
        self.nodes = {
            nid: RuntimeNode.from_node(nid, node)
            for nid, node in workflow.nodes.items()
        }
        self.start_node = next(
            (n for n in self.nodes.values() if n.node.opcode == WORKFLOW_START_OPCODE), None
        )

    def __str__(self):
        nodes_json = {nid: rn.dict() for nid, rn in self.nodes.items()}
        return (
            f"Start Node: {self.start_node} \nNodes: {json.dumps(nodes_json, indent=2)}"
        )
