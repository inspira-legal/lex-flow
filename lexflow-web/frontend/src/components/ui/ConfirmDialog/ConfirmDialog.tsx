import { useEffect, useRef } from "react"
import { createPortal } from "react-dom"
import { cn } from "@/lib/cn"
import {
  overlayVariants,
  dialogVariants,
  headerVariants,
  titleVariants,
  bodyVariants,
  messageVariants,
  footerVariants,
  buttonBaseVariants,
  cancelButtonVariants,
  confirmButtonVariants,
} from "./styles"
import type { ConfirmDialogProps } from "./types"

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "OK",
  cancelLabel = "Cancel",
  variant = "default",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const confirmButtonRef = useRef<HTMLButtonElement>(null)

  // Focus confirm button when dialog opens
  useEffect(() => {
    if (isOpen) {
      // Small delay to ensure the dialog is rendered
      const timer = setTimeout(() => {
        confirmButtonRef.current?.focus()
      }, 50)
      return () => clearTimeout(timer)
    }
  }, [isOpen])

  // Handle escape key
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onCancel()
      } else if (e.key === "Enter") {
        onConfirm()
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onCancel, onConfirm])

  if (!isOpen) return null

  return createPortal(
    <div
      className={cn(overlayVariants())}
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-message"
    >
      <div
        className={cn(dialogVariants())}
        onClick={(e) => e.stopPropagation()}
      >
        <div className={cn(headerVariants())}>
          <h2 id="confirm-dialog-title" className={cn(titleVariants())}>
            {title}
          </h2>
        </div>

        <div className={cn(bodyVariants())}>
          <p id="confirm-dialog-message" className={cn(messageVariants())}>
            {message}
          </p>
        </div>

        <div className={cn(footerVariants())}>
          <button
            className={cn(buttonBaseVariants(), cancelButtonVariants())}
            onClick={onCancel}
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmButtonRef}
            className={cn(buttonBaseVariants(), confirmButtonVariants({ variant }))}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}
