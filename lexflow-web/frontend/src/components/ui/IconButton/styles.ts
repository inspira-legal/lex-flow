import { cva } from "class-variance-authority"

export const iconButtonVariants = cva(
  "inline-flex items-center justify-center transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent-blue disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "text-text-secondary hover:text-text-primary hover:bg-surface-2",
        ghost: "text-text-muted hover:text-text-secondary hover:bg-surface-1",
      },
      size: {
        sm: "h-6 w-6 rounded-sm",
        md: "h-8 w-8 rounded-sm",
        lg: "h-10 w-10 rounded-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)
