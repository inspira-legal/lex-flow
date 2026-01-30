import { cva } from "class-variance-authority"

export const layoutVariants = cva(
  "flex flex-col h-full overflow-hidden"
)

export const mainVariants = cva(
  "flex flex-1 overflow-hidden relative"
)

export const editorPanelVariants = cva(
  "relative bg-surface-1 border-r border-border-subtle flex flex-col shrink-0"
)

export const canvasAreaVariants = cva(
  "flex-1 flex flex-col relative overflow-hidden bg-surface-0"
)

export const bottomPanelVariants = cva(
  "bg-surface-1 border-t border-border-subtle shrink-0 overflow-visible"
)

export const nodeEditorPanelVariants = cva(
  "absolute right-0 top-0 bottom-0 w-80 bg-surface-1 border-l border-border-subtle z-[100] shadow-lg transition-transform duration-200",
  {
    variants: {
      isOpen: {
        true: "translate-x-0",
        false: "translate-x-full",
      },
    },
    defaultVariants: {
      isOpen: false,
    },
  }
)

export const paletteOverlayVariants = cva(
  "fixed inset-0 bg-black/50 z-[200] flex justify-start"
)

export const paletteDrawerVariants = cva(
  "w-[300px] h-full bg-surface-1 border-r border-border-subtle animate-slide-in"
)
