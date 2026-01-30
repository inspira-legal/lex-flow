import { cva } from "class-variance-authority"

export const overlayVariants = cva(
  "fixed inset-0 z-[9999] bg-black/60 backdrop-blur-sm flex items-center justify-center animate-in fade-in duration-150"
)

export const dialogVariants = cva(
  "bg-surface-1 border border-border-default rounded-md shadow-2xl w-full max-w-[380px] mx-4 animate-in zoom-in-95 duration-150"
)

export const headerVariants = cva(
  "px-5 py-4 border-b border-border-subtle"
)

export const titleVariants = cva(
  "text-base font-semibold text-text-primary"
)

export const bodyVariants = cva(
  "px-5 py-4"
)

export const messageVariants = cva(
  "text-sm text-text-secondary leading-relaxed"
)

export const footerVariants = cva(
  "px-5 py-3 border-t border-border-subtle flex justify-end gap-2"
)

export const buttonBaseVariants = cva(
  "px-4 py-2 text-sm font-medium rounded-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface-1"
)

export const cancelButtonVariants = cva(
  "bg-surface-3 text-text-primary hover:bg-surface-4 border border-border-default focus:ring-border-default"
)

export const confirmButtonVariants = cva(
  "",
  {
    variants: {
      variant: {
        default: "bg-accent-blue text-white hover:bg-accent-blue/90 focus:ring-accent-blue",
        danger: "bg-accent-red text-white hover:bg-accent-red/90 focus:ring-accent-red",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)
