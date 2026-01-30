import { useEffect, useRef } from "react"
import { cn } from "@/lib/cn"
import {
  menuVariants,
  menuItemVariants,
  menuDividerVariants,
  menuItemIconVariants,
  menuItemLabelVariants,
  menuItemShortcutVariants,
} from "./styles"
import type { NodeContextMenuProps } from "./types"

export function NodeContextMenu({
  x,
  y,
  nodeId: _nodeId,
  hasReporters,
  reportersExpanded,
  isOrphan: _isOrphan,
  onExpandReporters,
  onCollapseReporters,
  onDelete,
  onDuplicate,
  onClose,
}: NodeContextMenuProps) {
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
  const adjustedX = Math.min(x, window.innerWidth - 180)
  const adjustedY = Math.min(y, window.innerHeight - 200)

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
      aria-label="Node actions"
    >
      {hasReporters && (
        <>
          {reportersExpanded ? (
            <button
              className={cn(menuItemVariants())}
              onClick={() => {
                onCollapseReporters()
                onClose()
              }}
              role="menuitem"
            >
              <span className={cn(menuItemIconVariants())}>▲</span>
              <span className={cn(menuItemLabelVariants())}>Collapse Reporters</span>
            </button>
          ) : (
            <button
              className={cn(menuItemVariants())}
              onClick={() => {
                onExpandReporters()
                onClose()
              }}
              role="menuitem"
            >
              <span className={cn(menuItemIconVariants())}>▼</span>
              <span className={cn(menuItemLabelVariants())}>Expand Reporters</span>
            </button>
          )}
          <div className={cn(menuDividerVariants())} role="separator" />
        </>
      )}

      <button
        className={cn(menuItemVariants())}
        onClick={() => {
          onDuplicate()
          onClose()
        }}
        role="menuitem"
      >
        <span className={cn(menuItemIconVariants())}>⧉</span>
        <span className={cn(menuItemLabelVariants())}>Duplicate</span>
        <span className={cn(menuItemShortcutVariants())}>Ctrl+D</span>
      </button>

      <div className={cn(menuDividerVariants())} role="separator" />

      <button
        className={cn(menuItemVariants({ variant: "danger" }))}
        onClick={() => {
          onDelete()
          onClose()
        }}
        role="menuitem"
      >
        <span className={cn(menuItemIconVariants())}>✕</span>
        <span className={cn(menuItemLabelVariants())}>Delete</span>
        <span className={cn(menuItemShortcutVariants())}>Del</span>
      </button>
    </div>
  )
}
