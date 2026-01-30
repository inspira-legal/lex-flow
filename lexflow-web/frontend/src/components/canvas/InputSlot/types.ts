import type { FormattedValue, OpcodeParameter } from "@/api/types"

export interface InputSlotProps {
  nodeId: string
  inputKey: string
  value: FormattedValue
  paramInfo?: OpcodeParameter
  opcode: string
  allInputs: Record<string, FormattedValue>
  x: number
  y: number
  width: number
}
