import { useEffect, useRef } from "react"
import { cn } from "@/lib/cn"
import {
  menuVariants,
  menuItemVariants,
  menuItemIconVariants,
  menuItemLabelVariants,
  menuDividerVariants,
} from "./styles"
import type { CanvasContextMenuProps } from "./types"

export function CanvasContextMenu({
  x,
  y,
  workflowName,
  onCreateWorkflow,
  onDeleteWorkflow,
  onClose,
}: CanvasContextMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose()
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    document.addEventListener("keydown", handleEscape)

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
      document.removeEventListener("keydown", handleEscape)
    }
  }, [onClose])

  // Adjust position to stay within viewport
  const adjustedX = Math.min(x, window.innerWidth - 220)
  const adjustedY = Math.min(y, window.innerHeight - 120)

  // Can only delete non-main workflows
  const canDelete = workflowName && workflowName !== "main"

  return (
    <div
      ref={menuRef}
      className={cn(menuVariants())}
      style={{
        position: "fixed",
        left: adjustedX,
        top: adjustedY,
        zIndex: 1000,
      }}
      role="menu"
      aria-label="Canvas actions"
    >
      <button
        className={cn(menuItemVariants())}
        onClick={() => {
          onCreateWorkflow()
          onClose()
        }}
        role="menuitem"
      >
        <span className={cn(menuItemIconVariants())}>+</span>
        <span className={cn(menuItemLabelVariants())}>Create New Workflow</span>
      </button>

      {canDelete && onDeleteWorkflow && (
        <>
          <div className={cn(menuDividerVariants())} role="separator" />
          <button
            className={cn(menuItemVariants({ variant: "danger" }))}
            onClick={() => {
              onDeleteWorkflow(workflowName)
              onClose()
            }}
            role="menuitem"
          >
            <span className={cn(menuItemIconVariants())}>✕</span>
            <span className={cn(menuItemLabelVariants())}>Delete "{workflowName}"</span>
          </button>
        </>
      )}
    </div>
  )
}
