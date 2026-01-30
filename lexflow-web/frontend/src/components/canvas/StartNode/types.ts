import type { WorkflowInterface } from "@/api/types"

export interface StartNodeProps {
  workflowName: string
  workflowInterface: WorkflowInterface
  variables: Record<string, unknown>
  x: number
  y: number
  zoom?: number
  onDrag?: (dx: number, dy: number) => void
}
