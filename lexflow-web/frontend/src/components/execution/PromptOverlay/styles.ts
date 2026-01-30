import { cva } from "class-variance-authority"

export const overlayVariants = cva(
  "absolute inset-0 flex items-center justify-center bg-black/60 z-[100] backdrop-blur-sm"
)

export const cardVariants = cva(
  "bg-surface-1 border border-border-default rounded-sm p-6 min-w-[300px] max-w-[400px] shadow-xl"
)

export const promptTextVariants = cva(
  "block text-sm text-text-primary mb-4 leading-relaxed"
)

export const inputVariants = cva(
  "w-full px-3 py-2.5 bg-surface-2 border border-border-default rounded-sm text-text-primary text-sm mb-4 transition-colors focus:outline-none focus:border-accent-blue focus:ring-1 focus:ring-accent-blue/20"
)

export const selectVariants = cva(
  "w-full px-3 py-2.5 bg-surface-2 border border-border-default rounded-sm text-text-primary text-sm mb-4 cursor-pointer transition-colors focus:outline-none focus:border-accent-blue"
)

export const actionsVariants = cva("flex gap-3 justify-end")

export const submitBtnVariants = cva(
  "px-5 py-2.5 bg-accent-blue border-none rounded-sm text-surface-0 font-medium text-sm cursor-pointer transition-all hover:brightness-110 focus:outline-none focus:ring-1 focus:ring-accent-blue/30"
)

export const cancelBtnVariants = cva(
  "px-5 py-2.5 bg-transparent border border-border-default rounded-sm text-text-secondary font-medium text-sm cursor-pointer transition-colors hover:bg-surface-2 hover:text-text-primary"
)

export const buttonPromptVariants = cva("flex justify-center")

export const actionButtonVariants = cva(
  "px-8 py-3 bg-accent-blue border-none rounded-sm text-white font-semibold text-base cursor-pointer transition-all shadow-lg hover:brightness-110 hover:-translate-y-px focus:outline-none focus:ring-1 focus:ring-accent-blue/30"
)
