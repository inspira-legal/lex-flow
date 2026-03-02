from typing import Any, Optional, Literal as LiteralType, Annotated
from pydantic import BaseModel, Field


# ============ Expressions ============
class Literal(BaseModel):
    """Literal value: 42, "hello", True, None"""

    type: LiteralType["Literal"] = "Literal"
    value: Any


class Variable(BaseModel):
    """Variable reference: x, count, flag"""

    type: LiteralType["Variable"] = "Variable"
    name: str


class Call(BaseModel):
    """Function call: add(x, y)"""

    type: LiteralType["Call"] = "Call"
    name: str
    args: list["Expression"]


class Opcode(BaseModel):
    """Opcode invocation for plugins"""

    type: LiteralType["Opcode"] = "Opcode"
    name: str
    args: list["Expression"]


# Union type for all expressions
Expression = Annotated[Literal | Variable | Call | Opcode, Field(discriminator="type")]


# ============ Statements ============
class Assign(BaseModel):
    """Assignment: x = 5"""

    type: LiteralType["Assign"] = "Assign"
    name: str
    value: Expression
    node_id: Optional[str] = None


class Block(BaseModel):
    """Statement sequence"""

    type: LiteralType["Block"] = "Block"
    stmts: list["Statement"]
    node_id: Optional[str] = None


class If(BaseModel):
    """Conditional: if cond then else"""

    type: LiteralType["If"] = "If"
    cond: Expression
    then: "Statement"
    else_: Optional["Statement"] = None
    node_id: Optional[str] = None


class While(BaseModel):
    """Loop: while cond do body"""

    type: LiteralType["While"] = "While"
    cond: Expression
    body: "Statement"
    node_id: Optional[str] = None


class For(BaseModel):
    """For loop: for var in range(start, end, step)"""

    type: LiteralType["For"] = "For"
    var_name: str
    start: Expression
    end: Expression
    step: Optional[Expression] = None
    body: "Statement"
    node_id: Optional[str] = None


class ForEach(BaseModel):
    """ForEach loop: for var in iterable"""

    type: LiteralType["ForEach"] = "ForEach"
    var_name: str
    iterable: Expression
    body: "Statement"
    node_id: Optional[str] = None


class Fork(BaseModel):
    """Fork: execute branches concurrently"""

    type: LiteralType["Fork"] = "Fork"
    branches: list["Statement"]
    node_id: Optional[str] = None


class Return(BaseModel):
    """Return from function - supports returning multiple values"""

    type: LiteralType["Return"] = "Return"
    values: list[Expression] = []
    node_id: Optional[str] = None


class ExprStmt(BaseModel):
    """Expression as statement (for side effects)"""

    type: LiteralType["ExprStmt"] = "ExprStmt"
    expr: Expression
    node_id: Optional[str] = None


class OpStmt(BaseModel):
    """Opcode as statement"""

    type: LiteralType["OpStmt"] = "OpStmt"
    name: str
    args: list[Expression]
    node_id: Optional[str] = None


class Catch(BaseModel):
    """Catch clause with optional exception type and variable binding."""

    exception_type: Optional[str] = None  # None = catch all
    var_name: Optional[str] = None  # Variable to bind exception message to
    body: "Statement"


class Try(BaseModel):
    """Try-catch-finally statement."""

    type: LiteralType["Try"] = "Try"
    body: "Statement"
    handlers: list[Catch]
    finally_: Optional["Statement"] = None
    node_id: Optional[str] = None


class Throw(BaseModel):
    """Throw an exception."""

    type: LiteralType["Throw"] = "Throw"
    value: Expression
    node_id: Optional[str] = None


class Spawn(BaseModel):
    """Spawn a background task."""

    type: LiteralType["Spawn"] = "Spawn"
    body: "Statement"
    var_name: Optional[str] = None  # Variable to store task handle
    node_id: Optional[str] = None


class AsyncForEach(BaseModel):
    """Async ForEach loop: async for var in async_iterable"""

    type: LiteralType["AsyncForEach"] = "AsyncForEach"
    var_name: str
    iterable: Expression
    body: "Statement"
    node_id: Optional[str] = None


class Timeout(BaseModel):
    """Timeout wrapper for a statement."""

    type: LiteralType["Timeout"] = "Timeout"
    timeout: Expression  # Timeout in seconds
    body: "Statement"
    on_timeout: Optional["Statement"] = None  # Fallback if timeout, else raises
    node_id: Optional[str] = None


class With(BaseModel):
    """Async context manager (with statement)."""

    type: LiteralType["With"] = "With"
    resource: Expression
    var_name: str
    body: "Statement"
    node_id: Optional[str] = None


# Union type for all statements
Statement = Annotated[
    Assign
    | Block
    | If
    | While
    | For
    | ForEach
    | Fork
    | Return
    | ExprStmt
    | OpStmt
    | Try
    | Throw
    | Spawn
    | AsyncForEach
    | Timeout
    | With,
    Field(discriminator="type"),
]


# ============ Top Level ============
class Workflow(BaseModel):
    """Workflow definition"""

    name: str
    params: list[str]
    body: Statement
    locals: dict[str, Any] = {}
    description: Optional[str] = None
    trigger: Optional[dict[str, Any]] = None


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
Spawn.model_rebuild()
AsyncForEach.model_rebuild()
Timeout.model_rebuild()
With.model_rebuild()
