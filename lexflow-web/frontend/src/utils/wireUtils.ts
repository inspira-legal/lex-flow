// Wire utilities for proximity detection and port calculations

export const WIRE_SNAP_DISTANCE = 40
export const NODE_WIDTH = 180

export function calculateDistance(x1: number, y1: number, x2: number, y2: number): number {
  return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
}

export function getPortPosition(
  nodeX: number,
  nodeY: number,
  port: 'input' | 'output'
): { x: number; y: number } {
  // Input port is at left edge (x=0), output port at right edge (x=180)
  // Port Y position is at vertical center (approximately y=30)
  const portY = nodeY + 30
  if (port === 'input') {
    return { x: nodeX, y: portY }
  }
  return { x: nodeX + NODE_WIDTH, y: portY }
}

interface LayoutNode {
  node: { id: string }
  x: number
  y: number
  isOrphan?: boolean
}

interface NearbyPort {
  nodeId: string
  port: 'input' | 'output'
  x: number
  y: number
}

export function findNearestPort(
  dragX: number,
  dragY: number,
  sourceNodeId: string,
  sourcePort: 'input' | 'output',
  layoutNodes: LayoutNode[]
): NearbyPort | null {
  // Determine which port type we're looking for (opposite of source)
  const targetPortType = sourcePort === 'output' ? 'input' : 'output'

  let nearestPort: NearbyPort | null = null
  let nearestDistance = WIRE_SNAP_DISTANCE

  for (const ln of layoutNodes) {
    // Skip the source node
    if (ln.node.id === sourceNodeId) continue

    // Get the target port position
    const portPos = getPortPosition(ln.x, ln.y, targetPortType)
    const distance = calculateDistance(dragX, dragY, portPos.x, portPos.y)

    if (distance < nearestDistance) {
      nearestDistance = distance
      nearestPort = {
        nodeId: ln.node.id,
        port: targetPortType,
        x: portPos.x,
        y: portPos.y,
      }
    }
  }

  return nearestPort
}
