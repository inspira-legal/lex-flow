// LayoutService - Business logic for canvas layout calculations

import type { FormattedValue } from "../../api/types";
import { CONTROL_FLOW_OPCODES } from "../../constants";

// Calculate total height of a reporter pill (including its content and label)
export function calculateReporterTotalHeight(
  value: FormattedValue,
  includeLabel = true,
): number {
  if (value.type !== "reporter") return 0;

  const labelHeight = includeLabel ? 14 : 0;
  const headerHeight = 22;

  let regularInputsCount = 0;
  let nestedReportersCount = 0;
  let nestedReportersHeight = 0;

  if (value.inputs) {
    for (const nestedValue of Object.values(value.inputs)) {
      if (nestedValue.type === "reporter" && nestedValue.opcode) {
        nestedReportersCount++;
        nestedReportersHeight +=
          calculateReporterTotalHeight(nestedValue, true) + 4;
      } else {
        const formatted = formatValueShort(nestedValue);
        if (formatted) regularInputsCount++;
      }
    }
  }

  const nestedLabelHeight = nestedReportersCount * 14;
  return (
    labelHeight +
    headerHeight +
    regularInputsCount * 14 +
    nestedLabelHeight +
    nestedReportersHeight +
    4
  );
}

// Format value for short display
export function formatValueShort(value: FormattedValue): string {
  switch (value.type) {
    case "literal": {
      const v = value.value;
      if (typeof v === "string")
        return `"${v.length > 10 ? v.slice(0, 10) + "..." : v}"`;
      return String(v);
    }
    case "variable":
      return `$${value.name}`;
    case "reporter":
      return `[reporter]`;
    case "workflow_call":
      return `→ ${value.name}`;
    default:
      return "";
  }
}

// Calculate node height based on inputs and branches
export function calculateNodeHeight(
  inputs: Record<string, FormattedValue>,
  opcode?: string,
): number {
  const reporterInputs: FormattedValue[] = [];
  const regularInputs: FormattedValue[] = [];

  for (const value of Object.values(inputs)) {
    if (value.type === "reporter" && value.opcode) {
      reporterInputs.push(value);
    } else {
      regularInputs.push(value);
    }
  }

  const inputPreviewCount = Math.min(regularInputs.length, 2);
  const baseHeight = 60 + inputPreviewCount * 18;

  const reporterSectionHeight = reporterInputs.reduce((acc, value) => {
    return acc + calculateReporterTotalHeight(value) + 4;
  }, 0);

  const hasBranchSlots =
    opcode && (CONTROL_FLOW_OPCODES as readonly string[]).includes(opcode);
  const branchSlotsHeight = hasBranchSlots ? 28 : 0;

  return baseHeight + reporterSectionHeight + branchSlotsHeight;
}

// Position interface
export interface Position {
  x: number;
  y: number;
}

// Calculate position with offset
export function applyPositionOffset(
  basePosition: Position,
  offset: Position | undefined,
): Position {
  if (!offset) return basePosition;
  return {
    x: basePosition.x + offset.x,
    y: basePosition.y + offset.y,
  };
}

// Calculate canvas coordinates from screen coordinates
export function screenToCanvas(
  screenX: number,
  screenY: number,
  panX: number,
  panY: number,
  zoom: number,
): Position {
  return {
    x: (screenX - panX) / zoom,
    y: (screenY - panY) / zoom,
  };
}

// Calculate screen coordinates from canvas coordinates
export function canvasToScreen(
  canvasX: number,
  canvasY: number,
  panX: number,
  panY: number,
  zoom: number,
): Position {
  return {
    x: canvasX * zoom + panX,
    y: canvasY * zoom + panY,
  };
}

// Clamp zoom to valid range
export function clampZoom(zoom: number, minZoom = 0.25, maxZoom = 2): number {
  return Math.max(minZoom, Math.min(maxZoom, zoom));
}

// Calculate bounding box for a set of positions
export interface BoundingBox {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  width: number;
  height: number;
}

export function calculateBoundingBox(
  positions: Position[],
): BoundingBox | null {
  if (positions.length === 0) return null;

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const pos of positions) {
    minX = Math.min(minX, pos.x);
    minY = Math.min(minY, pos.y);
    maxX = Math.max(maxX, pos.x);
    maxY = Math.max(maxY, pos.y);
  }

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

// Calculate center of a bounding box
export function calculateCenter(box: BoundingBox): Position {
  return {
    x: box.minX + box.width / 2,
    y: box.minY + box.height / 2,
  };
}

// Export as service object
export const layoutService = {
  calculateReporterTotalHeight,
  formatValueShort,
  calculateNodeHeight,
  applyPositionOffset,
  screenToCanvas,
  canvasToScreen,
  clampZoom,
  calculateBoundingBox,
  calculateCenter,
};
