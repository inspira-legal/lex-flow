import { cva } from "class-variance-authority"

export const headerVariants = cva(
  "flex items-center h-12 pl-5 pr-4 bg-surface-1 border-b border-border-subtle shrink-0"
)

export const logoVariants = cva(
  "text-base font-semibold text-text-primary tracking-tight ml-2"
)

export const dividerVariants = cva(
  "w-px h-6 mx-2 bg-border-subtle"
)

export const sectionVariants = cva(
  "flex items-center gap-1.5"
)
