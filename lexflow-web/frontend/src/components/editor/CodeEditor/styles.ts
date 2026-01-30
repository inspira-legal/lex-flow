import { cva } from "class-variance-authority"

export const editorContainerVariants = cva(
  "flex flex-col h-full"
)

export const editorHeaderVariants = cva(
  "flex items-center justify-between px-3 py-2 border-b border-border-subtle bg-surface-2"
)

export const editorTitleVariants = cva(
  "text-sm font-medium text-text-secondary"
)

export const editorStatusVariants = cva(
  "text-xs text-accent-blue animate-pulse"
)

export const editorWrapperVariants = cva(
  "flex-1 overflow-hidden"
)
