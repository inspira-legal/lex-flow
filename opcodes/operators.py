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


@opcode("operator_less_than")
class OperatorLessThan(BaseOpcode):
    async def execute(self, state, stmt, engine):
        op2 = state.pop()
        op1 = state.pop()

        result = int(op1) < int(op2)
        state.push(result)
        return True


@opcode("operator_greater_than")
class OperatorGreaterThan(BaseOpcode):
    async def execute(self, state, stmt, engine):
        op2 = state.pop()
        op1 = state.pop()

        result = int(op1) > int(op2)
        state.push(result)
        return True


@opcode("math_random")
class MathRandom(BaseOpcode):
    async def execute(self, state, stmt, engine):
        import random

        max_val = state.pop()
        min_val = state.pop()

        result = random.randint(int(min_val), int(max_val))
        state.push(result)
        return True


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


@opcode("str_concat")
class StrConcat(BaseOpcode):
    async def execute(self, state, stmt, engine):
        str2 = state.pop()
        str1 = state.pop()

        result = str(str1) + str(str2)
        state.push(result)
        return True
