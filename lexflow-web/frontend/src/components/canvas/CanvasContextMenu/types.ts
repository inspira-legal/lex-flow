export interface CanvasContextMenuProps {
  x: number
  y: number
  workflowName?: string // If set, we're right-clicking on a workflow group
  onCreateWorkflow: () => void
  onDeleteWorkflow?: (name: string) => void
  onClose: () => void
}
