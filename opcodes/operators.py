from core.opcodes import opcode, BaseOpcode, params


@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"},
)
@opcode("operator_equals")
class OperatorEquals(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._op_equals(params["op1"], params["op2"])
        state.push(result)
        return True

    async def _op_equals(self, op1: int, op2: int) -> bool:
        try:
            return int(op1) == int(op2)
        except (ValueError, TypeError):
            return op1 == op2


@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"},
)
@opcode("operator_add")
class OperatorAdd(BaseOpcode):
    async def execute(self, state, stmt, engine) -> bool:
        params = self.resolve_params(state, stmt)
        result = await self._op_add(params["op1"], params["op2"])
        state.push(result)
        return True

    async def _op_add(self, op1: int, op2: int) -> int:
        return int(op1) + int(op2)


@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"},
)
@opcode("operator_less_than")
class OperatorLessThan(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._op_less_than(params["op1"], params["op2"])
        state.push(result)
        return True

    async def _op_less_than(self, op1: int, op2: int) -> bool:
        return int(op1) < int(op2)


@params(
    op1={"type": int, "description": "First operand"},
    op2={"type": int, "description": "Second operand"},
)
@opcode("operator_greater_than")
class OperatorGreaterThan(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._op_greater_than(params["op1"], params["op2"])
        state.push(result)
        return True

    async def _op_greater_than(self, op1: int, op2: int) -> bool:
        return int(op1) > int(op2)


@params(
    min_val={"type": int, "description": "Minimum value"},
    max_val={"type": int, "description": "Maximum value"},
)
@opcode("math_random")
class MathRandom(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._random_int(params["min_val"], params["max_val"])
        state.push(result)
        return True

    async def _random_int(self, min_val: int, max_val: int) -> int:
        import random

        return random.randint(int(min_val), int(max_val))


@params(format_string={"type": str, "description": "Format template"})
@opcode("str_format")
class StrFormat(BaseOpcode):
    async def execute(self, state, stmt, engine):
        input_count = len(stmt.inputs)
        args = []

        for _ in range(input_count):
            args.append(state.pop())

        args.reverse()
        format_string = args.pop(0)

        result = await self._format_string(format_string, args)
        state.push(result)
        return True

    async def _format_string(self, template: str, args: list) -> str:
        return template.format(*args)


@params(
    str1={"type": str, "description": "First string"},
    str2={"type": str, "description": "Second string"},
)
@opcode("str_concat")
class StrConcat(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._concat_strings(params["str1"], params["str2"])
        state.push(result)
        return True

    async def _concat_strings(self, str1: str, str2: str) -> str:
        return str(str1) + str(str2)
