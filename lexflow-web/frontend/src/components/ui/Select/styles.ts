import { cva } from "class-variance-authority"

export const selectVariants = cva(
  "w-full bg-surface-2 text-text-secondary border border-border-subtle transition-colors focus:outline-none focus:ring-1 focus:ring-accent-blue focus:border-accent-blue hover:bg-surface-3 hover:text-text-primary disabled:cursor-not-allowed disabled:opacity-50 appearance-none cursor-pointer",
  {
    variants: {
      size: {
        sm: "h-7 px-2.5 pr-7 text-xs rounded-sm leading-7",
        md: "h-8 px-3 pr-8 text-sm rounded-sm leading-8",
        lg: "h-10 px-4 pr-10 text-sm rounded-sm leading-10",
      },
    },
    defaultVariants: {
      size: "md",
    },
  }
)
