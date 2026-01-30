import { cva } from "class-variance-authority"

export const badgeVariants = cva(
  "inline-flex items-center font-medium",
  {
    variants: {
      variant: {
        default: "bg-surface-3 text-text-secondary",
        blue: "bg-accent-blue/20 text-accent-blue",
        green: "bg-accent-green/20 text-accent-green",
        amber: "bg-accent-amber/20 text-accent-amber",
        red: "bg-accent-red/20 text-accent-red",
        violet: "bg-accent-violet/20 text-accent-violet",
      },
      size: {
        sm: "px-1.5 py-0.5 text-[10px] rounded-sm",
        md: "px-2 py-0.5 text-xs rounded-sm",
        lg: "px-2.5 py-1 text-xs rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)
