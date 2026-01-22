import { useRef } from 'react'
import { useUiStore, useWorkflowStore } from '../../store'
import type { WorkflowInterface } from '../../api/types'
import styles from './StartNode.module.css'

interface StartNodeProps {
  workflowName: string
  workflowInterface: WorkflowInterface
  variables: Record<string, unknown>
  x: number
  y: number
  zoom?: number
  onDrag?: (dx: number, dy: number) => void
}

const START_NODE_WIDTH = 160
const START_NODE_HEIGHT = 80

export { START_NODE_WIDTH, START_NODE_HEIGHT }

export function StartNode({
  workflowName,
  workflowInterface,
  variables,
  x,
  y,
  zoom = 1,
  onDrag,
}: StartNodeProps) {
  const { selectNode } = useWorkflowStore()
  const {
    selectedStartNode,
    selectStartNode,
    openNodeEditor,
    layoutMode,
    setIsDraggingNode,
  } = useUiStore()

  const isSelected = selectedStartNode === workflowName
  const justDraggedRef = useRef(false)

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (justDraggedRef.current) {
      justDraggedRef.current = false
      return
    }
    selectNode(null) // Deselect any regular node
    selectStartNode(workflowName)
    openNodeEditor()
  }

  // Handle node drag in free layout mode
  const handleDragStart = (e: React.MouseEvent) => {
    if (layoutMode !== 'free' || !onDrag) return
    e.stopPropagation()
    e.preventDefault()

    setIsDraggingNode(true)

    const startX = e.clientX
    const startY = e.clientY
    let hasMoved = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = (moveEvent.clientX - startX) / zoom
      const dy = (moveEvent.clientY - startY) / zoom
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        hasMoved = true
        onDrag(dx, dy)
      }
    }

    const handleMouseUp = () => {
      setIsDraggingNode(false)
      if (hasMoved) {
        justDraggedRef.current = true
      }
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
  }

  // Format variables for display
  const varEntries = Object.entries(variables).slice(0, 3)
  const hasMoreVars = Object.keys(variables).length > 3

  // Format interface inputs/outputs
  const inputs = workflowInterface.inputs || []
  const outputs = workflowInterface.outputs || []

  // Calculate dynamic height based on content
  const baseHeight = 50 // Header + padding
  const interfaceHeight = (inputs.length > 0 || outputs.length > 0) ? 18 : 0
  const variablesHeight = varEntries.length * 14 + (hasMoreVars ? 12 : 0)
  const totalHeight = Math.max(START_NODE_HEIGHT, baseHeight + interfaceHeight + variablesHeight + 10)

  return (
    <g
      className={`${styles.startNodeGroup} ${isSelected ? styles.selected : ''}`}
      transform={`translate(${x}, ${y})`}
      onClick={handleClick}
    >
      {/* Node card */}
      <rect
        className={styles.card}
        width={START_NODE_WIDTH}
        height={totalHeight}
        rx={8}
      />

      {/* Green color bar on left */}
      <rect className={styles.colorBar} width={4} height={totalHeight} rx={2} />

      {/* Green flag icon */}
      <text className={styles.flagIcon} x={16} y={24}>
        🚩
      </text>

      {/* Workflow name */}
      <text className={styles.name} x={38} y={24}>
        {workflowName}
      </text>

      {/* Interface info */}
      {(inputs.length > 0 || outputs.length > 0) && (
        <g transform="translate(12, 38)">
          <text className={styles.interfaceLabel} x={0} y={0}>
            {inputs.length > 0 && `In: ${inputs.join(', ')}`}
            {inputs.length > 0 && outputs.length > 0 && ' | '}
            {outputs.length > 0 && `Out: ${outputs.join(', ')}`}
          </text>
        </g>
      )}

      {/* Variables section */}
      {varEntries.length > 0 && (
        <g transform={`translate(12, ${baseHeight + interfaceHeight - 4})`}>
          {varEntries.map(([name, value], i) => (
            <text key={name} className={styles.variable} x={0} y={i * 14 + 10}>
              ${name} = {formatVariableValue(value)}
            </text>
          ))}
          {hasMoreVars && (
            <text className={styles.moreVars} x={0} y={varEntries.length * 14 + 10}>
              +{Object.keys(variables).length - 3} more...
            </text>
          )}
        </g>
      )}

      {/* Output port (connects to first real node) */}
      <circle
        className={styles.outputPort}
        cx={START_NODE_WIDTH}
        cy={30}
        r={6}
      />

      {/* Drag handle for free layout mode */}
      {layoutMode === 'free' && onDrag && (
        <rect
          className={styles.dragHandle}
          x={4}
          y={0}
          width={START_NODE_WIDTH - 8}
          height={40}
          fill="transparent"
          onMouseDown={handleDragStart}
        />
      )}
    </g>
  )
}

function formatVariableValue(value: unknown): string {
  if (value === null) return 'null'
  if (value === undefined) return 'undefined'
  if (typeof value === 'string') {
    if (value.length > 12) return `"${value.slice(0, 12)}..."`
    return `"${value}"`
  }
  if (typeof value === 'object') {
    return JSON.stringify(value).slice(0, 15) + '...'
  }
  return String(value)
}
