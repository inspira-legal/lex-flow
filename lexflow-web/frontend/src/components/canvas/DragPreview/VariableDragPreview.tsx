import { useUiStore } from "@/store"
import {
  variableDragPreviewStyle,
  variableGhostRectStyle,
  variableGhostTextStyle,
  variableCursorCircleStyle,
} from "./styles"

export function VariableDragPreview() {
  const { draggingVariable } = useUiStore()

  if (!draggingVariable) return null

  const { toX, toY, name } = draggingVariable

  // Variable drag just shows a ghost pill following the cursor
  // (no wire like orphan drag - variables come from "nowhere")
  return (
    <g style={variableDragPreviewStyle}>
      {/* Ghost variable pill at cursor */}
      <g transform={`translate(${toX - 40}, ${toY - 14})`}>
        <rect width={80} height={28} rx={14} style={variableGhostRectStyle} />
        <text x={40} y={18} textAnchor="middle" style={variableGhostTextStyle}>
          ${name.length > 8 ? name.slice(0, 8) + ".." : name}
        </text>
      </g>

      {/* Small cursor indicator */}
      <circle cx={toX} cy={toY} r={4} style={variableCursorCircleStyle} />
    </g>
  )
}
