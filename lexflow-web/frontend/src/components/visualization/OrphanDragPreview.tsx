import { useUiStore } from '../../store'
import styles from './OrphanDragPreview.module.css'

export function OrphanDragPreview() {
  const { draggingOrphan } = useUiStore()

  if (!draggingOrphan) return null

  const { fromX, fromY, toX, toY, opcode } = draggingOrphan

  // Calculate the path
  const dx = toX - fromX
  const dy = toY - fromY
  const distance = Math.sqrt(dx * dx + dy * dy)

  // Format the opcode name for display
  const displayName = opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, '')
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

  return (
    <g className={styles.orphanDragPreview}>
      {/* Dashed line from orphan to cursor */}
      <path
        className={styles.dragLine}
        d={`M ${fromX} ${fromY} L ${toX} ${toY}`}
        fill="none"
        stroke="#FACC15"
        strokeWidth={2}
        strokeDasharray="8 4"
      />

      {/* Start point indicator */}
      <circle cx={fromX} cy={fromY} r={4} fill="#FACC15" />

      {/* Ghost node preview at cursor (only show if dragging far enough) */}
      {distance > 30 && (
        <g transform={`translate(${toX - 40}, ${toY - 15})`}>
          <rect
            className={styles.ghostNode}
            width={80}
            height={30}
            rx={6}
            fill="rgba(250, 204, 21, 0.2)"
            stroke="#FACC15"
            strokeWidth={1.5}
            strokeDasharray="4 2"
          />
          <text className={styles.ghostLabel} x={40} y={18} textAnchor="middle">
            {displayName.length > 10 ? displayName.slice(0, 10) + '...' : displayName}
          </text>
        </g>
      )}

      {/* Cursor indicator */}
      <circle cx={toX} cy={toY} r={6} fill="rgba(250, 204, 21, 0.3)" stroke="#FACC15" strokeWidth={2} />
    </g>
  )
}
