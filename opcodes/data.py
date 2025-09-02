from core.opcodes import opcode, BaseOpcode, ControlFlow


@opcode("data_set_variable_to")
class DataSetVariableTo(BaseOpcode):
    async def execute(self, state, stmt, engine):
        value = state.pop()
        variable = state.pop()

        if variable not in state._variables:
            raise RuntimeError(f"Variable '{variable}' not found. Available: {list(state._variables.keys())}")

        state._variables[variable][1] = value
        return ControlFlow.CONTINUE


@opcode("data_get_variable")
class DataGetVariable(BaseOpcode):
    async def execute(self, state, stmt, engine):
        variable = state.pop()
        
        if variable not in state._variables:
            raise RuntimeError(f"Variable '{variable}' not found. Available: {list(state._variables.keys())}")
            
        value = state._variables[variable][1]
        state.push(value)
        return ControlFlow.CONTINUE
