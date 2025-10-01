from typing import Any, Optional
from pydantic import BaseModel


# ============ Expressions ============
class Literal(BaseModel):
    """Literal value: 42, "hello", True, None"""

    value: Any


class Variable(BaseModel):
    """Variable reference: x, count, flag"""

    name: str


class Call(BaseModel):
    """Function call: add(x, y)"""

    name: str
    args: list["Expression"]


class Opcode(BaseModel):
    """Opcode invocation for plugins"""

    name: str
    args: list["Expression"]


# Union type for all expressions
Expression = Literal | Variable | Call | Opcode


# ============ Statements ============
class Assign(BaseModel):
    """Assignment: x = 5"""

    name: str
    value: Expression


class Block(BaseModel):
    """Statement sequence"""

    stmts: list["Statement"]


class If(BaseModel):
    """Conditional: if cond then else"""

    cond: Expression
    then: "Statement"
    else_: Optional["Statement"] = None


class While(BaseModel):
    """Loop: while cond do body"""

    cond: Expression
    body: "Statement"


class Return(BaseModel):
    """Return from function"""

    value: Optional[Expression] = None


class ExprStmt(BaseModel):
    """Expression as statement (for side effects)"""

    expr: Expression


class OpStmt(BaseModel):
    """Opcode as statement"""

    name: str
    args: list[Expression]


# Union type for all statements
Statement = Assign | Block | If | While | Return | ExprStmt | OpStmt


# ============ Top Level ============
class Workflow(BaseModel):
    """Workflow definition"""

    name: str
    params: list[str]
    body: Statement
    locals: dict[str, Any] = {}


class Program(BaseModel):
    """Complete program"""

    globals: dict[str, Any] = {}
    externals: dict[str, Workflow] = {}
    main: Workflow


# Enable forward references
Block.model_rebuild()
If.model_rebuild()
While.model_rebuild()
