import { cva } from "class-variance-authority"

export const panelResizerVariants = cva(
  "absolute bg-transparent transition-colors hover:bg-accent-blue/50 z-10",
  {
    variants: {
      orientation: {
        horizontal: "cursor-col-resize w-1 -right-0.5 top-0 bottom-0",
        vertical: "cursor-row-resize h-1 -top-0.5 left-0 right-0",
      },
      isResizing: {
        true: "bg-accent-blue",
        false: "",
      },
    },
    defaultVariants: {
      orientation: "horizontal",
      isResizing: false,
    },
  }
)
