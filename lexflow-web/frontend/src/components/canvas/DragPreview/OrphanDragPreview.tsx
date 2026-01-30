import { useUiStore } from "@/store"
import {
  orphanDragPreviewStyle,
  orphanStartCircleStyle,
  orphanGhostNodeStyle,
  orphanGhostRectStyle,
  orphanGhostLabelStyle,
  orphanCursorCircleStyle,
} from "./styles"

export function OrphanDragPreview() {
  const { draggingOrphan } = useUiStore()

  if (!draggingOrphan) return null

  const { fromX, fromY, toX, toY, opcode } = draggingOrphan

  // Guard against invalid coordinates
  if (!Number.isFinite(fromX) || !Number.isFinite(fromY) || !Number.isFinite(toX) || !Number.isFinite(toY)) {
    return null
  }

  // Calculate the path
  const dx = toX - fromX
  const dy = toY - fromY
  const distance = Math.sqrt(dx * dx + dy * dy)

  // Format the opcode name for display
  const displayName = opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, "")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")

  return (
    <g style={orphanDragPreviewStyle}>
      {/* Dashed line from orphan to cursor */}
      <path
        d={`M ${fromX} ${fromY} L ${toX} ${toY}`}
        fill="none"
        stroke="#FACC15"
        strokeWidth={2}
        strokeDasharray="8 4"
        style={{
          animation: "dash-flow 0.5s linear infinite",
        }}
      />

      {/* Start point indicator */}
      <circle cx={fromX} cy={fromY} r={4} style={orphanStartCircleStyle} />

      {/* Ghost node preview at cursor (only show if dragging far enough) */}
      {distance > 30 && (
        <g transform={`translate(${toX - 40}, ${toY - 15})`} style={orphanGhostNodeStyle}>
          <rect width={80} height={30} rx={6} style={orphanGhostRectStyle} />
          <text x={40} y={18} textAnchor="middle" style={orphanGhostLabelStyle}>
            {displayName.length > 10 ? displayName.slice(0, 10) + "..." : displayName}
          </text>
        </g>
      )}

      {/* Cursor indicator */}
      <circle cx={toX} cy={toY} r={6} style={orphanCursorCircleStyle} />
    </g>
  )
}
