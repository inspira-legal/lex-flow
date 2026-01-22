import type { ReactElement } from 'react'
import { useWorkflowStore, useUiStore } from '../../store'
import type { SelectedReporter } from '../../store/uiStore'
import type { TreeNode, FormattedValue, NodeType } from '../../api/types'
import styles from './WorkflowNode.module.css'

interface WorkflowNodeProps {
  node: TreeNode
  x: number
  y: number
}

const NODE_COLORS: Record<NodeType | string, string> = {
  control_flow: '#FF9500',
  data: '#4CAF50',
  io: '#22D3EE',
  operator: '#9C27B0',
  workflow_op: '#E91E63',
  opcode: '#64748B',
}

const NODE_ICONS: Record<string, string> = {
  control_flow: '⟳',
  data: '📦',
  io: '📤',
  operator: '⚡',
  workflow_op: '🔗',
  opcode: '⚙',
}

const REPORTER_COLORS: Record<string, string> = {
  data: '#4CAF50',
  operator: '#9C27B0',
  io: '#22D3EE',
  workflow: '#E91E63',
  default: '#64748B',
}

export function WorkflowNode({ node, x, y }: WorkflowNodeProps) {
  const { selectedNodeId, selectNode } = useWorkflowStore()
  const { openNodeEditor, nodeStatus, searchResults, selectReporter, selectedReporter } = useUiStore()

  const color = NODE_COLORS[node.type] || NODE_COLORS.opcode
  const icon = NODE_ICONS[node.type] || NODE_ICONS.opcode
  const isSelected = selectedNodeId === node.id && !selectedReporter
  const isSearchMatch = searchResults.includes(node.id)
  const status = nodeStatus[node.id] || 'idle'

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    selectNode(node.id)
    selectReporter(null) // Clear any selected reporter
    openNodeEditor()
  }

  // Extract display name from opcode
  const displayName = formatOpcodeName(node.opcode)

  // Separate reporter inputs from regular inputs
  const reporterInputs: Array<{ key: string; value: FormattedValue }> = []
  const regularInputs: Array<{ key: string; value: FormattedValue }> = []

  for (const [key, value] of Object.entries(node.inputs)) {
    if (value.type === 'reporter' && value.opcode) {
      reporterInputs.push({ key, value })
    } else {
      regularInputs.push({ key, value })
    }
  }

  // Get preview of regular inputs
  const inputPreview = regularInputs
    .slice(0, 2)
    .map(({ key, value }) => {
      const formatted = formatValueShort(value)
      return formatted ? { key, formatted } : null
    })
    .filter(Boolean) as Array<{ key: string; formatted: string }>

  // Calculate heights
  const baseHeight = 60 + inputPreview.length * 18
  const reporterSectionHeight = reporterInputs.reduce((acc, { value }) => {
    return acc + calculateReporterTotalHeight(value) + 4
  }, 0)
  const totalHeight = baseHeight + reporterSectionHeight

  return (
    <g
      className={`${styles.nodeGroup} ${isSelected ? styles.selected : ''} ${isSearchMatch ? styles.searchMatch : ''} ${styles[status]}`}
      transform={`translate(${x}, ${y})`}
      onClick={handleClick}
    >
      {/* Node card */}
      <rect
        className={styles.card}
        width={180}
        height={totalHeight}
        rx={8}
        style={{ '--node-color': color } as React.CSSProperties}
      />

      {/* Color bar on left */}
      <rect className={styles.colorBar} width={4} height={totalHeight} rx={2} fill={color} />

      {/* Icon */}
      <text className={styles.icon} x={16} y={24}>
        {icon}
      </text>

      {/* Node name */}
      <text className={styles.name} x={36} y={24}>
        {displayName}
      </text>

      {/* Node ID (dimmed) */}
      <text className={styles.id} x={36} y={40}>
        {node.id}
      </text>

      {/* Regular input preview */}
      {inputPreview.map((input, i) => (
        <g key={input.key}>
          <text className={styles.inputKey} x={12} y={56 + i * 18}>
            {input.key}:
          </text>
          <text className={styles.input} x={12 + (input.key.length + 1) * 6} y={56 + i * 18}>
            {input.formatted}
          </text>
        </g>
      ))}

      {/* Nested reporter blocks */}
      {reporterInputs.length > 0 && (
        <g transform={`translate(8, ${baseHeight - 4})`}>
          {renderNestedReporters(reporterInputs, 0, true, node.id, [], selectReporter, selectedReporter)}
        </g>
      )}

      {/* Connection points */}
      <circle className={styles.inputPort} cx={0} cy={30} r={5} />
      <circle className={styles.outputPort} cx={180} cy={30} r={5} />

      {/* Status indicator */}
      {status !== 'idle' && (
        <circle
          className={styles.statusDot}
          cx={170}
          cy={10}
          r={6}
          fill={status === 'running' ? '#FACC15' : status === 'success' ? '#34D399' : '#F87171'}
        />
      )}
    </g>
  )
}

