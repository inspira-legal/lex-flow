import { cva } from "class-variance-authority"

export const menuVariants = cva(
  "min-w-[160px] py-1 bg-surface-1 border border-border-subtle rounded-md shadow-lg animate-scale-in"
)

export const menuItemVariants = cva(
  "w-full flex items-center gap-2 px-3 py-1.5 text-left text-sm text-text-primary bg-transparent border-none cursor-pointer transition-colors hover:bg-surface-2",
  {
    variants: {
      variant: {
        default: "",
        danger: "text-accent-red hover:bg-accent-red/10",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export const menuDividerVariants = cva(
  "h-px my-1 mx-2 bg-border-subtle"
)

export const menuItemIconVariants = cva(
  "w-4 text-center text-xs text-text-muted"
)

export const menuItemLabelVariants = cva(
  "flex-1"
)

export const menuItemShortcutVariants = cva(
  "text-xs text-text-muted"
)
