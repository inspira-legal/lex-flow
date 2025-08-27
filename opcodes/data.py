from core.opcodes import opcode, BaseOpcode


@opcode("data_set_variable_to")
class DataSetVariableTo(BaseOpcode):
    def execute(self, state, node, engine):
        variable = state.pop()
        value = state.pop()

        state._variables[variable][1] = value

        return True
