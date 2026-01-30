import { useRef, useCallback } from "react"
import { useUiStore } from "@/store"
import { getGroupLayout, getBorderStyle, getLabelBgStyle, getLabelStyle, dragHandleStyle, dragIconStyle } from "./styles"
import type { WorkflowGroupProps } from "./types"

export function WorkflowGroup({
  name,
  x,
  y,
  width,
  height,
  isMain,
  zoom,
  onDrag,
}: WorkflowGroupProps) {
  const isDragging = useRef(false)
  const dragStart = useRef({ x: 0, y: 0 })
  const setIsDraggingWorkflow = useUiStore((s) => s.setIsDraggingWorkflow)

  const layout = getGroupLayout(x, y, width, height)

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!onDrag) return
      e.stopPropagation()
      e.preventDefault()
      isDragging.current = true
      dragStart.current = { x: e.clientX, y: e.clientY }
      setIsDraggingWorkflow(true)

      const handleMouseMove = (moveEvent: MouseEvent) => {
        if (!isDragging.current) return
        moveEvent.preventDefault()
        const dx = (moveEvent.clientX - dragStart.current.x) / zoom
        const dy = (moveEvent.clientY - dragStart.current.y) / zoom
        dragStart.current = { x: moveEvent.clientX, y: moveEvent.clientY }
        onDrag(dx, dy)
      }

      const handleMouseUp = () => {
        isDragging.current = false
        setIsDraggingWorkflow(false)
        window.removeEventListener("mousemove", handleMouseMove)
        window.removeEventListener("mouseup", handleMouseUp)
      }

      window.addEventListener("mousemove", handleMouseMove)
      window.addEventListener("mouseup", handleMouseUp)
    },
    [onDrag, zoom, setIsDraggingWorkflow]
  )

  const displayName = isMain && name !== "main" ? `${name} (main)` : name
  const labelWidth = displayName.length * 7 + 24

  return (
    <g style={{ pointerEvents: "none" }}>
      {/* Dotted border rectangle */}
      <rect
        x={layout.rect.x}
        y={layout.rect.y}
        width={layout.rect.width}
        height={layout.rect.height}
        rx={12}
        style={getBorderStyle(isMain ?? false)}
      />

      {/* Draggable header area */}
      <rect
        x={layout.header.x}
        y={layout.header.y}
        width={layout.header.width}
        height={layout.header.height}
        fill="transparent"
        style={dragHandleStyle}
        onMouseDown={handleMouseDown}
      />

      {/* Workflow name label */}
      <g transform={`translate(${layout.label.x}, ${layout.label.y})`}>
        <rect
          x={0}
          y={0}
          width={labelWidth}
          height={20}
          rx={4}
          style={getLabelBgStyle(isMain ?? false)}
        />
        <text x={12} y={14} style={getLabelStyle(isMain ?? false)}>
          {displayName}
        </text>
      </g>

      {/* Drag indicator icon (4 small dots) */}
      <g transform={`translate(${layout.dragIcon.x}, ${layout.dragIcon.y})`} style={dragIconStyle}>
        <rect x={0} y={0} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={6} y={0} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={0} y={6} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={6} y={6} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
      </g>
    </g>
  )
}
