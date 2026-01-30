import { cva } from "class-variance-authority"

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-accent-blue disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-surface-3 text-text-primary hover:bg-surface-4 border border-border-default",
        primary: "bg-accent-blue text-white hover:bg-accent-blue/90",
        ghost: "text-text-secondary hover:bg-surface-2 hover:text-text-primary",
        destructive: "bg-accent-red text-white hover:bg-accent-red/90",
      },
      size: {
        sm: "h-7 px-3 text-xs rounded-sm",
        md: "h-8 px-4 text-sm rounded-sm",
        lg: "h-10 px-5 text-sm rounded-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)
