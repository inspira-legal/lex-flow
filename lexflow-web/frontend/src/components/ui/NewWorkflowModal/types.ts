export interface NewWorkflowModalProps {
  isOpen: boolean
  existingWorkflowNames: string[]
  onConfirm: (data: NewWorkflowData) => void
  onCancel: () => void
}

export interface NewWorkflowData {
  name: string
  inputs: string[]
  outputs: string[]
  variables: Record<string, unknown>
}
