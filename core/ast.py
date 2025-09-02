from enum import Enum
from typing import Any, Union
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
    node_data: dict[str, Any] = {}


class Program(BaseModel):
    variables: dict[str, Any]
    workflows: dict[str, WorkflowDef] = {}
    main: StatementList
    node_map: dict[str, Any] = None
    branches: dict[str, list[Statement]] = {}
    reporters: dict[str, Statement] = {}