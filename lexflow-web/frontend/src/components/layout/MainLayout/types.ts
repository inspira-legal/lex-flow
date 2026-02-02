import type { ReactNode } from "react"
import type { EditorMetadata } from "@/services/metadata"

export interface MainLayoutProps {
  canvas: ReactNode
  editor?: ReactNode
  executionPanel?: ReactNode
  nodeEditor?: ReactNode
  palette?: ReactNode
  className?: string
  // Header props
  onSave?: (source: string, metadata: EditorMetadata) => void | Promise<void>
  showSaveButton?: boolean
  saveButtonLabel?: string
  showExamples?: boolean
}
