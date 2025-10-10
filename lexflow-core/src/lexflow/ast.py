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


class For(BaseModel):
    """For loop: for var in range(start, end, step)"""

    var_name: str
    start: Expression
    end: Expression
    step: Optional[Expression] = None
    body: "Statement"


class ForEach(BaseModel):
    """ForEach loop: for var in iterable"""

    var_name: str
    iterable: Expression
    body: "Statement"


class Fork(BaseModel):
    """Fork: execute branches concurrently"""

    branches: list["Statement"]


class Return(BaseModel):
    """Return from function - supports returning multiple values"""

    values: list[Expression] = []


class ExprStmt(BaseModel):
    """Expression as statement (for side effects)"""

    expr: Expression


class OpStmt(BaseModel):
    """Opcode as statement"""

    name: str
    args: list[Expression]


class Catch(BaseModel):
    """Catch clause with optional exception type and variable binding."""

    exception_type: Optional[str] = None  # None = catch all
    var_name: Optional[str] = None  # Variable to bind exception message to
    body: "Statement"


class Try(BaseModel):
    """Try-catch-finally statement."""

    body: "Statement"
    handlers: list[Catch]
    finally_: Optional["Statement"] = None


class Throw(BaseModel):
    """Throw an exception."""

    value: Expression  # Evaluates to error message/exception


# Union type for all statements
Statement = Assign | Block | If | While | For | ForEach | Fork | Return | ExprStmt | OpStmt | Try | Throw


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
For.model_rebuild()
ForEach.model_rebuild()
Fork.model_rebuild()
Try.model_rebuild()
Catch.model_rebuild()
