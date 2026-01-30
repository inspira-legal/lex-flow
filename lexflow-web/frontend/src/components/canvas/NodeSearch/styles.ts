import { cva } from "class-variance-authority"

export const searchButtonVariants = cva(
  "absolute top-4 left-6 w-9 h-9 flex items-center justify-center bg-surface-1 border border-border-subtle rounded-sm text-text-secondary cursor-pointer z-10 shadow-md transition-colors hover:bg-surface-2 hover:border-border-strong hover:text-text-primary"
)

export const searchBarVariants = cva(
  "absolute top-4 left-6 flex items-center gap-2 px-3 py-2 bg-surface-1 border border-border-subtle rounded-sm z-10 shadow-md text-text-secondary focus-within:border-accent-blue"
)

export const inputVariants = cva(
  "bg-transparent border-none outline-none text-text-primary text-sm w-[180px] placeholder:text-text-muted"
)

export const resultCountVariants = cva(
  "text-xs text-text-muted whitespace-nowrap min-w-[60px] text-center"
)

export const navButtonsVariants = cva("flex gap-0.5")

export const navBtnVariants = cva(
  "w-6 h-6 flex items-center justify-center bg-transparent border-none text-text-secondary cursor-pointer rounded-sm transition-colors hover:bg-surface-2 hover:text-text-primary disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent"
)

export const closeBtnVariants = cva(
  "w-6 h-6 flex items-center justify-center bg-transparent border-none text-text-secondary cursor-pointer rounded-sm ml-1 transition-colors hover:bg-surface-2 hover:text-text-primary"
)