// Render nested reporters recursively
function renderNestedReporters(
  inputs: Array<{ key: string; value: FormattedValue }>,
  depth: number = 0,
  showLabels: boolean = true,
  parentNodeId: string,
  parentPath: string[],
  selectReporter: (reporter: SelectedReporter | null) => void,
  selectedReporter: SelectedReporter | null
): ReactElement {
  let yOffset = 0

  return (
    <g>
      {inputs.map(({ key, value }, index) => {
        const reporterColor = getReporterColor(value.opcode || '')
        const reporterName = formatOpcodeName(value.opcode || '')
        const width = 164 - depth * 8
        const currentPath = [...parentPath, key]

        // Check if this reporter is selected
        const isSelected =
          selectedReporter &&
          selectedReporter.parentNodeId === parentNodeId &&
          selectedReporter.inputPath.join('.') === currentPath.join('.')

        const handleReporterClick = (e: React.MouseEvent) => {
          e.stopPropagation()
          selectReporter({
            parentNodeId,
            inputPath: currentPath,
            opcode: value.opcode || '',
            inputs: value.inputs || {},
          })
        }

        // Separate reporter's inputs into reporters and regular values
        const nestedReporters: Array<{ key: string; value: FormattedValue }> = []
        const regularInputs: Array<{ key: string; formatted: string }> = []

        if (value.inputs) {
          for (const [nestedKey, nestedValue] of Object.entries(value.inputs)) {
            if (nestedValue.type === 'reporter' && nestedValue.opcode) {
              nestedReporters.push({ key: nestedKey, value: nestedValue })
            } else {
              const formatted = formatValueShort(nestedValue)
              if (formatted) {
                regularInputs.push({ key: nestedKey, formatted })
              }
            }
          }
        }

        // Calculate heights
        const labelHeight = showLabels ? 14 : 0
        const headerHeight = 22
        const regularInputsHeight = regularInputs.length * 14
        const nestedLabelHeight = nestedReporters.length > 0 ? nestedReporters.length * 14 : 0
        const nestedReportersHeight = nestedReporters.reduce((acc, { value: v }) => {
          return acc + calculateReporterTotalHeight(v) + 4
        }, 0)
        const totalPillHeight = headerHeight + regularInputsHeight + nestedLabelHeight + nestedReportersHeight + 4

        const currentY = yOffset
        yOffset += labelHeight + totalPillHeight + 4

        return (
          <g key={`${key}-${index}`} transform={`translate(0, ${currentY})`}>
            {/* Input slot label on parent level */}
            {showLabels && (
              <text className={styles.reporterLabel} x={0} y={10}>
                {key}
              </text>
            )}

            {/* Reporter pill */}
            <g
              transform={`translate(0, ${labelHeight})`}
              className={`${styles.reporterClickable} ${isSelected ? styles.reporterSelected : ''}`}
              onClick={handleReporterClick}
            >
              {/* Reporter pill background */}
              <rect
                className={styles.reporterPill}
                x={0}
                y={0}
                width={width}
                height={totalPillHeight}
                rx={11}
                style={{ '--reporter-color': reporterColor } as React.CSSProperties}
              />

              {/* Color dot */}
              <circle cx={10} cy={11} r={4} fill={reporterColor} />

              {/* Reporter name */}
              <text className={styles.reporterName} x={18} y={15}>
                {reporterName}
              </text>

              {/* Regular inputs (literals, variables) - split key/value */}
              {regularInputs.map((input, i) => (
                <g key={input.key}>
                  <text className={styles.reporterInputKey} x={18} y={headerHeight + 10 + i * 14}>
                    {input.key}:
                  </text>
                  <text
                    className={styles.reporterInputValue}
                    x={18 + (input.key.length + 1) * 5}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.formatted}
                  </text>
                </g>
              ))}

              {/* Nested reporter labels and reporters */}
              {nestedReporters.length > 0 && (
                <g transform={`translate(6, ${headerHeight + regularInputsHeight})`}>
                  {renderNestedReporterWithLabels(
                    nestedReporters,
                    depth + 1,
                    parentNodeId,
                    currentPath,
                    selectReporter,
                    selectedReporter
                  )}
                </g>
              )}
            </g>
          </g>
        )
      })}
    </g>
  )
}

