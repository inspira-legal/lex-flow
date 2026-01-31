export interface NodeContextMenuProps {
  x: number
  y: number
  nodeId: string
  hasReporters: boolean
  reportersExpanded: boolean
  isOrphan: boolean
  onExpandReporters: () => void
  onCollapseReporters: () => void
  onDelete: () => void
  onDuplicate: () => void
  onClose: () => void
  // Multi-selection support
  selectedNodeIds?: string[]
  onExtractToWorkflow?: () => void
}
