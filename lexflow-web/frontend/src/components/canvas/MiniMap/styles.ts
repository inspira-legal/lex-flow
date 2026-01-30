import { cva } from "class-variance-authority"
import type { CSSProperties } from "react"

export const MINIMAP_WIDTH = 160
export const MINIMAP_HEIGHT = 120

// Layout constants
export const NODE_WIDTH = 180
export const NODE_HEIGHT = 80
export const H_GAP = 60
export const V_GAP = 40
export const WORKFLOW_GAP = 80

export const minimapVariants = cva(
  "absolute bottom-4 left-6 rounded-sm border border-border-subtle overflow-hidden z-10 shadow-md cursor-pointer transition-colors hover:border-border-strong"
)

export const viewportStyle: CSSProperties = {
  pointerEvents: "none",
}

export function getNodeColor(type: string): string {
  switch (type) {
    case "control_flow":
      return "#FF9500"
    case "data":
      return "#4CAF50"
    case "io":
      return "#22D3EE"
    case "operator":
      return "#9C27B0"
    case "workflow_op":
      return "#E91E63"
    default:
      return "#64748B"
  }
}
