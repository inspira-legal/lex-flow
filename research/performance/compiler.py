"""
JIT compiler for LexFlow workflows.

Compiles workflow AST to Python source code, then exec()s it to create
a callable function. This bypasses the interpreter loop entirely.

Usage:
    compiler = WorkflowCompiler()
    compiled_fn = compiler.compile(workflow)
    result = await compiled_fn(scope, opcodes, workflows)
"""

from typing import Callable
from textwrap import indent

from lexflow.ast import (
    Statement,
    Expression,
    Assign,
    Block,
    If,
    While,
    For,
    ForEach,
    Fork,
    Return,
    ExprStmt,
    OpStmt,
    Try,
    Throw,
    Literal,
    Variable,
    Opcode,
    Call,
    Workflow,
)


# Python exception type mapping
EXCEPTION_TYPES = {
    "ValueError": "ValueError",
    "TypeError": "TypeError",
    "KeyError": "KeyError",
    "IndexError": "IndexError",
    "RuntimeError": "RuntimeError",
    "ZeroDivisionError": "ZeroDivisionError",
    "AttributeError": "AttributeError",
    "Exception": "Exception",
}


class CompilationError(Exception):
    """Raised when a workflow cannot be compiled."""

    pass


class WorkflowCompiler:
    """Compiles LexFlow workflows to Python functions."""

    # Opcodes that can be inlined as Python operators
    INLINE_BINARY_OPS = {
        "operator_add": "+",
        "operator_sub": "-",
        "operator_subtract": "-",
        "operator_mul": "*",
        "operator_multiply": "*",
        "operator_div": "/",
        "operator_divide": "/",
        "operator_mod": "%",
        "operator_modulo": "%",
        "operator_less_than": "<",
        "operator_greater_than": ">",
        "operator_equals": "==",
        "operator_not_equals": "!=",
        "operator_less_than_or_equal": "<=",
        "operator_greater_than_or_equal": ">=",
        "operator_less_than_or_equals": "<=",
        "operator_greater_than_or_equals": ">=",
    }

    INLINE_LOGICAL_OPS = {
        "operator_and": "and",
        "operator_or": "or",
    }

    INLINE_UNARY_OPS = {
        "operator_not": "not",
    }

    def __init__(self, debug: bool = False):
        self.debug = debug
        self._reset()

    def _reset(self):
        """Reset compiler state for new compilation."""
        self._needs_asyncio = False
        self._temp_counter = 0
        self._workflow_name = ""

    def _temp_var(self) -> str:
        """Generate a unique temporary variable name."""
        self._temp_counter += 1
        return f"_tmp_{self._temp_counter}"

    def _await_if_async(self, code: str, is_async: bool) -> str:
        """Wrap code with await if needed."""
        return f"await {code}" if is_async else code

    def _compilation_error(self, message: str) -> CompilationError:
        """Create error with workflow context."""
        if self._workflow_name:
            return CompilationError(f"[{self._workflow_name}] {message}")
        return CompilationError(message)

    def compile(self, workflow: Workflow) -> Callable:
        """Compile a workflow to a Python function."""
        source = self.compile_to_source(workflow)

        if self.debug:
            print("Generated code:")
            print("-" * 40)
            print(source)
            print("-" * 40)

        namespace = {"asyncio": __import__("asyncio")}
        try:
            exec(source, namespace)
        except SyntaxError as e:
            raise self._compilation_error(
                f"Generated invalid code: {e}\n\nCode:\n{source}"
            )

        return namespace["compiled"]

    def compile_to_source(self, workflow: Workflow) -> str:
        """Compile workflow and return the generated source code."""
        self._reset()
        self._workflow_name = workflow.name

        try:
            body_code = self._compile_stmt(workflow.body)
        except CompilationError:
            raise
        except Exception as e:
            raise self._compilation_error(f"Unexpected error: {e}")

        imports = "import asyncio\n\n" if self._needs_asyncio else ""
        func_def = "async def compiled(scope, opcodes, workflows):"
        docstring = f'    """Compiled workflow: {workflow.name}"""'

        return f"{imports}{func_def}\n{docstring}\n{indent(body_code, '    ')}"

    def _compile_stmt(self, stmt: Statement) -> str:
        """Compile a statement to Python code using pattern matching."""
        match stmt:
            case Block(stmts=stmts):
                return self._compile_block_stmts(stmts)
            case Assign(name=n, value=v):
                return self._compile_assign(n, v)
            case For(var_name=var, start=s, end=e, step=step, body=b):
                return self._compile_for(var, s, e, step, b)
            case ForEach(var_name=var, iterable=it, body=b):
                return self._compile_foreach(var, it, b)
            case While(cond=c, body=b):
                return self._compile_while(c, b)
            case If(cond=c, then=t, else_=e):
                return self._compile_if(c, t, e)
            case Return(values=vals):
                return self._compile_return(vals)
            case ExprStmt(expr=e):
                return self._compile_expr_stmt(e)
            case OpStmt(name=n, args=args):
                return self._compile_op_stmt(n, args)
            case Try(body=body, handlers=handlers, finally_=finally_):
                return self._compile_try(body, handlers, finally_)
            case Throw(value=v):
                return self._compile_throw(v)
            case Fork(branches=branches):
                return self._compile_fork(branches)
            case _:
                raise self._compilation_error(
                    f"Unsupported statement type: {type(stmt).__name__}"
                )

    def _compile_block_stmts(self, stmts: list) -> str:
        """Compile a block of statements."""
        if not stmts:
            return "pass"
        return "\n".join(self._compile_stmt(s) for s in stmts)

    def _compile_assign(self, name: str, value: Expression) -> str:
        """Compile assignment: scope["name"] = value"""
        value_code, is_async = self._compile_expr_with_async(value)
        return f'scope["{name}"] = {self._await_if_async(value_code, is_async)}'

    def _compile_for(
        self, var: str, start: Expression, end: Expression, step, body: Statement
    ) -> str:
        """Compile for loop."""
        start_code = self._compile_expr(start)
        end_code = self._compile_expr(end)

        if step:
            step_code = self._compile_expr(step)
            range_code = f"range(int({start_code}), int({end_code}), int({step_code}))"
        else:
            range_code = f"range(int({start_code}), int({end_code}))"

        body_code = self._compile_stmt(body)
        return f'for {var} in {range_code}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

    def _compile_foreach(self, var: str, iterable: Expression, body: Statement) -> str:
        """Compile foreach loop."""
        iterable_code, is_async = self._compile_expr_with_async(iterable)
        body_code = self._compile_stmt(body)

        if is_async:
            temp = self._temp_var()
            return f'{temp} = await {iterable_code}\nfor {var} in {temp}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

        return f'for {var} in {iterable_code}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

    def _compile_while(self, cond: Expression, body: Statement) -> str:
        """Compile while loop."""
        cond_code, is_async = self._compile_expr_with_async(cond)
        body_code = self._compile_stmt(body)

        if is_async:
            return f"while True:\n    if not (await {cond_code}):\n        break\n{indent(body_code, '    ')}"

        return f"while {cond_code}:\n{indent(body_code, '    ')}"

    def _compile_if(self, cond: Expression, then: Statement, else_) -> str:
        """Compile if statement."""
        cond_code, is_async = self._compile_expr_with_async(cond)
        then_code = self._compile_stmt(then)

        cond_str = self._await_if_async(cond_code, is_async)
        result = f"if {cond_str}:\n{indent(then_code, '    ')}"

        if else_:
            else_code = self._compile_stmt(else_)
            result += f"\nelse:\n{indent(else_code, '    ')}"

        return result

    def _compile_return(self, values: list) -> str:
        """Compile return statement."""
        if not values:
            return "return None"

        if len(values) == 1:
            value_code, is_async = self._compile_expr_with_async(values[0])
            return f"return {self._await_if_async(value_code, is_async)}"

        # Multiple return values
        parts = []
        for v in values:
            code, is_async = self._compile_expr_with_async(v)
            parts.append(self._await_if_async(code, is_async))
        return f"return ({', '.join(parts)})"

    def _compile_expr_stmt(self, expr: Expression) -> str:
        """Compile expression statement."""
        expr_code, is_async = self._compile_expr_with_async(expr)
        return self._await_if_async(expr_code, is_async)

    def _compile_op_stmt(self, name: str, args: list) -> str:
        """Compile opcode statement (side-effect only)."""
        code = self._compile_opcode_call(name, args)
        return f"await {code}"

    def _compile_try(self, body: Statement, handlers: list, finally_) -> str:
        """Compile try-catch-finally statement."""
        body_code = self._compile_stmt(body)
        result = f"try:\n{indent(body_code, '    ')}"

        for handler in handlers:
            exc_type = handler.exception_type or "Exception"
            py_exc_type = EXCEPTION_TYPES.get(exc_type, "Exception")

            if handler.var_name:
                result += f"\nexcept {py_exc_type} as _exc:\n"
                handler_body = f'scope["{handler.var_name}"] = str(_exc)\n'
                handler_body += self._compile_stmt(handler.body)
            else:
                result += f"\nexcept {py_exc_type}:\n"
                handler_body = self._compile_stmt(handler.body)

            result += indent(handler_body, "    ")

        if finally_:
            finally_code = self._compile_stmt(finally_)
            result += f"\nfinally:\n{indent(finally_code, '    ')}"

        return result

    def _compile_throw(self, value: Expression) -> str:
        """Compile throw statement."""
        value_code, is_async = self._compile_expr_with_async(value)
        return f"raise RuntimeError(str({self._await_if_async(value_code, is_async)}))"

    def _compile_fork(self, branches: list) -> str:
        """Compile fork statement using asyncio.gather."""
        if not branches:
            return "pass"

        self._needs_asyncio = True

        branch_funcs = []
        for i, branch in enumerate(branches):
            func_name = f"_fork_branch_{self._temp_counter}_{i}"
            self._temp_counter += 1
            branch_code = self._compile_stmt(branch)
            branch_funcs.append((func_name, branch_code))

        lines = []
        for func_name, branch_code in branch_funcs:
            lines.append(f"async def {func_name}():")
            lines.append(indent(branch_code, "    "))

        func_calls = ", ".join(f"{name}()" for name, _ in branch_funcs)
        lines.append(f"await asyncio.gather({func_calls})")

        return "\n".join(lines)

    def _compile_expr(self, expr: Expression) -> str:
        """Compile an expression to Python code (without async info)."""
        code, _ = self._compile_expr_with_async(expr)
        return code

    def _compile_expr_with_async(self, expr: Expression) -> tuple[str, bool]:
        """Compile an expression. Returns (code, is_async)."""
        match expr:
            case Literal(value=v):
                return repr(v), False

            case Variable(name=n):
                return f'scope["{n}"]', False

            case Opcode(name=name, args=args):
                return self._compile_opcode_expr(name, args)

            case Call(name=name, args=args):
                return self._compile_workflow_call(name, args)

            case _:
                raise self._compilation_error(
                    f"Unsupported expression type: {type(expr).__name__}"
                )

    def _compile_opcode_expr(self, name: str, args: list) -> tuple[str, bool]:
        """Compile opcode expression. Returns (code, is_async)."""
        # Try to inline binary operators (only if operands are sync)
        if name in self.INLINE_BINARY_OPS and len(args) == 2:
            left_code, left_async = self._compile_expr_with_async(args[0])
            right_code, right_async = self._compile_expr_with_async(args[1])
            if not left_async and not right_async:
                op = self.INLINE_BINARY_OPS[name]
                return f"({left_code} {op} {right_code})", False

        # Try to inline logical operators (only if operands are sync)
        if name in self.INLINE_LOGICAL_OPS and len(args) == 2:
            left_code, left_async = self._compile_expr_with_async(args[0])
            right_code, right_async = self._compile_expr_with_async(args[1])
            if not left_async and not right_async:
                op = self.INLINE_LOGICAL_OPS[name]
                return f"({left_code} {op} {right_code})", False

        # Try to inline unary operators (only if operand is sync)
        if name in self.INLINE_UNARY_OPS and len(args) == 1:
            operand_code, operand_async = self._compile_expr_with_async(args[0])
            if not operand_async:
                op = self.INLINE_UNARY_OPS[name]
                return f"({op} {operand_code})", False

        # Fall back to opcode call (async)
        return self._compile_opcode_call(name, args), True

    def _compile_opcode_call(self, name: str, args: list) -> str:
        """Compile a call to the opcode registry."""
        # Args must be awaited if async before passing to opcode
        args_parts = []
        for a in args:
            code, is_async = self._compile_expr_with_async(a)
            args_parts.append(f"(await {code})" if is_async else code)
        args_code = ", ".join(args_parts)
        return f'opcodes.call("{name}", [{args_code}])'

    def _compile_workflow_call(self, name: str, args: list) -> tuple[str, bool]:
        """Compile workflow call. Returns (code, is_async)."""
        # Args must be awaited if async before passing to workflow
        args_parts = []
        for a in args:
            code, is_async = self._compile_expr_with_async(a)
            args_parts.append(f"(await {code})" if is_async else code)
        args_code = ", ".join(args_parts)
        return f'workflows.call("{name}", [{args_code}])', True


class CompiledEngine:
    """
    Engine that uses JIT compilation for workflow execution.

    Falls back to interpreter for unsupported constructs.
    """

    def __init__(self, debug: bool = False):
        self.compiler = WorkflowCompiler(debug=debug)
        self._cache: dict[str, Callable] = {}

    def compile_workflow(self, workflow: Workflow) -> Callable:
        """Compile a workflow, using cache if available."""
        if workflow.name not in self._cache:
            self._cache[workflow.name] = self.compiler.compile(workflow)
        return self._cache[workflow.name]

    def get_source(self, workflow: Workflow) -> str:
        """Get the generated source code for a workflow."""
        return self.compiler.compile_to_source(workflow)

    def clear_cache(self):
        """Clear the compilation cache."""
        self._cache.clear()
