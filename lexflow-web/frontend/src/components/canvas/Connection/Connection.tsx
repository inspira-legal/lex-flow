import { memo } from "react"
import { useUiStore } from "@/store"
import {
  calculateBezierPath,
  hitAreaStyle,
  getPathShadowStyle,
  getPathStyle,
  flowDotStyle,
  labelStyle,
  deleteButtonStyle,
  getDeleteButtonCircleStyle,
  deleteButtonTextStyle,
} from "./styles"
import type { ConnectionProps } from "./types"

export const Connection = memo(function Connection({
  fromNodeId,
  toNodeId,
  fromPort = "output",
  toPort = "input",
  x1: directX1,
  y1: directY1,
  x2: directX2,
  y2: directY2,
  color = "#475569",
  label,
  isDotted,
  isSelected,
  onSelect,
  onDelete,
}: ConnectionProps) {
  const slotPositions = useUiStore((s) => s.slotPositions)

  // Get positions from slot registry, falling back to direct coordinates
  let x1: number, y1: number, x2: number, y2: number

  if (
    directX1 !== undefined &&
    directY1 !== undefined &&
    directX2 !== undefined &&
    directY2 !== undefined
  ) {
    // Use direct coordinates (for WireDragPreview)
    x1 = directX1
    y1 = directY1
    x2 = directX2
    y2 = directY2
  } else {
    // Look up from slot registry
    const fromSlots = slotPositions[fromNodeId]
    const toSlots = slotPositions[toNodeId]

    if (!fromSlots || !toSlots) return null

    // Get source position based on port type
    const fromPos =
      fromPort === "output"
        ? fromSlots.output
        : fromPort === "input"
          ? fromSlots.input
          : fromSlots.branches[fromPort]
    const toPos = toPort === "input" ? toSlots.input : toSlots.output

    if (!fromPos || !toPos) return null

    x1 = fromPos.x
    y1 = fromPos.y
    x2 = toPos.x
    y2 = toPos.y
  }

  // Guard against invalid coordinates (NaN, Infinity, or very large values)
  if (!Number.isFinite(x1) || !Number.isFinite(y1) || !Number.isFinite(x2) || !Number.isFinite(y2)) {
    return null
  }

  // Guard against uninitialized positions (both endpoints at origin or same point)
  // This can happen briefly when a new node is added but hasn't registered its slot yet
  if ((x1 === 0 && y1 === 0 && x2 === 0 && y2 === 0) || (x1 === x2 && y1 === y2)) {
    return null
  }

  const path = calculateBezierPath(x1, y1, x2, y2)
  const midX = (x1 + x2) / 2
  const midY = (y1 + y2) / 2

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onSelect?.()
  }

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.()
  }

  return (
    <g style={{ cursor: "pointer" }}>
      {/* Invisible wider hit area for easier clicking */}
      <path style={hitAreaStyle} d={path} onClick={handleClick} />

      {/* Shadow/glow path */}
      <path style={getPathShadowStyle(color, isSelected ?? false)} d={path} />

      {/* Main path */}
      <path style={getPathStyle(color, isSelected ?? false, isDotted ?? false)} d={path} />

      {/* Animated flow dots (skip for dotted connections) */}
      {!isDotted && !isSelected && (
        <circle style={flowDotStyle} r={3} fill={color}>
          <animateMotion dur="2s" repeatCount="indefinite" path={path} />
        </circle>
      )}

      {/* Label (for branch names or input names) */}
      {label && (
        <text style={labelStyle} x={midX} y={(y1 + y2) / 2 - 8}>
          {label}
        </text>
      )}

      {/* Delete button at midpoint when selected */}
      {isSelected && onDelete && (
        <g
          style={deleteButtonStyle}
          transform={`translate(${midX}, ${midY})`}
          onClick={handleDeleteClick}
        >
          <circle cx={0} cy={0} r={12} style={getDeleteButtonCircleStyle()} />
          <text x={0} y={4} textAnchor="middle" style={deleteButtonTextStyle}>
            ×
          </text>
        </g>
      )}
    </g>
  )
})
