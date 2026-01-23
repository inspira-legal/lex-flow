import { useUiStore } from "../../store";

export function VariableDragPreview() {
  const { draggingVariable } = useUiStore();

  if (!draggingVariable) return null;

  const { toX, toY, name } = draggingVariable;

  // Variable drag just shows a ghost pill following the cursor
  // (no wire like orphan drag - variables come from "nowhere")
  return (
    <g style={{ pointerEvents: "none" }}>
      {/* Ghost variable pill at cursor */}
      <g transform={`translate(${toX - 40}, ${toY - 14})`}>
        <rect
          width={80}
          height={28}
          rx={14}
          fill="rgba(34, 197, 94, 0.25)"
          stroke="#22C55E"
          strokeWidth={2}
        />
        <text
          x={40}
          y={18}
          textAnchor="middle"
          fill="#4ADE80"
          fontSize={12}
          fontWeight={600}
          fontFamily="'JetBrains Mono', monospace"
        >
          ${name.length > 8 ? name.slice(0, 8) + ".." : name}
        </text>
      </g>

      {/* Small cursor indicator */}
      <circle cx={toX} cy={toY} r={4} fill="#22C55E" />
    </g>
  );
}
