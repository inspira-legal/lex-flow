import type { CSSProperties } from "react"

export const inputSlotStyle: CSSProperties = {
  pointerEvents: "all",
}

export function getSlotBgStyle(
  isDropTarget: boolean,
  isCompatible: boolean | null,
  slotColor: string
): CSSProperties {
  if (!isDropTarget) {
    return {
      fill: "transparent",
      stroke: "transparent",
      strokeWidth: 1,
      transition: "fill 0.15s ease, stroke 0.15s ease",
    }
  }

  if (isCompatible === true) {
    return {
      fill: "rgba(52, 211, 153, 0.15)",
      stroke: "var(--color-accent-green)",
      strokeWidth: 1,
      strokeDasharray: "none",
      transition: "fill 0.15s ease, stroke 0.15s ease",
      // Pulsing animation for compatible targets
      animation: "pulse-slot 0.6s ease infinite alternate",
    }
  }

  if (isCompatible === false) {
    return {
      fill: "rgba(248, 113, 113, 0.15)",
      stroke: "var(--color-accent-red)",
      strokeWidth: 1,
      strokeDasharray: "none",
      transition: "fill 0.15s ease, stroke 0.15s ease",
    }
  }

  // Neutral state (for variables or unknown compatibility)
  return {
    fill: "rgba(148, 163, 184, 0.1)",
    stroke: slotColor,
    strokeWidth: 1,
    strokeDasharray: "4 2",
    transition: "fill 0.15s ease, stroke 0.15s ease",
  }
}

export const inputKeyStyle: CSSProperties = {
  fontSize: "9px",
  fontWeight: 500,
  fill: "var(--color-text-muted)",
  textTransform: "lowercase",
}

export const inputValueStyle: CSSProperties = {
  fontSize: "9px",
  fontFamily: "'JetBrains Mono', monospace",
  fill: "var(--color-text-secondary)",
}

export const typeHintStyle: CSSProperties = {
  fontSize: "7px",
  fill: "var(--color-text-muted)",
  fontStyle: "italic",
  textTransform: "uppercase",
  letterSpacing: "0.3px",
}
