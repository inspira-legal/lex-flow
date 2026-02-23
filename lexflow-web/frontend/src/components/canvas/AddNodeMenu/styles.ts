import { cva } from "class-variance-authority"

export const menuVariants = cva(
  "w-[320px] max-h-[480px] bg-surface-1 border border-border-subtle rounded-md shadow-lg flex flex-col animate-scale-in"
)

export const searchContainerVariants = cva(
  "p-2 border-b border-border-subtle"
)

export const searchInputVariants = cva(
  "w-full px-3 py-1.5 text-sm bg-surface-2 border border-border-subtle rounded text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-blue"
)

export const contentVariants = cva(
  "flex-1 overflow-y-auto overflow-x-hidden"
)

export const noResultsVariants = cva(
  "px-4 py-8 text-sm text-text-muted text-center"
)

export const categoryVariants = cva(
  "border-b border-border-subtle last:border-b-0"
)

export const categoryHeaderVariants = cva(
  "w-full flex items-center gap-2 px-3 py-2 text-left bg-surface-1 border-none cursor-pointer transition-colors hover:bg-surface-2 sticky top-0 z-10"
)

export const categoryIconVariants = cva(
  "w-5 h-5 flex items-center justify-center text-xs font-bold rounded transition-colors text-[var(--cat-color)] bg-[var(--cat-color)]/10"
)

export const categoryLabelVariants = cva(
  "flex-1 text-sm font-medium text-text-primary"
)

export const categoryCountVariants = cva(
  "text-xs text-text-muted"
)

export const expandIconVariants = cva(
  "w-4 text-xs text-text-muted transition-transform"
)

export const categoryItemsVariants = cva(
  "bg-surface-0"
)

export const opcodeItemVariants = cva(
  "w-full flex flex-col items-start gap-1 px-4 py-2 text-left bg-transparent border-none cursor-pointer transition-colors hover:bg-surface-2 border-b border-border-subtle last:border-b-0"
)

export const opcodeNameVariants = cva(
  "text-sm font-medium text-text-primary"
)

export const opcodeRawVariants = cva(
  "text-xs font-mono text-text-muted"
)

export const opcodeDescVariants = cva(
  "text-xs text-text-secondary line-clamp-2"
)

export const searchResultItemVariants = cva(
  "w-full flex flex-col items-start gap-1 px-4 py-2.5 text-left bg-transparent border-none cursor-pointer transition-colors hover:bg-surface-2 border-b border-border-subtle last:border-b-0"
)

export const highlightVariants = cva(
  "font-semibold text-accent-blue"
)
