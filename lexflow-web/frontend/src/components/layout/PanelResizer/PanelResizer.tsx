import { cn } from "@/lib/cn"
import { panelResizerVariants } from "./styles"
import type { PanelResizerProps } from "./types"

export function PanelResizer({
  orientation,
  isResizing = false,
  onMouseDown,
  className,
}: PanelResizerProps) {
  return (
    <div
      className={cn(panelResizerVariants({ orientation, isResizing }), className)}
      onMouseDown={onMouseDown}
    />
  )
}
