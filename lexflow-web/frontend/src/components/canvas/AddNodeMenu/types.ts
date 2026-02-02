import type { OpcodeInterface } from "@/api/types"

export interface AddNodeMenuProps {
  x: number
  y: number
  opcodes: OpcodeInterface[]
  onSelect: (opcode: OpcodeInterface) => void
  onClose: () => void
}
