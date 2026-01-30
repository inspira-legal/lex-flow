import { cva } from "class-variance-authority"

export const panelVariants = cva(
  "flex flex-col relative min-h-[100px] max-h-[600px]"
)

export const resizeHandleVariants = cva(
  "absolute top-0 left-0 right-0 h-1.5 cursor-ns-resize bg-transparent z-10 transition-colors hover:bg-accent-blue/50",
  {
    variants: {
      isResizing: {
        true: "bg-accent-blue",
        false: "",
      },
    },
    defaultVariants: {
      isResizing: false,
    },
  }
)

export const headerVariants = cva(
  "flex items-center justify-between px-3 py-1.5 border-b border-border-subtle bg-surface-1"
)

export const titleGroupVariants = cva(
  "flex items-center gap-2"
)

export const titleVariants = cva(
  "text-sm font-medium text-text-secondary"
)

export const statusDotVariants = cva(
  "w-1.5 h-1.5 rounded-full",
  {
    variants: {
      status: {
        idle: "bg-text-muted",
        running: "bg-accent-green animate-pulse",
        error: "bg-accent-red",
      },
    },
    defaultVariants: {
      status: "idle",
    },
  }
)

export const actionsVariants = cva(
  "flex items-center gap-1"
)

export const separatorVariants = cva(
  "w-px h-5 bg-border-subtle mx-1"
)

export const toggleBtnVariants = cva(
  "h-7 px-2.5 bg-transparent border border-border-subtle rounded-sm text-text-muted text-xs font-medium cursor-pointer transition-colors hover:text-text-primary hover:border-text-muted",
  {
    variants: {
      active: {
        true: "bg-surface-3 text-text-primary border-border-default",
        false: "",
      },
    },
    defaultVariants: {
      active: false,
    },
  }
)

export const runBtnVariants = cva(
  "h-7 px-3 flex items-center gap-1.5 bg-accent-green border-none rounded-sm text-surface-0 font-medium text-xs cursor-pointer transition-all hover:brightness-110 disabled:opacity-60 disabled:cursor-not-allowed"
)

export const cancelBtnVariants = cva(
  "h-7 px-3 flex items-center gap-1.5 bg-accent-red border-none rounded-sm text-surface-0 font-medium text-xs cursor-pointer transition-all hover:brightness-110"
)

export const iconBtnVariants = cva(
  "w-7 h-7 flex items-center justify-center bg-transparent border-none text-text-muted cursor-pointer rounded-sm hover:text-text-primary hover:bg-surface-2"
)

export const closeBtnVariants = cva(
  "w-7 h-7 flex items-center justify-center bg-transparent border-none text-text-muted cursor-pointer rounded-sm hover:text-text-primary hover:bg-surface-2"
)

export const inputsRowVariants = cva(
  "flex items-center gap-3 px-4 py-2 border-b border-border-subtle shrink-0"
)

export const labelVariants = cva(
  "text-xs text-text-muted"
)

export const inputFieldVariants = cva(
  "flex items-center gap-1.5"
)

export const inputFieldLabelVariants = cva(
  "text-xs text-text-secondary"
)

export const inputFieldInputVariants = cva(
  "px-2.5 py-1.5 bg-surface-3 border border-border-subtle rounded-sm text-text-primary text-sm w-30 focus:outline-none focus:border-accent-blue"
)

export const progressContainerVariants = cva(
  "flex items-center gap-2.5 px-4 py-2 border-b border-border-subtle shrink-0"
)

export const progressBarVariants = cva(
  "flex-1 h-1.5 bg-surface-3 rounded-none overflow-hidden"
)

export const progressFillVariants = cva(
  "h-full bg-accent-blue transition-[width] duration-200"
)

export const progressLabelVariants = cva(
  "text-xs text-text-muted whitespace-nowrap"
)

export const panesVariants = cva(
  "flex-1 flex overflow-hidden"
)

export const paneVariants = cva(
  "flex-1 flex flex-col overflow-hidden min-w-[200px]"
)

export const paneHeaderVariants = cva(
  "flex items-center px-4 py-1.5 bg-surface-2 border-b border-border-subtle text-xs font-medium text-text-muted uppercase tracking-wide"
)

export const paneContentVariants = cva(
  "flex-1 p-4 overflow-auto"
)

export const paneResizerVariants = cva(
  "w-px bg-border-subtle cursor-col-resize shrink-0 hover:bg-accent-blue"
)

export const emptyStateVariants = cva(
  "flex-1 flex items-center justify-center text-text-muted text-sm"
)

export const placeholderVariants = cva(
  "text-text-muted text-sm italic"
)

export const outputTextVariants = cva(
  "font-mono text-sm text-text-secondary whitespace-pre-wrap break-words"
)

export const errorVariants = cva(
  "text-accent-red text-sm"
)

export const resultVariants = cva(
  "flex gap-2 mt-2 pt-2 border-t border-border-subtle"
)

export const resultLabelVariants = cva(
  "text-xs text-text-muted"
)

export const resultCodeVariants = cva(
  "font-mono text-sm text-accent-green"
)

export const cursorVariants = cva(
  "text-accent-blue animate-blink"
)

export const alertsContainerVariants = cva(
  "absolute bottom-3 right-3 flex flex-col gap-2 max-w-[300px] z-50"
)

export const alertVariants = cva(
  "flex items-center justify-between gap-3 px-4 py-3 bg-surface-2 border border-border-subtle rounded-sm text-sm text-text-primary shadow-lg animate-slide-in-right",
  {
    variants: {
      variant: {
        info: "border-l-[3px] border-l-accent-blue",
        success: "border-l-[3px] border-l-accent-green",
        warning: "border-l-[3px] border-l-accent-amber",
        error: "border-l-[3px] border-l-accent-red",
      },
    },
    defaultVariants: {
      variant: "info",
    },
  }
)

export const alertDismissVariants = cva(
  "bg-transparent border-none text-text-muted cursor-pointer p-0 text-xs hover:text-text-primary"
)

export const htmlContentVariants = cva(
  "p-3 bg-surface-2 rounded-sm text-sm text-text-primary"
)

export const markdownContentVariants = cva(
  "p-2 text-sm text-text-primary [&_h1]:text-xl [&_h1]:mb-2 [&_h2]:text-lg [&_h2]:mb-1.5 [&_h3]:text-base [&_h3]:mb-1 [&_p]:mb-2 [&_p]:leading-relaxed [&_code]:bg-surface-3 [&_code]:px-1 [&_code]:rounded [&_code]:font-mono [&_code]:text-[0.85em] [&_strong]:text-text-primary"
)

export const tableContainerVariants = cva(
  "overflow-x-auto"
)

export const tableVariants = cva(
  "w-full border-collapse text-sm"
)

export const tableHeaderVariants = cva(
  "px-3 py-2 text-left border-b border-border-subtle bg-surface-2 text-text-secondary font-medium"
)

export const tableCellVariants = cva(
  "px-3 py-2 text-left border-b border-border-subtle text-text-primary"
)

export const imageContainerVariants = cva(
  "max-w-full"
)

export const imageVariants = cva(
  "max-w-full h-auto rounded-sm"
)
