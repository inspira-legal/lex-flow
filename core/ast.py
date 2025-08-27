from enum import Enum
from typing import Any, Union
from pydantic import BaseModel


class ValueType(Enum):
    LITERAL = "literal"
    VARIABLE = "variable"
    NODE_REF = "node_ref"
    BRANCH_REF = "branch_ref"


class Value(BaseModel):
    type: ValueType
    data: Any


class Statement(BaseModel):
    opcode: str
    inputs: dict[str, Value]
    next: Union["Statement", None] = None


class StatementList(BaseModel):
    statements: list[Statement]


class Program(BaseModel):
    variables: dict[str, Any]
    main: StatementList
    node_map: dict[str, Any] = None