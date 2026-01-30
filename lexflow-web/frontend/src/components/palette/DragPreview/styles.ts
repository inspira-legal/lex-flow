import { cva } from "class-variance-authority"

export const previewVariants = cva(
  "fixed pointer-events-none z-[10000] flex flex-col gap-1"
)

export const cardVariants = cva(
  "flex flex-col gap-0.5 px-4 py-3 bg-surface-1 border-2 border-accent-blue rounded-sm shadow-xl min-w-[120px]",
  {
    variants: {
      type: {
        opcode: "border-accent-blue",
        workflow: "border-[#E91E63]",
      },
    },
    defaultVariants: {
      type: "opcode",
    },
  }
)

export const nameVariants = cva("text-sm font-semibold text-text-primary")

export const opcodeVariants = cva("text-[0.7rem] text-text-muted font-mono")

export const hintVariants = cva("text-[0.7rem] text-accent-blue text-center font-medium")
