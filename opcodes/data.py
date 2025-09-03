from core.opcodes import opcode, BaseOpcode, ControlFlow, params


@params(
    variable={"type": str, "description": "Variable name to set"},
    value={"type": "Any", "description": "Value to store in the variable"},
)
@opcode("data_set_variable_to")
class DataSetVariableTo(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._set_variable(state, params["variable"], params["value"])
        return result

    async def _set_variable(self, state, variable: str, value) -> ControlFlow:
        if variable not in state._variables:
            raise RuntimeError(
                f"Variable '{variable}' not found. Available: {list(state._variables.keys())}"
            )

        state._variables[variable][1] = value
        return ControlFlow.CONTINUE


@params(variable={"type": str, "description": "Variable name to get"})
@opcode("data_get_variable")
class DataGetVariable(BaseOpcode):
    async def execute(self, state, stmt, engine):
        params = self.resolve_params(state, stmt)
        result = await self._get_variable(state, params["variable"])
        state.push(result)
        return ControlFlow.CONTINUE

    async def _get_variable(self, state, variable: str):
        if variable not in state._variables:
            raise RuntimeError(
                f"Variable '{variable}' not found. Available: {list(state._variables.keys())}"
            )

        return state._variables[variable][1]
