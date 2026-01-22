import { useRef, useCallback } from 'react'
import { useUiStore } from '../../store'
import styles from './WorkflowGroup.module.css'

interface WorkflowGroupProps {
  name: string
  x: number
  y: number
  width: number
  height: number
  isMain?: boolean
  zoom: number
  onDrag?: (dx: number, dy: number) => void
}

export function WorkflowGroup({ name, x, y, width, height, isMain, zoom, onDrag }: WorkflowGroupProps) {
  const padding = 24
  const labelHeight = 28
  const isDragging = useRef(false)
  const dragStart = useRef({ x: 0, y: 0 })
  const setIsDraggingWorkflow = useUiStore((s) => s.setIsDraggingWorkflow)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!onDrag) return
    e.stopPropagation()
    e.preventDefault()
    isDragging.current = true
    dragStart.current = { x: e.clientX, y: e.clientY }
    setIsDraggingWorkflow(true)

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!isDragging.current) return
      moveEvent.preventDefault()
      const dx = (moveEvent.clientX - dragStart.current.x) / zoom
      const dy = (moveEvent.clientY - dragStart.current.y) / zoom
      dragStart.current = { x: moveEvent.clientX, y: moveEvent.clientY }
      onDrag(dx, dy)
    }

    const handleMouseUp = () => {
      isDragging.current = false
      setIsDraggingWorkflow(false)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
  }, [onDrag, zoom, setIsDraggingWorkflow])

  const displayName = isMain && name !== 'main' ? `${name} (main)` : name
  const labelWidth = displayName.length * 7 + 24

  return (
    <g className={styles.group}>
      {/* Dotted border rectangle */}
      <rect
        x={x - padding}
        y={y - padding - labelHeight}
        width={width + padding * 2}
        height={height + padding * 2 + labelHeight}
        rx={12}
        className={`${styles.border} ${isMain ? styles.main : ''}`}
      />

      {/* Draggable header area */}
      <rect
        x={x - padding}
        y={y - padding - labelHeight}
        width={width + padding * 2}
        height={labelHeight + padding}
        fill="transparent"
        className={styles.dragHandle}
        onMouseDown={handleMouseDown}
      />

      {/* Workflow name label */}
      <g transform={`translate(${x - padding + 12}, ${y - padding - labelHeight + 8})`}>
        <rect
          x={0}
          y={0}
          width={labelWidth}
          height={20}
          rx={4}
          className={`${styles.labelBg} ${isMain ? styles.main : ''}`}
        />
        <text
          x={12}
          y={14}
          className={`${styles.label} ${isMain ? styles.main : ''}`}
        >
          {displayName}
        </text>
      </g>

      {/* Drag indicator icon */}
      <g transform={`translate(${x + width + padding - 24}, ${y - padding - labelHeight + 10})`} className={styles.dragIcon}>
        <rect x={0} y={0} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={6} y={0} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={0} y={6} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
        <rect x={6} y={6} width={4} height={4} rx={1} fill="currentColor" opacity={0.4} />
      </g>
    </g>
  )
}
