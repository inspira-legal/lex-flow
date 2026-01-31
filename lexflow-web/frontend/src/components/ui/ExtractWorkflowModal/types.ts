export interface ExtractWorkflowModalProps {
  isOpen: boolean
  existingWorkflowNames: string[]
  nodeIds: string[]
  suggestedInputs: string[]
  suggestedOutputs: string[]
  onConfirm: (data: ExtractWorkflowData) => void
  onCancel: () => void
}

export interface ExtractWorkflowData {
  name: string
  inputs: string[]
  outputs: string[]
  variables: Record<string, unknown>
}
