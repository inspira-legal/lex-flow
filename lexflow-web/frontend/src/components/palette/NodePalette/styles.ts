import { cva } from "class-variance-authority"

export const paletteVariants = cva(
  "flex flex-col h-full"
)

export const headerVariants = cva(
  "flex items-center justify-between px-4 py-4 border-b border-border-subtle"
)

export const headerTitleVariants = cva(
  "text-base font-semibold text-text-primary"
)

export const closeBtnVariants = cva(
  "w-7 h-7 flex items-center justify-center bg-transparent border-none text-text-muted cursor-pointer rounded-sm hover:text-text-primary hover:bg-surface-2"
)

export const searchVariants = cva(
  "px-4 py-3 border-b border-border-subtle"
)

export const searchInputVariants = cva(
  "w-full px-3 py-2 bg-surface-3 border border-border-subtle rounded-sm text-text-primary text-sm focus:outline-none focus:border-accent-blue placeholder:text-text-muted"
)

export const contentVariants = cva(
  "flex-1 overflow-y-auto py-2"
)

export const searchResultsVariants = cva(
  "px-4"
)

export const noResultsVariants = cva(
  "text-text-muted text-center py-5 italic"
)

export const categoryVariants = cva(
  "border-b border-border-subtle"
)

export const categoryHeaderVariants = cva(
  "w-full flex items-center gap-2 px-4 py-2.5 bg-transparent border-none cursor-pointer text-left text-text-primary transition-colors hover:bg-surface-2"
)

export const categoryIconVariants = cva(
  "text-base"
)

export const categoryLabelVariants = cva(
  "flex-1 text-sm font-medium"
)

export const categoryCountVariants = cva(
  "text-xs text-text-muted px-1.5 py-0.5 bg-border-subtle rounded-sm"
)

export const expandIconVariants = cva(
  "text-[0.7rem] text-text-muted"
)

export const categoryItemsVariants = cva(
  "py-1 pb-2 bg-surface-2"
)

export const opcodeItemVariants = cva(
  "mx-2"
)

export const opcodeHeaderVariants = cva(
  "w-full flex flex-col items-start gap-0.5 px-3 py-2 bg-surface-1 border border-border-subtle rounded-sm cursor-pointer mb-1 transition-all hover:border-accent-blue hover:translate-x-0.5"
)

export const opcodeNameVariants = cva(
  "text-sm font-medium text-text-primary"
)

export const opcodeRawVariants = cva(
  "text-[0.7rem] text-text-muted font-mono"
)

export const opcodeDetailsVariants = cva(
  "px-3 py-2 -mt-1 mb-1 bg-surface-3 border border-border-subtle border-t-0 rounded-b-sm"
)

export const opcodeDescVariants = cva(
  "text-xs text-text-secondary mb-2 leading-relaxed"
)

export const opcodeParamsVariants = cva(
  "flex flex-wrap gap-1.5 items-center"
)

export const paramsLabelVariants = cva(
  "text-[0.7rem] text-text-muted uppercase tracking-wide"
)

export const paramVariants = cva(
  "text-xs px-1.5 py-0.5 bg-border-subtle rounded-sm text-text-primary font-mono"
)

export const paramTypeVariants = cva(
  "text-text-muted"
)

export const variableItemVariants = cva(
  "flex items-center gap-2 px-3 py-2 mx-2 mb-1 bg-surface-1 border border-border-subtle rounded-sm cursor-grab transition-all hover:border-accent-green hover:translate-x-0.5 active:cursor-grabbing"
)

export const variableNameVariants = cva(
  "text-sm font-semibold text-accent-green font-mono"
)

export const variableValueVariants = cva(
  "text-xs text-text-muted font-mono"
)

export const variableWorkflowVariants = cva(
  "text-[0.7rem] text-text-muted ml-auto"
)

export const emptyVariablesVariants = cva(
  "px-4 py-3 text-xs text-text-muted italic text-center"
)

export const workflowItemVariants = cva(
  "mx-2"
)

export const workflowHeaderVariants = cva(
  "w-full flex items-center gap-2 px-3 py-2 bg-surface-1 border border-border-subtle rounded-sm cursor-grab mb-1 transition-all hover:border-accent-violet hover:translate-x-0.5 active:cursor-grabbing"
)

export const workflowNameVariants = cva(
  "text-sm font-semibold text-accent-violet font-mono"
)

export const workflowParamsVariants = cva(
  "text-xs text-text-muted ml-auto"
)

export const workflowDetailsVariants = cva(
  "px-3 py-2 -mt-1 mb-1 bg-surface-3 border border-border-subtle border-t-0 rounded-b-sm"
)

export const workflowParamListVariants = cva(
  "flex flex-col gap-1 mb-2"
)

export const workflowParamVariants = cva(
  "text-xs px-1.5 py-0.5 bg-border-subtle rounded-sm text-text-primary font-mono"
)

export const workflowNoParamsVariants = cva(
  "text-xs text-text-muted italic mb-2"
)

export const goToDefinitionBtnVariants = cva(
  "w-full px-3 py-1.5 text-xs bg-transparent border border-accent-violet rounded-sm text-accent-violet cursor-pointer transition-colors hover:bg-accent-violet/10"
)

export const footerVariants = cva(
  "px-4 py-3 border-t border-border-subtle"
)

export const hintVariants = cva(
  "text-xs text-text-muted text-center"
)
