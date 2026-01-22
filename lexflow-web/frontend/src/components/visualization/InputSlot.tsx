import { useUiStore, useWorkflowStore } from '../../store'
import type { FormattedValue, OpcodeParameter } from '../../api/types'
import { checkTypeCompatibility, getCompatibilityColor } from '../../utils/typeCompatibility'
import styles from './WorkflowNode.module.css'

interface InputSlotProps {
  nodeId: string
  inputKey: string
  value: FormattedValue
  paramInfo?: OpcodeParameter
  x: number
  y: number
  width: number
}

export function InputSlot({ nodeId, inputKey, value, paramInfo, x, y, width }: InputSlotProps) {
  const { draggingOrphan, setDraggingOrphan, draggingVariable, setDraggingVariable } = useUiStore()
  const { convertOrphanToReporter, updateNodeInput } = useWorkflowStore()

  // Format the display value
  const displayValue = formatValueShort(value)

  // Check if we're a valid drop target for either orphan or variable
  const isOrphanDropTarget = draggingOrphan !== null
  const isVariableDropTarget = draggingVariable !== null
  const isDropTarget = isOrphanDropTarget || isVariableDropTarget

  // Calculate type compatibility if dragging orphan (variables are untyped, so neutral)
  const compatibility = isOrphanDropTarget
    ? checkTypeCompatibility(draggingOrphan.returnType, paramInfo?.type)
    : isVariableDropTarget
      ? null // Neutral for variables (no type checking)
      : null

  const handleMouseUp = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (draggingOrphan) {
      // Convert the orphan to a reporter for this input
      convertOrphanToReporter(draggingOrphan.nodeId, nodeId, inputKey, compatibility)
      setDraggingOrphan(null)
    } else if (draggingVariable) {
      // Update the input to use the variable reference
      updateNodeInput(nodeId, inputKey, `$${draggingVariable.name}`)
      setDraggingVariable(null)
    }
  }

  const handleMouseEnter = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  // Determine slot styling based on drop state
  let slotClass = styles.inputSlot
  let bgClass = styles.inputSlotBg
  if (isDropTarget) {
    bgClass += ` ${styles.dropTarget}`
    if (isVariableDropTarget) {
      // Variable drops always show as compatible (green highlight)
      bgClass += ` ${styles.compatible}`
    } else if (compatibility === true) {
      bgClass += ` ${styles.compatible}`
    } else if (compatibility === false) {
      bgClass += ` ${styles.incompatible}`
    }
  }

  // Use green color for variable drops
  const slotColor = isVariableDropTarget ? '#22C55E' : getCompatibilityColor(compatibility)

  const slotHeight = 16

  return (
    <g
      className={slotClass}
      transform={`translate(${x}, ${y})`}
      onMouseUp={handleMouseUp}
      onMouseEnter={handleMouseEnter}
    >
      {/* Background rect for drop target */}
      <rect
        className={bgClass}
        x={0}
        y={0}
        width={width}
        height={slotHeight}
        rx={3}
        style={
          isDropTarget
            ? ({ '--slot-color': slotColor } as React.CSSProperties)
            : undefined
        }
      />

      {/* Key label */}
      <text className={styles.inputKey} x={4} y={11}>
        {inputKey}:
      </text>

      {/* Value */}
      <text className={styles.input} x={4 + (inputKey.length + 1) * 6} y={11}>
        {displayValue}
      </text>

      {/* Type hint when dragging */}
      {isDropTarget && paramInfo?.type && (
        <text className={styles.typeHint} x={width - 4} y={11} textAnchor="end">
          {paramInfo.type}
        </text>
      )}
    </g>
  )
}

function formatValueShort(value: FormattedValue): string {
  switch (value.type) {
    case 'literal':
      const v = value.value
      if (typeof v === 'string') return `"${v.length > 10 ? v.slice(0, 10) + '...' : v}"`
      return String(v)
    case 'variable':
      return `$${value.name}`
    case 'reporter':
      return `[reporter]`
    case 'workflow_call':
      return `-> ${value.name}`
    default:
      return ''
  }
}