// Render nested reporters with their labels inside parent pill
function renderNestedReporterWithLabels(
  inputs: Array<{ key: string; value: FormattedValue }>,
  depth: number,
  parentNodeId: string,
  parentPath: string[],
  selectReporter: (reporter: SelectedReporter | null) => void,
  selectedReporter: SelectedReporter | null
): ReactElement {
  let yOffset = 0

  return (
    <g>
      {inputs.map(({ key, value }, index) => {
        const reporterColor = getReporterColor(value.opcode || '')
        const reporterName = formatOpcodeName(value.opcode || '')
        const width = 164 - depth * 8 - 6
        const currentPath = [...parentPath, key]

        // Check if this reporter is selected
        const isSelected =
          selectedReporter &&
          selectedReporter.parentNodeId === parentNodeId &&
          selectedReporter.inputPath.join('.') === currentPath.join('.')

        const handleReporterClick = (e: React.MouseEvent) => {
          e.stopPropagation()
          selectReporter({
            parentNodeId,
            inputPath: currentPath,
            opcode: value.opcode || '',
            inputs: value.inputs || {},
          })
        }

        // Get nested content
        const nestedReporters: Array<{ key: string; value: FormattedValue }> = []
        const regularInputs: Array<{ key: string; formatted: string }> = []

        if (value.inputs) {
          for (const [nestedKey, nestedValue] of Object.entries(value.inputs)) {
            if (nestedValue.type === 'reporter' && nestedValue.opcode) {
              nestedReporters.push({ key: nestedKey, value: nestedValue })
            } else {
              const formatted = formatValueShort(nestedValue)
              if (formatted) {
                regularInputs.push({ key: nestedKey, formatted })
              }
            }
          }
        }

        const labelHeight = 14
        const headerHeight = 22
        const regularInputsHeight = regularInputs.length * 14
        const nestedLabelHeight = nestedReporters.length > 0 ? nestedReporters.length * 14 : 0
        const nestedReportersHeight = nestedReporters.reduce((acc, { value: v }) => {
          return acc + calculateReporterTotalHeight(v) + 4
        }, 0)
        const pillHeight = headerHeight + regularInputsHeight + nestedLabelHeight + nestedReportersHeight + 4

        const currentY = yOffset
        yOffset += labelHeight + pillHeight + 4

        return (
          <g key={`${key}-${index}`} transform={`translate(0, ${currentY})`}>
            {/* Label */}
            <text className={styles.reporterNestedLabel} x={0} y={10}>
              {key}
            </text>

            {/* Nested pill */}
            <g
              transform={`translate(0, ${labelHeight})`}
              className={`${styles.reporterClickable} ${isSelected ? styles.reporterSelected : ''}`}
              onClick={handleReporterClick}
            >
              <rect
                className={styles.reporterPill}
                x={0}
                y={0}
                width={width}
                height={pillHeight}
                rx={11}
                style={{ '--reporter-color': reporterColor } as React.CSSProperties}
              />

              <circle cx={10} cy={11} r={4} fill={reporterColor} />

              <text className={styles.reporterName} x={18} y={15}>
                {reporterName}
              </text>

              {regularInputs.map((input, i) => (
                <g key={input.key}>
                  <text className={styles.reporterInputKey} x={18} y={headerHeight + 10 + i * 14}>
                    {input.key}:
                  </text>
                  <text
                    className={styles.reporterInputValue}
                    x={18 + (input.key.length + 1) * 5}
                    y={headerHeight + 10 + i * 14}
                  >
                    {input.formatted}
                  </text>
                </g>
              ))}

              {nestedReporters.length > 0 && (
                <g transform={`translate(6, ${headerHeight + regularInputsHeight})`}>
                  {renderNestedReporterWithLabels(
                    nestedReporters,
                    depth + 1,
                    parentNodeId,
                    currentPath,
                    selectReporter,
                    selectedReporter
                  )}
                </g>
              )}
            </g>
          </g>
        )
      })}
    </g>
  )
}

// Calculate total height of a reporter pill (including its content and label)
function calculateReporterTotalHeight(value: FormattedValue, includeLabel: boolean = true): number {
  if (value.type !== 'reporter') return 0

  const labelHeight = includeLabel ? 14 : 0
  const headerHeight = 22

  // Count regular inputs and nested reporters
  let regularInputsCount = 0
  let nestedReportersCount = 0
  let nestedReportersHeight = 0

  if (value.inputs) {
    for (const nestedValue of Object.values(value.inputs)) {
      if (nestedValue.type === 'reporter' && nestedValue.opcode) {
        nestedReportersCount++
        nestedReportersHeight += calculateReporterTotalHeight(nestedValue, true) + 4
      } else {
        const formatted = formatValueShort(nestedValue)
        if (formatted) regularInputsCount++
      }
    }
  }

  const nestedLabelHeight = nestedReportersCount * 14
  return labelHeight + headerHeight + regularInputsCount * 14 + nestedLabelHeight + nestedReportersHeight + 4
}

function getReporterColor(opcode: string): string {
  if (opcode.startsWith('data_')) return REPORTER_COLORS.data
  if (opcode.startsWith('operator_')) return REPORTER_COLORS.operator
  if (opcode.startsWith('io_')) return REPORTER_COLORS.io
  if (opcode.startsWith('workflow_')) return REPORTER_COLORS.workflow
  return REPORTER_COLORS.default
}

function formatOpcodeName(opcode: string): string {
  return opcode
    .replace(/^(control_|data_|io_|operator_|workflow_)/, '')
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
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
      return `[${formatOpcodeName(value.opcode || '')}]`
    case 'workflow_call':
      return `→ ${value.name}`
    default:
      return ''
  }
}
