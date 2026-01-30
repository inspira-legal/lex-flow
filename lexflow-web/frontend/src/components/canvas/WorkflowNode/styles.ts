import type { CSSProperties } from "react"

// Node dimensions - balanced square-ish proportions
export const NODE_WIDTH = 110
export const NODE_HEIGHT = 70
export const NODE_EXPANDED_INPUT_HEIGHT = 30

// Node type to default icon fallback mapping
export const NODE_TYPE_ICONS: Record<string, string> = {
  control_flow: "⟳",
  data: "📦",
  io: "📤",
  operator: "⚡",
  workflow_op: "🔗",
  opcode: "⚙",
}

// Main node card - minimal, clean appearance
export function getCardStyle(
  color: string,
  isSelected: boolean,
  isSearchMatch: boolean,
  isOrphan: boolean,
  isHovered: boolean,
  status: string,
  _isExpanded: boolean
): CSSProperties {
  let stroke = "transparent"
  let strokeWidth = 1.5
  let strokeDasharray = "none"
  let opacity = 1

  if (isOrphan) {
    stroke = "var(--color-accent-amber)"
    strokeDasharray = "6 3"
    opacity = 0.9
  }

  if (isHovered && !isSelected) {
    stroke = color
    strokeWidth = 1.5
    opacity = 1
  }

  if (isSearchMatch && !isSelected) {
    stroke = "#facc15"
    strokeWidth = 2
    strokeDasharray = "none"
  }

  if (isSelected) {
    stroke = "var(--color-accent-blue)"
    strokeWidth = 2
    strokeDasharray = "none"
    opacity = 1
  }

  if (status === "success") {
    stroke = "var(--color-accent-green)"
  } else if (status === "error") {
    stroke = "var(--color-accent-red)"
  }

  return {
    fill: "var(--color-surface-1)",
    stroke,
    strokeWidth,
    strokeDasharray,
    opacity,
    filter: isSelected
      ? "drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))"
      : isHovered
        ? "drop-shadow(0 2px 8px rgba(0, 0, 0, 0.25))"
        : "drop-shadow(0 1px 3px rgba(0, 0, 0, 0.2))",
    transition: "all 0.15s ease",
    animation: status === "running" ? "pulse 1.5s ease-in-out infinite" : "none",
  }
}

// Left color accent bar
export function getColorBarStyle(color: string): CSSProperties {
  return {
    fill: color,
    pointerEvents: "none",
  }
}

// Icon container circle
export function getIconContainerStyle(color: string, isHovered: boolean): CSSProperties {
  return {
    fill: isHovered ? color : `${color}20`,
    transition: "fill 0.15s ease",
  }
}

// Icon text
export const iconStyle: CSSProperties = {
  fontSize: "14px",
  fill: "var(--color-text-primary)",
  textAnchor: "middle",
  dominantBaseline: "central",
  pointerEvents: "none",
}

// Node name - primary label
export const nameStyle: CSSProperties = {
  fontSize: "11px",
  fontWeight: 600,
  fill: "var(--color-text-primary)",
  letterSpacing: "-0.01em",
}

// Node ID - secondary label (shown on hover or selection)
export const idStyle: CSSProperties = {
  fontSize: "9px",
  fill: "var(--color-text-muted)",
  fontFamily: "'JetBrains Mono', monospace",
}

// Connection port styles
export function getPortStyle(
  isHovered: boolean,
  isHighlighted: boolean,
  isDragging: boolean
): CSSProperties {
  const baseSize = 5

  return {
    fill: isHighlighted
      ? "var(--color-accent-green)"
      : "var(--color-surface-2)",
    stroke: isHighlighted
      ? "var(--color-accent-green)"
      : isHovered
        ? "var(--color-accent-blue)"
        : "var(--color-border-default)",
    strokeWidth: 1.5,
    r: isHighlighted ? baseSize + 1 : baseSize,
    transition: "all 0.12s ease",
    filter: isHighlighted ? "drop-shadow(0 0 6px var(--color-accent-green))" : "none",
    cursor: isDragging ? "pointer" : "crosshair",
  }
}

// Reporter indicator badge (shows count of nested reporters)
export function getReporterBadgeStyle(hasReporters: boolean, isExpanded: boolean): CSSProperties {
  return {
    fill: isExpanded ? "var(--color-accent-blue)" : "var(--color-surface-3)",
    stroke: "var(--color-border-subtle)",
    strokeWidth: 1,
    cursor: hasReporters ? "pointer" : "default",
    transition: "fill 0.15s ease",
    opacity: hasReporters ? 1 : 0,
    pointerEvents: hasReporters ? "all" : "none",
  }
}

export const reporterBadgeTextStyle: CSSProperties = {
  fontSize: "8px",
  fontWeight: 600,
  fill: "var(--color-text-secondary)",
  textAnchor: "middle",
  dominantBaseline: "central",
  pointerEvents: "none",
}

