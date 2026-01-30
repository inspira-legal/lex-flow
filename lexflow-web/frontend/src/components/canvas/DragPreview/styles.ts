import type { CSSProperties } from "react"

// Orphan drag preview styles
export const orphanDragPreviewStyle: CSSProperties = {
  pointerEvents: "none",
}

export const orphanDragLineStyle: CSSProperties = {
  fill: "none",
  stroke: "#FACC15",
  strokeWidth: 2,
  strokeDasharray: "8 4",
  // Animation applied via inline animation style
}

export const orphanStartCircleStyle: CSSProperties = {
  fill: "#FACC15",
}

export const orphanGhostNodeStyle: CSSProperties = {
  filter: "drop-shadow(0 2px 4px rgba(250, 204, 21, 0.3))",
}

export const orphanGhostRectStyle: CSSProperties = {
  fill: "rgba(250, 204, 21, 0.2)",
  stroke: "#FACC15",
  strokeWidth: 1.5,
  strokeDasharray: "4 2",
}

export const orphanGhostLabelStyle: CSSProperties = {
  fontSize: "9px",
  fontWeight: 600,
  fill: "#facc15",
}

export const orphanCursorCircleStyle: CSSProperties = {
  fill: "rgba(250, 204, 21, 0.3)",
  stroke: "#FACC15",
  strokeWidth: 2,
}

// Variable drag preview styles
export const variableDragPreviewStyle: CSSProperties = {
  pointerEvents: "none",
}

export const variableGhostRectStyle: CSSProperties = {
  fill: "rgba(34, 197, 94, 0.25)",
  stroke: "#22C55E",
  strokeWidth: 2,
}

export const variableGhostTextStyle: CSSProperties = {
  fill: "#4ADE80",
  fontSize: "12px",
  fontWeight: 600,
  fontFamily: "'JetBrains Mono', monospace",
}

export const variableCursorCircleStyle: CSSProperties = {
  fill: "#22C55E",
}
