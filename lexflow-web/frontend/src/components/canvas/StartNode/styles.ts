import type { CSSProperties } from "react"

export const START_NODE_WIDTH = 160
export const START_NODE_HEIGHT = 80

// Green color for start nodes
const GREEN_500 = "#22c55e"
const GREEN_400 = "#4ade80"

export function getCardStyle(isSelected: boolean, isHovered: boolean): CSSProperties {
  return {
    fill: "var(--color-surface-1)",
    stroke: isSelected ? "var(--color-accent-blue)" : GREEN_500,
    strokeWidth: isSelected || isHovered ? 2.5 : 2,
    transition: "stroke 0.15s ease, stroke-width 0.15s ease, filter 0.15s ease",
    filter: isSelected
      ? "drop-shadow(0 0 8px rgba(34, 211, 238, 0.4))"
      : isHovered
        ? "drop-shadow(0 4px 8px rgba(34, 197, 94, 0.3))"
        : "drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))",
  }
}

export const colorBarStyle: CSSProperties = {
  fill: GREEN_500,
  pointerEvents: "none",
}

export const flagIconStyle: CSSProperties = {
  fontSize: "14px",
}

export const nameStyle: CSSProperties = {
  fontSize: "13px",
  fontWeight: 700,
  fill: "var(--color-text-primary)",
}

export const interfaceLabelStyle: CSSProperties = {
  fontSize: "9px",
  fill: "var(--color-text-secondary)",
  fontFamily: "'JetBrains Mono', monospace",
}

export const variableStyle: CSSProperties = {
  fontSize: "10px",
  fontFamily: "'JetBrains Mono', monospace",
  fill: GREEN_400,
}

export const moreVarsStyle: CSSProperties = {
  fontSize: "9px",
  fill: "var(--color-text-muted)",
  fontStyle: "italic",
}

export function getOutputPortStyle(isHovered: boolean): CSSProperties {
  return {
    fill: isHovered ? GREEN_500 : "var(--color-surface-2)",
    stroke: isHovered ? GREEN_400 : GREEN_500,
    strokeWidth: 2,
    transition: "all 0.15s ease",
    filter: isHovered ? `drop-shadow(0 0 4px ${GREEN_500})` : "none",
  }
}

export const dragHandleStyle: CSSProperties = {
  cursor: "grab",
  pointerEvents: "all",
}
