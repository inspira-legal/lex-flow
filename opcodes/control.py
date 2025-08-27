from core.opcodes import opcode, BaseOpcode
from core.models import Node, RuntimeNode
from core.state import Frame


@opcode("control_if_else")
class ControlIfElse(BaseOpcode):
    def execute(self, state, node):
        branch1 = state.pop()
        branch2 = state.pop()
        condition = state.pop()

        return_node = state._workflow.nodes.get(node.node.next)

        if condition:
            frame = Frame(return_node=return_node, pending_input="void")
            state._call_stack.append(frame)
            node = Node(next=branch2, opcode="void")
            state._pc = RuntimeNode(id="sub1", node=node)
        else:
            frame = Frame(return_node=return_node, pending_input="void")
            state._call_stack.append(frame)
            node = Node(next=branch1, opcode="void")
            state._pc = RuntimeNode(id="sub2", node=node)

        return True


@opcode("control_while")
class ControlWhile(BaseOpcode):
    def execute(self, state, node) -> bool:
        print(f"Entering while loop execution")
        branch = state.pop()
        condition = state.pop()

        # Convert condition to boolean if it's a string
        if isinstance(condition, str):
            condition_bool = condition.lower() == "true"
        elif isinstance(condition, list) and len(condition) >= 2:
            condition_bool = str(condition[1]).lower() == "true"
        else:
            condition_bool = bool(condition)

        print(f"While condition: {condition}, evaluated as: {condition_bool}")

        if condition_bool:
            # Execute the branch and return to this while loop to re-evaluate condition
            frame = Frame(return_node=node, pending_input="void")
            state._call_stack.append(frame)
            branch_node = Node(next=branch, opcode="void")
            state._pc = RuntimeNode(id="while_branch", node=branch_node)
            print(f"Setting PC to branch, will return to while loop")
        else:
            # Exit the loop - continue to next node
            print(f"Condition false, exiting while loop")
            if node.node.next:
                state._pc = state._workflow.nodes.get(node.node.next)
            else:
                state._pc = None

        return True
