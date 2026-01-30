import { cva } from "class-variance-authority"

export const canvasContainerVariants = cva("flex-1 relative overflow-hidden")

export const svgVariants = cva("w-full h-full block")

export const canvasToolbarVariants = cva(
  "absolute bottom-4 right-4 flex items-center gap-1 bg-surface-1 p-1 rounded-sm border border-border-subtle z-10 shadow-md"
)

export const toolbarButtonVariants = cva(
  "w-7 h-7 flex items-center justify-center bg-transparent border-none text-text-secondary cursor-pointer rounded-sm hover:bg-surface-2 hover:text-text-primary"
)

export const toolbarDividerVariants = cva(
  "w-px h-5 bg-border-subtle mx-1"
)

export const zoomLevelVariants = cva("min-w-10 text-center text-xs text-text-muted")

export const layoutButtonVariants = cva(
  "h-7 px-2.5 flex items-center justify-center gap-1.5 bg-transparent border-none text-text-secondary cursor-pointer rounded-sm text-xs font-medium transition-colors hover:bg-surface-2 hover:text-text-primary",
  {
    variants: {
      active: {
        true: "bg-surface-3 text-text-primary",
        false: "",
      },
    },
    defaultVariants: {
      active: false,
    },
  }
)

export const errorOverlayVariants = cva(
  "absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-3 px-5 py-3 bg-accent-red/15 border border-accent-red rounded-sm text-accent-red z-10 max-w-[80%]"
)

export const errorIconVariants = cva("text-lg")

export const emptyStateVariants = cva(
  "absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center text-text-muted pointer-events-none"
)

export const emptyStateTitleVariants = cva("text-lg mb-2 text-text-secondary")

export const emptyStateTextVariants = cva("text-sm")
