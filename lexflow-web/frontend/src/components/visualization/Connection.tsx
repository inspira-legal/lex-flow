import { useUiStore } from "../../store";
import styles from "./Connection.module.css";

interface ConnectionProps {
  fromNodeId: string;
  toNodeId: string;
  fromPort?: "input" | "output" | string; // string for branch names like "THEN", "ELSE"
  toPort?: "input" | "output";
  // Optional direct coordinates (used by WireDragPreview)
  x1?: number;
  y1?: number;
  x2?: number;
  y2?: number;
  color?: string;
  label?: string;
  isDotted?: boolean;
  isSelected?: boolean;
  onSelect?: () => void;
  onDelete?: () => void;
}

export function Connection({
  fromNodeId,
  toNodeId,
  fromPort = "output",
  toPort = "input",
  x1: directX1,
  y1: directY1,
  x2: directX2,
  y2: directY2,
  color = "#475569",
  label,
  isDotted,
  isSelected,
  onSelect,
  onDelete,
}: ConnectionProps) {
  const slotPositions = useUiStore((s) => s.slotPositions);

  // Get positions from slot registry, falling back to direct coordinates
  let x1: number, y1: number, x2: number, y2: number;

  if (
    directX1 !== undefined &&
    directY1 !== undefined &&
    directX2 !== undefined &&
    directY2 !== undefined
  ) {
    // Use direct coordinates (for WireDragPreview)
    x1 = directX1;
    y1 = directY1;
    x2 = directX2;
    y2 = directY2;
  } else {
    // Look up from slot registry
    const fromSlots = slotPositions[fromNodeId];
    const toSlots = slotPositions[toNodeId];

    if (!fromSlots || !toSlots) return null;

    // Get source position based on port type
    const fromPos =
      fromPort === "output"
        ? fromSlots.output
        : fromPort === "input"
          ? fromSlots.input
          : fromSlots.branches[fromPort];
    const toPos = toPort === "input" ? toSlots.input : toSlots.output;

    if (!fromPos || !toPos) return null;

    x1 = fromPos.x;
    y1 = fromPos.y;
    x2 = toPos.x;
    y2 = toPos.y;
  }
  // Create a bezier curve for smooth connection
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  // Determine if this is more of a vertical or horizontal connection
  const dx = Math.abs(x2 - x1);
  const dy = Math.abs(y2 - y1);
  const isMoreVertical = dy > dx * 0.5; // If vertical distance is significant

  let path: string;
  if (isMoreVertical && y2 > y1) {
    // Vertical/diagonal connection (like branch connections from bottom)
    // Control points extend vertically
    const controlOffsetY = Math.min(dy / 2, 60);
    path = `M ${x1} ${y1} C ${x1} ${y1 + controlOffsetY}, ${x2} ${y2 - controlOffsetY}, ${x2} ${y2}`;
  } else {
    // Horizontal connection (standard left-to-right)
    // Control points extend horizontally
    const controlOffsetX = Math.min(dx / 2, 80);
    path = `M ${x1} ${y1} C ${x1 + controlOffsetX} ${y1}, ${x2 - controlOffsetX} ${y2}, ${x2} ${y2}`;
  }

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect?.();
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.();
  };

  return (
    <g className={`${styles.connection} ${isSelected ? styles.selected : ""}`}>
      {/* Invisible wider hit area for easier clicking */}
      <path className={styles.hitArea} d={path} onClick={handleClick} />

      {/* Shadow/glow path */}
      <path className={styles.pathShadow} d={path} stroke={color} />

      {/* Main path */}
      <path
        className={`${styles.path} ${isDotted ? styles.dotted : ""}`}
        d={path}
        stroke={isSelected ? "#22D3EE" : color}
      />

      {/* Animated flow dots (skip for dotted connections) */}
      {!isDotted && !isSelected && (
        <circle className={styles.flowDot} r={3} fill={color}>
          <animateMotion dur="2s" repeatCount="indefinite" path={path} />
        </circle>
      )}

      {/* Label (for branch names or input names) */}
      {label && (
        <text className={styles.label} x={midX} y={(y1 + y2) / 2 - 8}>
          {label}
        </text>
      )}

      {/* Delete button at midpoint when selected */}
      {isSelected && onDelete && (
        <g
          className={styles.deleteButton}
          transform={`translate(${midX}, ${midY})`}
          onClick={handleDeleteClick}
        >
          <circle cx={0} cy={0} r={12} />
          <text x={0} y={4} textAnchor="middle">
            ×
          </text>
        </g>
      )}
    </g>
  );
}
