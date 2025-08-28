from core.opcodes import opcode, BaseOpcode


@opcode("operator_equals")
class OperatorEquals(BaseOpcode):
    async def execute(self, state, stmt, engine):
        op2 = state.pop()
        op1 = state.pop()

        try:
            result = int(op1) == int(op2)
        except (ValueError, TypeError):
            result = op1 == op2
        state.push(result)
        return True


@opcode("operator_add")
class OperatorAdd(BaseOpcode):
    async def execute(self, state, stmt, engine):
        op2 = state.pop()
        op1 = state.pop()

        result = int(op1) + int(op2)
        state.push(result)
        return True


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


@opcode("str_format")
class StrFormat(BaseOpcode):
    async def execute(self, state, stmt, engine):
        format_string = state.pop()

        args = []
        while state:
            args.append(state.pop())

        args.reverse()

        result = format_string.format(*args)
        state.push(result)
        return True


@opcode("str_concat")
class StrConcat(BaseOpcode):
    async def execute(self, state, stmt, engine):
        str2 = state.pop()
        str1 = state.pop()

        result = str(str1) + str(str2)
        state.push(result)
        return True