// Expanded input slot styles (shown during drag operations)
export function getInputSlotStyle(isHighlighted: boolean, isCompatible: boolean): CSSProperties {
  return {
    fill: isHighlighted
      ? "var(--color-accent-green)"
      : isCompatible
        ? "var(--color-surface-3)"
        : "var(--color-surface-2)",
    stroke: isHighlighted
      ? "var(--color-accent-green)"
      : isCompatible
        ? "var(--color-accent-blue)"
        : "var(--color-border-subtle)",
    strokeWidth: isHighlighted ? 1.5 : 1,
    strokeDasharray: isHighlighted ? "none" : "3 2",
    transition: "all 0.12s ease",
    cursor: "pointer",
  }
}

export const inputSlotTextStyle: CSSProperties = {
  fontSize: "9px",
  fill: "var(--color-text-muted)",
  fontWeight: 500,
}

export const inputSlotValueStyle: CSSProperties = {
  fontSize: "8px",
  fill: "var(--color-text-secondary)",
  fontFamily: "'JetBrains Mono', monospace",
}

// Status indicator
export function getStatusDotStyle(status: string): CSSProperties {
  const colors: Record<string, string> = {
    running: "var(--color-accent-amber)",
    success: "var(--color-accent-green)",
    error: "var(--color-accent-red)",
  }

  return {
    fill: colors[status] || "transparent",
    filter: status !== "idle" ? `drop-shadow(0 0 4px ${colors[status]})` : "none",
    transition: "all 0.15s ease",
  }
}

// Orphan indicator badge
export const orphanBadgeStyle: CSSProperties = {
  cursor: "grab",
  pointerEvents: "all",
}

export const orphanBadgeRectStyle: CSSProperties = {
  fill: "var(--color-accent-amber)",
  transition: "filter 0.15s ease",
}

export const orphanBadgeTextStyle: CSSProperties = {
  fontSize: "9px",
  fill: "var(--color-surface-0)",
  fontWeight: 600,
  pointerEvents: "none",
  textAnchor: "middle",
  dominantBaseline: "central",
}

// Node drag handle for free layout
export const nodeDragHandleStyle: CSSProperties = {
  cursor: "grab",
  pointerEvents: "all",
  fill: "transparent",
}

// Branch port styles
export function getBranchPortStyle(isConnected: boolean, color: string): CSSProperties {
  return {
    fill: isConnected ? color : "transparent",
    stroke: color,
    strokeWidth: 1.5,
    cursor: "crosshair",
    transition: "all 0.12s ease",
  }
}

export const branchLabelStyle: CSSProperties = {
  fontSize: "8px",
  fontWeight: 500,
  textAnchor: "middle",
  pointerEvents: "none",
  userSelect: "none",
  textTransform: "uppercase",
  letterSpacing: "0.3px",
}

// Collapsed reporter pill (minimal representation)
export function getCollapsedReporterStyle(color: string, isSelected: boolean): CSSProperties {
  return {
    fill: "var(--color-surface-2)",
    stroke: isSelected ? "var(--color-accent-blue)" : color,
    strokeWidth: isSelected ? 1.5 : 1,
    transition: "all 0.12s ease",
    cursor: "pointer",
  }
}

export const collapsedReporterTextStyle: CSSProperties = {
  fontSize: "9px",
  fontWeight: 500,
  fill: "var(--color-text-secondary)",
}

// Expanded reporter styles (when toggled open)
export function getExpandedReporterStyle(color: string, isSelected: boolean, depth: number): CSSProperties {
  const opacity = Math.max(0.6, 1 - depth * 0.15)

  return {
    fill: `var(--color-surface-${Math.min(depth + 2, 4)})`,
    stroke: isSelected ? "var(--color-accent-blue)" : color,
    strokeWidth: isSelected ? 1.5 : 1,
    opacity,
    transition: "all 0.15s ease",
    cursor: "pointer",
  }
}

export const reporterNameStyle: CSSProperties = {
  fontSize: "9px",
  fontWeight: 600,
  fill: "var(--color-text-primary)",
}

export const reporterInputStyle: CSSProperties = {
  fontSize: "8px",
  fill: "var(--color-text-muted)",
}

// Expand/collapse toggle for reporters
export function getExpandToggleStyle(isExpanded: boolean): CSSProperties {
  return {
    fill: "var(--color-surface-3)",
    stroke: "var(--color-border-subtle)",
    strokeWidth: 1,
    cursor: "pointer",
    transition: "transform 0.15s ease",
    transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
  }
}

export const expandToggleIconStyle: CSSProperties = {
  fontSize: "8px",
  fill: "var(--color-text-muted)",
  textAnchor: "middle",
  dominantBaseline: "central",
  pointerEvents: "none",
}
