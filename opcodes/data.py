from core.opcodes import opcode, BaseOpcode


@opcode("data_set_variable_to")
class DataSetVariableTo(BaseOpcode):
    def execute(self, state, stmt, engine):
        value = state.pop()
        variable = state.pop()

        state._variables[variable][1] = value
        return True


@opcode("data_get_variable")
class DataGetVariable(BaseOpcode):
    def execute(self, state, stmt, engine):
        variable = state.pop()
        value = state._variables[variable][1]
        state.push(value)
        return True
