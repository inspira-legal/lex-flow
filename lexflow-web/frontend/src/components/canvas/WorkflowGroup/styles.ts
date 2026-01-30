import type { CSSProperties } from "react"

const PADDING = 24
const LABEL_HEIGHT = 28

export function getGroupLayout(x: number, y: number, width: number, height: number) {
  return {
    padding: PADDING,
    labelHeight: LABEL_HEIGHT,
    rect: {
      x: x - PADDING,
      y: y - PADDING - LABEL_HEIGHT,
      width: width + PADDING * 2,
      height: height + PADDING * 2 + LABEL_HEIGHT,
    },
    header: {
      x: x - PADDING,
      y: y - PADDING - LABEL_HEIGHT,
      width: width + PADDING * 2,
      height: LABEL_HEIGHT + PADDING,
    },
    label: {
      x: x - PADDING + 12,
      y: y - PADDING - LABEL_HEIGHT + 8,
    },
    dragIcon: {
      x: x + width + PADDING - 24,
      y: y - PADDING - LABEL_HEIGHT + 10,
    },
  }
}

export function getBorderStyle(isMain: boolean): CSSProperties {
  return {
    fill: "transparent",
    stroke: isMain ? "var(--color-accent-blue)" : "var(--color-border-default)",
    strokeWidth: 2,
    strokeDasharray: "8 4",
    opacity: isMain ? 0.4 : 0.6,
  }
}

export function getLabelBgStyle(isMain: boolean): CSSProperties {
  return {
    fill: isMain ? "rgba(59, 130, 246, 0.1)" : "var(--color-surface-2)",
    stroke: isMain ? "var(--color-accent-blue)" : "var(--color-border-default)",
    strokeWidth: 1,
  }
}

export function getLabelStyle(isMain: boolean): CSSProperties {
  return {
    fontSize: "11px",
    fontWeight: 600,
    fill: isMain ? "var(--color-accent-blue)" : "var(--color-text-secondary)",
    fontFamily: "'Inter', sans-serif",
  }
}

export const dragHandleStyle: CSSProperties = {
  cursor: "grab",
  pointerEvents: "all",
}

export const dragIconStyle: CSSProperties = {
  pointerEvents: "none",
  color: "var(--color-text-muted)",
}
