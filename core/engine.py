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

    # -------------------------
    # Control flow helpers
    # -------------------------
    def jump_to(self, target_id: str | None):
        """Jump execution directly to a node ID, or None (end)."""
        if target_id is None:
            self._state._pc = None
        else:
            self._state._pc = self._state._workflow.nodes.get(target_id)

    def call_substack(self, return_node: RuntimeNode | None, target_id: str):
        """Enter a substack and return to return_node when done."""
        frame = Frame(return_node=return_node, pending_input=None)
        self._state._call_stack.append(frame)
        self.jump_to(target_id)

    def return_from_frame(self, value=None):
        """Return to the parent node after a substack call."""
        frame = self._state.pop_frame()
        if not frame:
            self._state._pc = None
            return

        self._state._pc = frame._return_node
        if value is not None and frame._pending_input:
            # Push result into the pending input of the parent node
            frame._return_node.node.inputs[frame._pending_input] = (
                InputTypes.LITERAL.value,
                value,
            )

    # -------------------------
    # Input evaluation
    # -------------------------
    def _evaluate_inputs(self, node: "RuntimeNode") -> bool:
        """Evaluate all reporter inputs. If a reporter triggers a substack, pause step."""
        inputs = node.node.inputs or {}
        for name, (input_type, value) in list(inputs.items()):
            if input_type == InputTypes.LITERAL.value:
                self._state.push(value)

            elif input_type == InputTypes.VARIABLE_REF.value:
                self._state.push(self._state._variables[value][1])

            elif input_type == InputTypes.NODE_REF.value:
                # Reporter → run node first, then come back
                frame = Frame(return_node=node, pending_input=name)
                self._state._call_stack.append(frame)
                target = self._state._workflow.nodes[value]
                self._state._pc = target
                return False

            elif input_type == InputTypes.BRANCH_REF.value:
                # Branch references are just node IDs
                self._state.push(value)

        return True

    # -------------------------
    # Opcode execution
    # -------------------------
    def execute_opcode(self, node: "RuntimeNode"):
        opcode_cls = self._opcode_registry.get(node.node.opcode)
        opcode = opcode_cls()
        if not opcode.execute(self._state, node, self):
            print(f"Failure to run opcode {node.node.opcode}")

    # -------------------------
    # Step execution
    # -------------------------
    def step(self) -> bool:
        """Execute a single node in the workflow."""
        pc = self._state._pc
        if pc is None:
            return False

        # First resolve reporter inputs
        if not self._evaluate_inputs(pc):
            return True  # Substack called, pause current step

        # Execute the opcode
        self.execute_opcode(pc)

        # If opcode didn’t redirect control flow, move to next
        if pc == self._state._pc:
            if pc.node.next:
                self.jump_to(pc.node.next)
            else:
                # End of flow → return from substack if available
                if self._state._call_stack:
                    result = self._state.pop() if self._state else None
                    self.return_from_frame(result)
                else:
                    self._state._pc = None

        return True
