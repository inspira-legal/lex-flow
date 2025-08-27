from core.models import Workflow, RuntimeNode, InputTypes
from core.state import WorkflowState, Frame
from core.opcodes import OpcodeRegistry


class Engine:
    _state: WorkflowState
    _opcode_registry: OpcodeRegistry

    def __init__(self, workflow: Workflow):
        self._state = WorkflowState(workflow)
        self._opcode_registry = OpcodeRegistry()

        self._opcode_registry.discover_opcodes("opcodes")

    def _evaluate_inputs(self, node: "RuntimeNode") -> bool:
        inputs = node.node.inputs or {}
        for name, (input_type, value) in list(inputs.items()):
            if input_type == InputTypes.LITERAL.value:
                self._state.push(value)

            elif input_type == InputTypes.VARIABLE_REF.value:
                self._state.push(self._state._variables[value])

            elif input_type == InputTypes.NODE_REF.value:
                frame = Frame(return_node=node, pending_input=name)
                self._state._call_stack.append(frame)

                target = self._state._workflow.nodes[value]
                self._state._pc = target
                return False
            elif input_type == InputTypes.BRANCH_REF.value:
                self._state.push(value)

        return True

    def execute_opcode(self, node: "RuntimeNode"):
        opcode = self._opcode_registry.get(node.node.opcode)

        opcode = opcode()
        if not opcode.execute(self._state, node):
            print("Failure to run opcode")

    def step(self) -> bool:
        pc = self._state._pc
        if pc is None:
            return False

        # print(f"Trying to run {pc}")

        if not self._evaluate_inputs(pc):
            return True

        self.execute_opcode(pc)

        if self._state._pc.node.next:
            self._state._pc = self._state._workflow.nodes.get(self._state._pc.node.next)
        else:
            if self._state._call_stack:
                frame = self._state._call_stack.pop()

                result = None

                if self._state:
                    result = self._state.pop()

                parent = frame._return_node
                if parent and result:
                    parent.node.inputs[frame._pending_input] = (
                        InputTypes.LITERAL.value,
                        result,
                    )

                self._state._pc = parent
            else:
                self._state._pc = None

        return True
