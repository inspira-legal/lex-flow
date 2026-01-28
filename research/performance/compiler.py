"""
Complete JIT compiler for LexFlow workflows.

Compiles workflow AST to Python source code, then exec()s it to create
a callable function. This bypasses the interpreter loop entirely.

Supported constructs:
- All expressions: Literal, Variable, Opcode, Call
- All statements: Assign, Block, If, While, For, ForEach, Fork,
                  Return, ExprStmt, OpStmt, Try/Catch/Finally, Throw

Usage:
    compiler = WorkflowCompiler()
    compiled_fn = compiler.compile(workflow)
    result = await compiled_fn(scope, opcodes, workflows)
"""

from typing import Any, Callable, Optional, Set
from textwrap import indent, dedent

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
    Catch,
    Literal,
    Variable,
    Opcode,
    Call,
    Workflow,
)


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
}

INLINE_LOGICAL_OPS = {
    "operator_and": "and",
    "operator_or": "or",
}

INLINE_UNARY_OPS = {
    "operator_not": "not",
}

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
    """
    Compiles LexFlow workflows to Python functions.

    The compiled function has signature:
        async def compiled(scope: dict, opcodes: OpcodeRegistry, workflows: WorkflowManager) -> Any
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self._reset()

    def _reset(self):
        """Reset compiler state for new compilation."""
        self._async_needed = False
        self._needs_asyncio = False
        self._temp_counter = 0
        self._indent_level = 0

    def _temp_var(self) -> str:
        """Generate a unique temporary variable name."""
        self._temp_counter += 1
        return f"_tmp_{self._temp_counter}"

    def compile(self, workflow: Workflow) -> Callable:
        """
        Compile a workflow to a Python function.

        Returns an async function with signature:
            async def compiled(scope, opcodes, workflows) -> Any
        """
        source = self.compile_to_source(workflow)

        if self.debug:
            print("Generated code:")
            print("-" * 40)
            print(source)
            print("-" * 40)

        # Compile and extract function
        namespace = {"asyncio": __import__("asyncio")}
        try:
            exec(source, namespace)
        except SyntaxError as e:
            raise CompilationError(f"Generated invalid code: {e}\n\nCode:\n{source}")

        return namespace["compiled"]

    def compile_to_source(self, workflow: Workflow) -> str:
        """Compile workflow and return the generated source code."""
        self._reset()

        # Generate function body
        body_code = self._compile_stmt(workflow.body)

        # Build imports if needed
        imports = ""
        if self._needs_asyncio:
            imports = "import asyncio\n\n"

        # Always async for consistent interface
        func_def = "async def compiled(scope, opcodes, workflows):"

        # Add docstring with workflow name
        docstring = f'    """Compiled workflow: {workflow.name}"""'

        return f"{imports}{func_def}\n{docstring}\n{indent(body_code, '    ')}"

    def _compile_stmt(self, stmt: Statement) -> str:
        """Compile a statement to Python code."""
        stmt_type = type(stmt)

        handlers = {
            Block: self._compile_block,
            Assign: self._compile_assign,
            For: self._compile_for,
            ForEach: self._compile_foreach,
            While: self._compile_while,
            If: self._compile_if,
            Return: self._compile_return,
            ExprStmt: self._compile_expr_stmt,
            OpStmt: self._compile_op_stmt,
            Try: self._compile_try,
            Throw: self._compile_throw,
            Fork: self._compile_fork,
        }

        handler = handlers.get(stmt_type)
        if handler:
            return handler(stmt)
        else:
            raise CompilationError(f"Unsupported statement type: {stmt_type.__name__}")

    def _compile_block(self, stmt: Block) -> str:
        """Compile a block of statements."""
        if not stmt.stmts:
            return "pass"
        return "\n".join(self._compile_stmt(s) for s in stmt.stmts)

    def _compile_assign(self, stmt: Assign) -> str:
        """Compile assignment: scope["name"] = value"""
        value_code, is_async = self._compile_expr_with_async(stmt.value)
        if is_async:
            return f'scope["{stmt.name}"] = await {value_code}'
        return f'scope["{stmt.name}"] = {value_code}'

    def _compile_for(self, stmt: For) -> str:
        """Compile for loop to Python for."""
        start_code = self._compile_expr(stmt.start)
        end_code = self._compile_expr(stmt.end)

        if stmt.step:
            step_code = self._compile_expr(stmt.step)
            range_code = f"range(int({start_code}), int({end_code}), int({step_code}))"
        else:
            range_code = f"range(int({start_code}), int({end_code}))"

        body_code = self._compile_stmt(stmt.body)
        var = stmt.var_name

        return f'for {var} in {range_code}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

    def _compile_foreach(self, stmt: ForEach) -> str:
        """Compile foreach loop."""
        iterable_code, is_async = self._compile_expr_with_async(stmt.iterable)
        body_code = self._compile_stmt(stmt.body)
        var = stmt.var_name

        if is_async:
            # Need to await the iterable first
            temp = self._temp_var()
            return f'{temp} = await {iterable_code}\nfor {var} in {temp}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

        return f'for {var} in {iterable_code}:\n    scope["{var}"] = {var}\n{indent(body_code, "    ")}'

    def _compile_while(self, stmt: While) -> str:
        """Compile while loop."""
        cond_code, is_async = self._compile_expr_with_async(stmt.cond)
        body_code = self._compile_stmt(stmt.body)

        if is_async:
            # Async condition needs special handling
            return f"while True:\n    if not (await {cond_code}):\n        break\n{indent(body_code, '    ')}"

        return f"while {cond_code}:\n{indent(body_code, '    ')}"

    def _compile_if(self, stmt: If) -> str:
        """Compile if statement."""
        cond_code, is_async = self._compile_expr_with_async(stmt.cond)
        then_code = self._compile_stmt(stmt.then)

        if is_async:
            cond_code = f"await {cond_code}"

        result = f"if {cond_code}:\n{indent(then_code, '    ')}"

        if stmt.else_:
            else_code = self._compile_stmt(stmt.else_)
            result += f"\nelse:\n{indent(else_code, '    ')}"

        return result

    def _compile_return(self, stmt: Return) -> str:
        """Compile return statement."""
        if not stmt.values:
            return "return None"
        elif len(stmt.values) == 1:
            value_code, is_async = self._compile_expr_with_async(stmt.values[0])
            if is_async:
                return f"return await {value_code}"
            return f"return {value_code}"
        else:
            # Multiple return values - need to handle async for each
            parts = []
            any_async = False
            for v in stmt.values:
                code, is_async = self._compile_expr_with_async(v)
                if is_async:
                    any_async = True
                    parts.append(f"await {code}")
                else:
                    parts.append(code)

            return f"return ({', '.join(parts)})"

    def _compile_expr_stmt(self, stmt: ExprStmt) -> str:
        """Compile expression statement."""
        expr_code, is_async = self._compile_expr_with_async(stmt.expr)
        if is_async:
            return f"await {expr_code}"
        return expr_code

    def _compile_op_stmt(self, stmt: OpStmt) -> str:
        """Compile opcode statement (side-effect only)."""
        code = self._compile_opcode_call(stmt.name, stmt.args)
        self._async_needed = True
        return f"await {code}"

    def _compile_try(self, stmt: Try) -> str:
        """Compile try-catch-finally statement."""
        body_code = self._compile_stmt(stmt.body)

        result = f"try:\n{indent(body_code, '    ')}"

        # Compile catch handlers
        for handler in stmt.handlers:
            exc_type = handler.exception_type or "Exception"
            # Map to Python exception type if known
            py_exc_type = EXCEPTION_TYPES.get(exc_type, "Exception")

            if handler.var_name:
                result += f"\nexcept {py_exc_type} as _exc:\n"
                handler_body = f'scope["{handler.var_name}"] = str(_exc)\n'
                handler_body += self._compile_stmt(handler.body)
            else:
                result += f"\nexcept {py_exc_type}:\n"
                handler_body = self._compile_stmt(handler.body)

            result += indent(handler_body, '    ')

        # Compile finally block
        if stmt.finally_:
            finally_code = self._compile_stmt(stmt.finally_)
            result += f"\nfinally:\n{indent(finally_code, '    ')}"

        return result

    def _compile_throw(self, stmt: Throw) -> str:
        """Compile throw statement."""
        value_code, is_async = self._compile_expr_with_async(stmt.value)
        if is_async:
            return f"raise RuntimeError(str(await {value_code}))"
        return f"raise RuntimeError(str({value_code}))"

    def _compile_fork(self, stmt: Fork) -> str:
        """Compile fork statement using asyncio.gather."""
        if not stmt.branches:
            return "pass"

        self._async_needed = True
        self._needs_asyncio = True

        # Create async functions for each branch
        branch_funcs = []
        for i, branch in enumerate(stmt.branches):
            func_name = f"_fork_branch_{self._temp_counter}_{i}"
            self._temp_counter += 1
            branch_code = self._compile_stmt(branch)
            branch_funcs.append((func_name, branch_code))

        # Build the fork code
        lines = []

        # Define branch functions
        for func_name, branch_code in branch_funcs:
            lines.append(f"async def {func_name}():")
            lines.append(indent(branch_code, "    "))

        # Call asyncio.gather
        func_calls = ", ".join(f"{name}()" for name, _ in branch_funcs)
        lines.append(f"await asyncio.gather({func_calls})")

        return "\n".join(lines)

    def _compile_expr(self, expr: Expression) -> str:
        """Compile an expression to Python code (without async info)."""
        code, _ = self._compile_expr_with_async(expr)
        return code

    def _compile_expr_with_async(self, expr: Expression) -> tuple[str, bool]:
        """
        Compile an expression to Python code.
        Returns (code, is_async) where is_async indicates if the code needs await.
        """
        expr_type = type(expr)

        if expr_type is Literal:
            return repr(expr.value), False

        elif expr_type is Variable:
            return f'scope["{expr.name}"]', False

        elif expr_type is Opcode:
            return self._compile_opcode_expr(expr)

        elif expr_type is Call:
            return self._compile_workflow_call(expr)

        else:
            raise CompilationError(f"Unsupported expression type: {expr_type.__name__}")

    def _compile_opcode_expr(self, expr: Opcode) -> tuple[str, bool]:
        """Compile opcode expression. Returns (code, is_async)."""
        name = expr.name
        args = expr.args

        # Try to inline binary operators
        if name in INLINE_BINARY_OPS and len(args) == 2:
            op = INLINE_BINARY_OPS[name]
            left = self._compile_expr(args[0])
            right = self._compile_expr(args[1])
            return f"({left} {op} {right})", False

        # Try to inline logical operators (short-circuit)
        if name in INLINE_LOGICAL_OPS and len(args) == 2:
            op = INLINE_LOGICAL_OPS[name]
            left = self._compile_expr(args[0])
            right = self._compile_expr(args[1])
            return f"({left} {op} {right})", False

        # Try to inline unary operators
        if name in INLINE_UNARY_OPS and len(args) == 1:
            op = INLINE_UNARY_OPS[name]
            operand = self._compile_expr(args[0])
            return f"({op} {operand})", False

        # Fall back to opcode call (async)
        code = self._compile_opcode_call(name, args)
        self._async_needed = True
        return code, True

    def _compile_opcode_call(self, name: str, args: list) -> str:
        """Compile a call to the opcode registry."""
        args_code = ", ".join(self._compile_expr(a) for a in args)
        return f'opcodes.call("{name}", [{args_code}])'

    def _compile_workflow_call(self, expr: Call) -> tuple[str, bool]:
        """Compile workflow call. Returns (code, is_async)."""
        self._async_needed = True
        args_code = ", ".join(self._compile_expr(a) for a in expr.args)
        return f'workflows.call("{expr.name}", [{args_code}])', True


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
