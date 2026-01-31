import { cva } from "class-variance-authority"

// Reuse overlay and button styles from ConfirmDialog
export {
  overlayVariants,
  buttonBaseVariants,
  cancelButtonVariants,
  confirmButtonVariants,
} from "../ConfirmDialog/styles"

// Extended dialog for larger form
export const dialogVariants = cva(
  "bg-surface-1 border border-border-default rounded-md shadow-2xl w-full max-w-[480px] mx-4 animate-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col"
)

export const headerVariants = cva(
  "px-5 py-4 border-b border-border-subtle flex-shrink-0"
)

export const titleVariants = cva(
  "text-base font-semibold text-text-primary"
)

export const bodyVariants = cva(
  "px-5 py-4 overflow-y-auto flex-1"
)

export const footerVariants = cva(
  "px-5 py-3 border-t border-border-subtle flex justify-end gap-2 flex-shrink-0"
)

export const formFieldVariants = cva(
  "mb-4 last:mb-0"
)

export const labelVariants = cva(
  "block text-sm font-medium text-text-primary mb-1.5"
)

export const inputVariants = cva(
  "w-full px-3 py-2 text-sm bg-surface-2 border border-border-default rounded-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent"
)

export const errorVariants = cva(
  "text-xs text-accent-red mt-1"
)

export const tagListVariants = cva(
  "flex flex-wrap gap-1.5 mb-2"
)

export const tagVariants = cva(
  "inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-surface-3 text-text-primary rounded-sm border border-border-subtle"
)

export const tagRemoveVariants = cva(
  "ml-0.5 text-text-muted hover:text-text-primary cursor-pointer"
)

export const addRowVariants = cva(
  "flex gap-2"
)

export const addButtonVariants = cva(
  "px-3 py-2 text-sm bg-surface-3 text-text-primary hover:bg-surface-4 border border-border-default rounded-sm transition-colors"
)

export const variableRowVariants = cva(
  "flex items-center gap-2 mb-2"
)

export const smallInputVariants = cva(
  "flex-1 px-2 py-1.5 text-sm bg-surface-2 border border-border-default rounded-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-transparent"
)

export const removeButtonVariants = cva(
  "p-1 text-text-muted hover:text-accent-red transition-colors"
)
