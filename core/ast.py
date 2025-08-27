from enum import Enum
from typing import Any, Union
from pydantic import BaseModel


class ValueType(Enum):
    LITERAL = "literal"
    VARIABLE = "variable"
    NODE_REF = "node_ref"
    BRANCH_REF = "branch_ref"
    FUNCTION_CALL = "function_call"


class Value(BaseModel):
    type: ValueType
    data: Any


class Statement(BaseModel):
    opcode: str
    inputs: dict[str, Value]
    next: Union["Statement", None] = None


class StatementList(BaseModel):
    statements: list[Statement]


class FunctionDef(BaseModel):
    name: str
    inputs: list[str]
    outputs: list[str]
    body: StatementList
    variables: dict[str, Any] = {}


class Program(BaseModel):
    variables: dict[str, Any]
    functions: dict[str, FunctionDef] = {}
    main: StatementList
    node_map: dict[str, Any] = None