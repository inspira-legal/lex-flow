import { cva } from "class-variance-authority"

export const panelVariants = cva("", {
  variants: {
    variant: {
      default: "bg-surface-1 border border-border-subtle",
      elevated: "bg-surface-2 border border-border-default shadow-lg",
      inset: "bg-surface-0 border border-border-subtle",
    },
    padding: {
      none: "",
      sm: "p-2",
      md: "p-4",
      lg: "p-6",
    },
    radius: {
      none: "",
      sm: "rounded-sm",
      md: "rounded-md",
      lg: "rounded-lg",
    },
  },
  defaultVariants: {
    variant: "default",
    padding: "md",
    radius: "md",
  },
})
