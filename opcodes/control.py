from core.opcodes import opcode, BaseOpcode
from core.models import Node, RuntimeNode
from core.state import Frame
from core.state import WorkflowState
from core.models import RuntimeNode, InputTypes


@opcode("control_if_else")
class ControlIfElse(BaseOpcode):
    def execute(self, state, node, engine):
        branch2 = state.pop()
        branch1 = state.pop()
        condition = state.pop()

        if condition:
            engine.call_substack(return_node=node.node.next, target_id=branch1)
        else:
            engine.call_substack(return_node=node.node.next, target_id=branch2)

        return True


@opcode("control_while")
class ControlWhile(BaseOpcode):
    def execute(self, state, node, engine):
        # Get CONDITION and SUBSTACK inputs
        condition_result = state.pop()
        substack_id = state.pop()

        if condition_result:
            engine.call_substack(return_node=node, target_id=substack_id)
        else:
            return True

        return True
