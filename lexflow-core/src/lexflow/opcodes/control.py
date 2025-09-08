from ..core.opcodes import opcode, BaseOpcode, ControlFlow, params


@params(
    condition={"type": bool, "description": "Condition to evaluate"},
    true_branch={"type": str, "description": "Branch to execute if condition is true"},
    false_branch={
        "type": str,
        "description": "Branch to execute if condition is false",
    },
)
@opcode("control_if_else")
class ControlIfElse(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        return await self._execute_if_else(
            engine, params["condition"], params["true_branch"], params["false_branch"]
        )

    async def _execute_if_else(
        self, engine, condition: bool, true_branch: str, false_branch: str
    ):
        if condition:
            return await engine._execute_branch_from_node(true_branch)
        else:
            return await engine._execute_branch_from_node(false_branch)


@params(
    condition_result={"type": bool, "description": "Result of the loop condition"},
    loop_body={"type": str, "description": "Branch containing the loop body"},
)
@opcode("control_while")
class ControlWhile(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        return await self._execute_while_loop(
            engine, params["condition_result"], params["loop_body"]
        )

    async def _execute_while_loop(self, engine, condition_result: bool, loop_body: str):
        if condition_result:
            control_result = await engine._execute_branch_from_node(loop_body)

            if control_result == ControlFlow.HALT:
                return ControlFlow.CONTINUE
            else:
                return ControlFlow.REPEAT
        else:
            return ControlFlow.CONTINUE
