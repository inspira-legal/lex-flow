import { useUiStore } from '../../store'
import { Connection } from './Connection'

export function WireDragPreview() {
  const { draggingWire } = useUiStore()

  if (!draggingWire) return null

  // Snap endpoint to nearby port position when available
  const endX = draggingWire.nearbyPort?.x ?? draggingWire.dragX
  const endY = draggingWire.nearbyPort?.y ?? draggingWire.dragY

  // Determine direction based on source port type
  const isReverse = draggingWire.sourcePort === 'input'

  // When dragging from input, swap the bezier direction so the curve looks correct
  const x1 = isReverse ? endX : draggingWire.sourceX
  const y1 = isReverse ? endY : draggingWire.sourceY
  const x2 = isReverse ? draggingWire.sourceX : endX
  const y2 = isReverse ? draggingWire.sourceY : endY

  // Green when snapping to a valid port, cyan otherwise
  const color = draggingWire.nearbyPort ? '#22C55E' : '#22D3EE'

  return (
    <Connection
      fromNodeId={draggingWire.sourceNodeId}
      toNodeId=""
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      color={color}
      isDotted={!draggingWire.nearbyPort}
    />
  )
}
