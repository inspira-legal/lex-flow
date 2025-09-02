from core.opcodes import opcode, BaseOpcode, ControlFlow


@opcode("control_if_else")
class ControlIfElse(BaseOpcode):
    async def execute(self, state, stmt, engine):
        false_branch = state.pop()
        true_branch = state.pop()
        condition = state.pop()

        if condition:
            return await engine._execute_branch_from_node(true_branch)
        else:
            return await engine._execute_branch_from_node(false_branch)


@opcode("control_while")
class ControlWhile(BaseOpcode):
    async def execute(self, state, stmt, engine):
        loop_body = state.pop()
        condition_result = state.pop()

        if condition_result:
            control_result = await engine._execute_branch_from_node(loop_body)
            
            if control_result == ControlFlow.HALT:
                return ControlFlow.CONTINUE
            else:
                return ControlFlow.REPEAT
        else:
            return ControlFlow.CONTINUE
