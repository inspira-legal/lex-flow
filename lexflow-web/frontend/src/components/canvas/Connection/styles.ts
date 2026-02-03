import type { CSSProperties } from "react"

export function calculateBezierPath(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): string {
  const dx = x2 - x1
  const dy = Math.abs(y2 - y1)
  const absDx = Math.abs(dx)
  const isMoreVertical = dy > absDx * 0.5

  if (isMoreVertical && y2 > y1) {
    // Vertical/diagonal connection (like branch connections from bottom)
    const controlOffsetY = Math.min(dy / 2, 60)
    return `M ${x1} ${y1} C ${x1} ${y1 + controlOffsetY}, ${x2} ${y2 - controlOffsetY}, ${x2} ${y2}`
  } else if (dx >= 0) {
    // Standard left-to-right horizontal connection
    const controlOffsetX = Math.min(absDx / 2, 80)
    return `M ${x1} ${y1} C ${x1 + controlOffsetX} ${y1}, ${x2 - controlOffsetX} ${y2}, ${x2} ${y2}`
  } else {
    // Backward connection (right-to-left) - curve around
    const loopOffset = Math.max(50, absDx / 2)
    const verticalOffset = Math.max(40, dy / 2 + 20)
    // Go right from source, then down/up, then left to target
    return `M ${x1} ${y1} C ${x1 + loopOffset} ${y1}, ${x1 + loopOffset} ${y1 + verticalOffset}, ${(x1 + x2) / 2} ${y1 + verticalOffset} S ${x2 - loopOffset} ${y2}, ${x2} ${y2}`
  }
}

export const hitAreaStyle: CSSProperties = {
  fill: "none",
  stroke: "transparent",
  strokeWidth: 16,
  strokeLinecap: "round",
  pointerEvents: "stroke",
}

export function getPathShadowStyle(color: string, isSelected: boolean): CSSProperties {
  return {
    fill: "none",
    stroke: isSelected ? "#22d3ee" : color,
    strokeWidth: 6,
    strokeLinecap: "round",
    opacity: isSelected ? 0.3 : 0.2,
    pointerEvents: "none",
  }
}

export function getPathStyle(
  color: string,
  isSelected: boolean,
  isDotted: boolean
): CSSProperties {
  return {
    fill: "none",
    stroke: isSelected ? "#22D3EE" : color,
    strokeWidth: isSelected ? 3 : isDotted ? 1.5 : 2,
    strokeLinecap: "round",
    strokeDasharray: isDotted ? "6 4" : "none",
    pointerEvents: "none",
    transition: "stroke-width 0.15s ease, stroke 0.15s ease",
    filter: isSelected ? "drop-shadow(0 0 6px rgba(34, 211, 238, 0.5))" : "none",
  }
}

export const flowDotStyle: CSSProperties = {
  opacity: 0.6,
  pointerEvents: "none",
}

export const labelStyle: CSSProperties = {
  fontSize: "10px",
  fill: "var(--color-text-muted)",
  textAnchor: "middle",
  fontWeight: 500,
  pointerEvents: "none",
}

export const deleteButtonStyle: CSSProperties = {
  cursor: "pointer",
  pointerEvents: "all",
}

export function getDeleteButtonCircleStyle(): CSSProperties {
  return {
    fill: "var(--color-accent-red)",
    stroke: "var(--color-surface-0)",
    strokeWidth: 2,
    transition: "transform 0.15s ease, filter 0.15s ease",
  }
}

export const deleteButtonTextStyle: CSSProperties = {
  fontSize: "16px",
  fontWeight: "bold",
  fill: "white",
  pointerEvents: "none",
}
