import { cva } from "class-variance-authority"

export const panelVariants = cva(
  "flex flex-col h-full bg-surface-1"
)

export const headerVariants = cva(
  "flex items-center justify-between px-4 py-3 border-b border-border-subtle bg-surface-2"
)

export const titleVariants = cva(
  "text-sm font-semibold text-text-primary"
)

export const closeBtnVariants = cva(
  "w-7 h-7 flex items-center justify-center bg-transparent border-none text-text-muted cursor-pointer rounded-sm hover:text-text-primary hover:bg-surface-3"
)

export const contentVariants = cva(
  "flex-1 overflow-y-auto p-4"
)

export const backBtnVariants = cva(
  "flex items-center gap-1.5 px-3 py-2 mb-4 bg-surface-2 border border-border-subtle rounded-sm text-accent-blue text-sm cursor-pointer transition-colors w-full hover:bg-surface-3 hover:border-accent-blue"
)

export const emptyVariants = cva(
  "flex items-center justify-center h-full text-text-muted"
)

export const nodeInfoVariants = cva(
  "flex gap-3 mb-5 p-3 bg-surface-2 rounded-sm"
)

export const colorBarVariants = cva(
  "w-1 rounded-sm shrink-0"
)

export const nodeDetailsVariants = cva(
  "flex-1"
)

export const nodeTypeVariants = cva(
  "text-[0.7rem] uppercase tracking-wide text-text-muted"
)

export const nodeNameVariants = cva(
  "text-base font-semibold text-text-primary my-1"
)

export const nodeIdBtnVariants = cva(
  "text-xs text-text-muted font-mono bg-transparent border-none cursor-pointer px-1 py-0.5 -mx-1 rounded-sm transition-colors hover:bg-border-subtle hover:text-text-primary"
)

export const descriptionVariants = cva(
  "text-sm text-text-secondary leading-relaxed p-3 bg-surface-2 rounded-sm mb-4"
)

export const fieldVariants = cva(
  "mb-3"
)

export const fieldLabelVariants = cva(
  "block text-xs font-medium text-text-secondary mb-1 uppercase tracking-wide"
)

export const inputTypeVariants = cva(
  "text-[0.65rem] text-text-muted ml-1.5 px-1.5 py-0.5 bg-border-subtle rounded-sm"
)

export const inputVariants = cva(
  "w-full px-3 py-2 bg-surface-3 border border-border-subtle rounded-sm text-text-primary text-sm font-mono focus:outline-none focus:border-accent-blue read-only:opacity-70 read-only:cursor-not-allowed"
)

export const inputPreviewVariants = cva(
  "flex gap-2 px-3 py-2 bg-surface-3 border border-border-subtle rounded-sm text-sm",
  {
    variants: {
      editable: {
        true: "cursor-pointer transition-colors hover:border-accent-blue hover:bg-surface-2",
        false: "",
      },
    },
    defaultVariants: {
      editable: false,
    },
  }
)

export const valueTypeVariants = cva(
  "px-1.5 py-0.5 bg-border-subtle rounded-sm text-[0.7rem] text-text-muted font-medium shrink-0"
)

export const valueContentVariants = cva(
  "text-text-primary font-mono overflow-hidden text-ellipsis whitespace-nowrap"
)

export const editHintVariants = cva(
  "text-[0.65rem] text-text-muted ml-auto opacity-0 transition-opacity group-hover:opacity-100"
)

export const editInputVariants = cva(
  "w-full px-3 py-2 bg-surface-3 border-2 border-accent-blue rounded-sm text-text-primary text-sm font-mono focus:outline-none"
)

export const sectionVariants = cva(
  "mt-5"
)

export const sectionTitleVariants = cva(
  "text-xs font-semibold text-text-secondary mb-2.5 uppercase tracking-wide"
)

export const noInputsVariants = cva(
  "text-text-muted italic text-sm"
)

export const branchVariants = cva(
  "flex items-center gap-2 px-3 py-2 bg-surface-2 rounded-sm mb-1.5"
)

export const branchNameVariants = cva(
  "font-medium text-text-primary text-sm"
)

export const branchCountVariants = cva(
  "text-text-muted text-xs flex-1"
)

export const removeBranchBtnVariants = cva(
  "w-5 h-5 flex items-center justify-center bg-transparent border border-accent-red rounded-sm text-accent-red cursor-pointer text-sm font-bold opacity-60 transition-opacity hover:opacity-100 hover:bg-accent-red/10"
)

export const addBranchBtnVariants = cva(
  "w-full px-3 py-2 mt-2 bg-transparent border border-dashed border-border-subtle rounded-sm text-text-secondary text-sm cursor-pointer transition-colors hover:border-accent-blue hover:text-accent-blue hover:bg-accent-blue/5"
)

export const dynamicInputVariants = cva(
  "flex items-center gap-2 px-3 py-2 bg-surface-2 rounded-sm mb-1.5"
)

export const dynamicInputNameVariants = cva(
  "flex-1 font-medium text-text-primary text-sm font-mono"
)

export const paramListVariants = cva(
  "flex flex-wrap gap-1.5"
)

export const paramItemVariants = cva(
  "flex items-center gap-1 px-2 py-1 bg-surface-2 rounded-sm text-xs"
)

export const paramNameVariants = cva(
  "text-text-primary font-medium"
)

export const optionalVariants = cva(
  "text-text-muted"
)

export const paramTypeVariants = cva(
  "text-text-muted text-[0.7rem]"
)

export const actionsVariants = cva(
  "flex gap-2 px-4 py-3 border-t border-border-subtle"
)

export const actionBtnVariants = cva(
  "flex-1 px-4 py-2 bg-surface-2 border border-border-subtle rounded-sm text-text-primary text-sm cursor-pointer transition-colors hover:bg-surface-3 hover:border-accent-blue disabled:opacity-50 disabled:cursor-not-allowed"
)

export const actionBtnDangerVariants = cva(
  "flex-1 px-4 py-2 bg-transparent border border-accent-red rounded-sm text-accent-red text-sm cursor-pointer transition-colors hover:bg-accent-red/10 disabled:opacity-50 disabled:cursor-not-allowed"
)

export const goToDefinitionBtnVariants = cva(
  "w-full px-4 py-2 text-sm bg-transparent border border-accent-violet rounded-sm text-accent-violet cursor-pointer transition-colors hover:bg-accent-violet/10"
)
