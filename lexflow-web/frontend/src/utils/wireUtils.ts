// Wire utilities for proximity detection and port calculations

import type { NodeSlotPositions, SlotPosition } from "../store/uiStore";

export const WIRE_SNAP_DISTANCE = 25;
export const NODE_WIDTH = 180;

export function calculateDistance(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
): number {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
}

// Get port position from slot registry
export function getPortPositionFromRegistry(
  nodeId: string,
  port: "input" | "output" | string,
  slotPositions: Record<string, NodeSlotPositions>,
): SlotPosition | null {
  const slots = slotPositions[nodeId];
  if (!slots) return null;

  if (port === "input") return slots.input;
  if (port === "output") return slots.output;
  return slots.branches[port] || null;
}

// Legacy function - fallback when slot registry isn't available
export function getPortPosition(
  nodeX: number,
  nodeY: number,
  port: "input" | "output",
): { x: number; y: number } {
  // Input port is at left edge (x=0), output port at right edge (x=180)
  // Port Y position is at vertical center (approximately y=30)
  const portY = nodeY + 30;
  if (port === "input") {
    return { x: nodeX, y: portY };
  }
  return { x: nodeX + NODE_WIDTH, y: portY };
}

interface LayoutNode {
  node: { id: string };
  x: number;
  y: number;
  isOrphan?: boolean;
}

interface NearbyPort {
  nodeId: string;
  port: "input" | "output";
  x: number;
  y: number;
}

// Find nearest port using slot registry (preferred)
export function findNearestPortFromRegistry(
  dragX: number,
  dragY: number,
  sourceNodeId: string,
  sourcePort: "input" | "output",
  slotPositions: Record<string, NodeSlotPositions>,
): NearbyPort | null {
  // Determine which port type we're looking for (opposite of source)
  const targetPortType = sourcePort === "output" ? "input" : "output";

  let nearestPort: NearbyPort | null = null;
  let nearestDistance = WIRE_SNAP_DISTANCE;

  for (const [nodeId, slots] of Object.entries(slotPositions)) {
    // Skip the source node
    if (nodeId === sourceNodeId) continue;

    // Get the target port position from registry
    const portPos = targetPortType === "input" ? slots.input : slots.output;
    const distance = calculateDistance(dragX, dragY, portPos.x, portPos.y);

    if (distance < nearestDistance) {
      nearestDistance = distance;
      nearestPort = {
        nodeId,
        port: targetPortType,
        x: portPos.x,
        y: portPos.y,
      };
    }
  }

  return nearestPort;
}

// Legacy function - fallback using layout nodes
export function findNearestPort(
  dragX: number,
  dragY: number,
  sourceNodeId: string,
  sourcePort: "input" | "output",
  layoutNodes: LayoutNode[],
): NearbyPort | null {
  // Determine which port type we're looking for (opposite of source)
  const targetPortType = sourcePort === "output" ? "input" : "output";

  let nearestPort: NearbyPort | null = null;
  let nearestDistance = WIRE_SNAP_DISTANCE;

  for (const ln of layoutNodes) {
    // Skip the source node
    if (ln.node.id === sourceNodeId) continue;

    // Get the target port position
    const portPos = getPortPosition(ln.x, ln.y, targetPortType);
    const distance = calculateDistance(dragX, dragY, portPos.x, portPos.y);

    if (distance < nearestDistance) {
      nearestDistance = distance;
      nearestPort = {
        nodeId: ln.node.id,
        port: targetPortType,
        x: portPos.x,
        y: portPos.y,
      };
    }
  }

  return nearestPort;
}
