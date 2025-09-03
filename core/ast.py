from enum import Enum
from typing import Any, Union, TYPE_CHECKING
from pydantic import BaseModel


class ValueType(Enum):
    LITERAL = "literal"
    VARIABLE = "variable"
    NODE_REF = "node_ref"
    BRANCH_REF = "branch_ref"
    WORKFLOW_CALL = "workflow_call"


class Value(BaseModel):
    type: ValueType
    data: Any


class Statement(BaseModel):
    opcode: str
    inputs: dict[str, Value]
    next: Union["Statement", None] = None


class StatementList(BaseModel):
    statements: list[Statement]


class WorkflowDef(BaseModel):
    name: str
    inputs: list[str]
    outputs: list[str]
    body: StatementList
    variables: dict[str, Any] = {}
    nodes: dict[str, "Node"] = {}


class Program(BaseModel):
    variables: dict[str, Any]
    workflows: dict[str, WorkflowDef] = {}
    main: StatementList
    node_map: dict[str, Any] = None
    branches: dict[str, list[Statement]] = {}
    reporters: dict[str, Statement] = {}


if TYPE_CHECKING:
    pass
else:
    from .models import Node

    WorkflowDef.model_rebuild()
    Program.model_rebuild()

