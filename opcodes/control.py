from core.opcodes import opcode, BaseOpcode


@opcode("control_if_else")
class ControlIfElse(BaseOpcode):
    async def execute(self, state, stmt, engine):
        branch2 = state.pop()
        branch1 = state.pop()
        condition = state.pop()

        if condition:
            branch_stmts = engine._parse_branch_chain(branch1)
            await engine._execute_branch(branch_stmts)
        else:
            branch_stmts = engine._parse_branch_chain(branch2)
            await engine._execute_branch(branch_stmts)

        return True


@opcode("control_while")
class ControlWhile(BaseOpcode):
    async def execute(self, state, stmt, engine):
        substack_id = state.pop()
        condition_result = state.pop()

        if condition_result:
            branch_stmts = engine._parse_branch_chain(substack_id)
            await engine._execute_branch(branch_stmts)

            state._pc -= 1

        return True
