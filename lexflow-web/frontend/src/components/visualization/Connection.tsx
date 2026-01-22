import styles from './Connection.module.css'

interface ConnectionProps {
  x1: number
  y1: number
  x2: number
  y2: number
  color?: string
  label?: string
  isDotted?: boolean
}

export function Connection({ x1, y1, x2, y2, color = '#475569', label, isDotted }: ConnectionProps) {
  // Create a bezier curve for smooth connection
  const midX = (x1 + x2) / 2
  const controlOffset = Math.min(Math.abs(x2 - x1) / 2, 80)

  const path = `M ${x1} ${y1} C ${x1 + controlOffset} ${y1}, ${x2 - controlOffset} ${y2}, ${x2} ${y2}`

  return (
    <g className={styles.connection}>
      {/* Shadow/glow path */}
      <path className={styles.pathShadow} d={path} stroke={color} />

      {/* Main path */}
      <path
        className={`${styles.path} ${isDotted ? styles.dotted : ''}`}
        d={path}
        stroke={color}
      />

      {/* Animated flow dots (skip for dotted connections) */}
      {!isDotted && (
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
    </g>
  )
}
