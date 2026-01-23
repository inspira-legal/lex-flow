import { useUiStore } from "../../store";
import { getPortPositionFromRegistry } from "../../utils/wireUtils";
import { Connection } from "./Connection";

export function WireDragPreview() {
  const { draggingWire, slotPositions } = useUiStore();

  if (!draggingWire) return null;

  // Get source position from slot registry (single source of truth)
  const sourcePort = draggingWire.branchLabel || draggingWire.sourcePort;
  const sourcePos = getPortPositionFromRegistry(
    draggingWire.sourceNodeId,
    sourcePort,
    slotPositions,
  );

  // Fallback to stored coordinates if not yet in registry
  const sourceX = sourcePos?.x ?? draggingWire.sourceX;
  const sourceY = sourcePos?.y ?? draggingWire.sourceY;

  // Snap endpoint to nearby port position when available
  const endX = draggingWire.nearbyPort?.x ?? draggingWire.dragX;
  const endY = draggingWire.nearbyPort?.y ?? draggingWire.dragY;

  // Determine direction based on source port type
  const isReverse = draggingWire.sourcePort === "input";

  // When dragging from input, swap the bezier direction so the curve looks correct
  const x1 = isReverse ? endX : sourceX;
  const y1 = isReverse ? endY : sourceY;
  const x2 = isReverse ? sourceX : endX;
  const y2 = isReverse ? sourceY : endY;

  // Green when snapping to a valid port, cyan otherwise
  const color = draggingWire.nearbyPort ? "#22C55E" : "#22D3EE";

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
  );
}
