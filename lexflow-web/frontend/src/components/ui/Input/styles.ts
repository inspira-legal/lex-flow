import { cva } from "class-variance-authority"

export const inputVariants = cva(
  "w-full bg-surface-0 text-text-primary placeholder:text-text-muted border border-border-default transition-colors focus:outline-none focus:ring-2 focus:ring-accent-blue focus:border-accent-blue disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      size: {
        sm: "h-7 px-2 text-xs rounded-sm",
        md: "h-8 px-3 text-sm rounded-md",
        lg: "h-10 px-4 text-sm rounded-md",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
)
