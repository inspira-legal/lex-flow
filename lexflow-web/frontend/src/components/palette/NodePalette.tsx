import { useState, useMemo, useRef } from 'react'
import { useWorkflowStore, useUiStore } from '../../store'
import type { OpcodeInterface } from '../../api/types'
import styles from './NodePalette.module.css'

const CATEGORIES = [
  { id: 'control', prefix: 'control_', label: 'Control', color: '#FF9500', icon: '⟳' },
  { id: 'data', prefix: 'data_', label: 'Data', color: '#4CAF50', icon: '📦' },
  { id: 'io', prefix: 'io_', label: 'I/O', color: '#22D3EE', icon: '📤' },
  { id: 'operator', prefix: 'operator_', label: 'Operators', color: '#9C27B0', icon: '⚡' },
  { id: 'list', prefix: 'list_', label: 'Lists', color: '#3B82F6', icon: '📋' },
  { id: 'dict', prefix: 'dict_', label: 'Dicts', color: '#F59E0B', icon: '📖' },
  { id: 'string', prefix: 'string_', label: 'Strings', color: '#F472B6', icon: '📝' },
  { id: 'math', prefix: 'math_', label: 'Math', color: '#8B5CF6', icon: '🔢' },
  { id: 'workflow', prefix: 'workflow_', label: 'Workflow', color: '#E91E63', icon: '🔗' },
]

export function NodePalette() {
  const { opcodes, tree } = useWorkflowStore()
  const { togglePalette, setDraggingVariable } = useUiStore()
  const [search, setSearch] = useState('')
  const [expandedCategory, setExpandedCategory] = useState<string | null>('variables')

  // Get variables from all workflows
  const allVariables = useMemo(() => {
    if (!tree) return []
    const vars: Array<{ name: string; value: unknown; workflowName: string }> = []
    for (const workflow of tree.workflows) {
      for (const [name, value] of Object.entries(workflow.variables)) {
        vars.push({ name, value, workflowName: workflow.name })
      }
    }
    return vars
  }, [tree])

  // Group opcodes by category
  const grouped = useMemo(() => {
    const groups: Record<string, OpcodeInterface[]> = {}
    for (const cat of CATEGORIES) {
      groups[cat.id] = []
    }
    groups['other'] = []

    for (const opcode of opcodes) {
      let matched = false
      for (const cat of CATEGORIES) {
        if (opcode.name.startsWith(cat.prefix)) {
          groups[cat.id].push(opcode)
          matched = true
          break
        }
      }
      if (!matched) {
        groups['other'].push(opcode)
      }
    }

    return groups
  }, [opcodes])

  // Filter by search
  const filteredOpcodes = useMemo(() => {
    if (!search) return null
    const lower = search.toLowerCase()
    return opcodes.filter(
      (op) =>
        op.name.toLowerCase().includes(lower) ||
        (op.description?.toLowerCase().includes(lower) ?? false)
    )
  }, [opcodes, search])

  return (
    <div className={styles.palette}>
      <div className={styles.header}>
        <h2>Node Palette</h2>
        <button className={styles.closeBtn} onClick={togglePalette}>
          ✕
        </button>
      </div>

      {/* Search */}
      <div className={styles.search}>
        <input
          type="text"
          placeholder="Search nodes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={styles.searchInput}
        />
      </div>

      <div className={styles.content}>
        {filteredOpcodes ? (
          // Search results
          <div className={styles.searchResults}>
            {filteredOpcodes.length === 0 ? (
              <p className={styles.noResults}>No nodes found</p>
            ) : (
              filteredOpcodes.map((opcode) => (
                <OpcodeItem key={opcode.name} opcode={opcode} />
              ))
            )}
          </div>
        ) : (
          // Category list
          <>
            {/* Variables category (always at top) */}
            <div className={styles.category}>
              <button
                className={styles.categoryHeader}
                onClick={() =>
                  setExpandedCategory(expandedCategory === 'variables' ? null : 'variables')
                }
                style={{ '--cat-color': '#22C55E' } as React.CSSProperties}
              >
                <span className={styles.categoryIcon}>$</span>
                <span className={styles.categoryLabel}>Variables</span>
                <span className={styles.categoryCount}>{allVariables.length}</span>
                <span className={styles.expandIcon}>
                  {expandedCategory === 'variables' ? '▼' : '▶'}
                </span>
              </button>

              {expandedCategory === 'variables' && (
                <div className={styles.categoryItems}>
                  {allVariables.length === 0 ? (
                    <div className={styles.emptyVariables}>
                      No variables defined. Add variables in the Start Node editor.
                    </div>
                  ) : (
                    allVariables.map((v) => (
                      <VariableItem
                        key={`${v.workflowName}-${v.name}`}
                        name={v.name}
                        value={v.value}
                        workflowName={v.workflowName}
                        onDragStart={setDraggingVariable}
                        onDragEnd={() => setDraggingVariable(null)}
                      />
                    ))
                  )}
                </div>
              )}
            </div>

            {CATEGORIES.map((cat) => (
              <div key={cat.id} className={styles.category}>
                <button
                  className={styles.categoryHeader}
                  onClick={() =>
                    setExpandedCategory(expandedCategory === cat.id ? null : cat.id)
                  }
                  style={{ '--cat-color': cat.color } as React.CSSProperties}
                >
                  <span className={styles.categoryIcon}>{cat.icon}</span>
                  <span className={styles.categoryLabel}>{cat.label}</span>
                  <span className={styles.categoryCount}>{grouped[cat.id].length}</span>
                  <span className={styles.expandIcon}>
                    {expandedCategory === cat.id ? '▼' : '▶'}
                  </span>
                </button>

                {expandedCategory === cat.id && (
                  <div className={styles.categoryItems}>
                    {grouped[cat.id].map((opcode) => (
                      <OpcodeItem key={opcode.name} opcode={opcode} />
                    ))}
                  </div>
                )}
              </div>
            ))}

            {/* Other category if not empty */}
            {grouped['other'].length > 0 && (
              <div className={styles.category}>
                <button
                  className={styles.categoryHeader}
                  onClick={() =>
                    setExpandedCategory(expandedCategory === 'other' ? null : 'other')
                  }
                  style={{ '--cat-color': '#64748B' } as React.CSSProperties}
                >
                  <span className={styles.categoryIcon}>⚙</span>
                  <span className={styles.categoryLabel}>Other</span>
                  <span className={styles.categoryCount}>{grouped['other'].length}</span>
                  <span className={styles.expandIcon}>
                    {expandedCategory === 'other' ? '▼' : '▶'}
                  </span>
                </button>

                {expandedCategory === 'other' && (
                  <div className={styles.categoryItems}>
                    {grouped['other'].map((opcode) => (
                      <OpcodeItem key={opcode.name} opcode={opcode} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      <div className={styles.footer}>
        <p className={styles.hint}>Click to view details • Drag to canvas to add node</p>
      </div>
    </div>
  )
}

function OpcodeItem({ opcode }: { opcode: OpcodeInterface }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { setDraggingOpcode, togglePalette } = useUiStore()
  const isDraggingRef = useRef(false)
  const startPosRef = useRef({ x: 0, y: 0 })

  const displayName = opcode.name
    .replace(/^(control_|data_|io_|operator_|list_|dict_|string_|math_|workflow_)/, '')
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')

  const handleMouseDown = (e: React.MouseEvent) => {
    // Record start position to detect drag vs click
    startPosRef.current = { x: e.clientX, y: e.clientY }
    isDraggingRef.current = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const dx = Math.abs(moveEvent.clientX - startPosRef.current.x)
      const dy = Math.abs(moveEvent.clientY - startPosRef.current.y)

      // Start drag if moved more than 5 pixels
      if (!isDraggingRef.current && (dx > 5 || dy > 5)) {
        isDraggingRef.current = true
        setDraggingOpcode(opcode)
        // Close palette so we can drop on canvas
        togglePalette()
      }
    }

    const handleMouseUp = () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
  }

  return (
    <div className={styles.opcodeItem}>
      <button
        className={styles.opcodeHeader}
        onMouseDown={handleMouseDown}
        onClick={() => {
          // Only expand if not dragging
          if (!isDraggingRef.current) {
            setIsExpanded(!isExpanded)
          }
        }}
      >
        <span className={styles.opcodeName}>{displayName}</span>
        <span className={styles.opcodeRaw}>{opcode.name}</span>
      </button>

      {isExpanded && (
        <div className={styles.opcodeDetails}>
          {opcode.description && (
            <p className={styles.opcodeDesc}>{opcode.description}</p>
          )}
          {opcode.parameters.length > 0 && (
            <div className={styles.opcodeParams}>
              <span className={styles.paramsLabel}>Parameters:</span>
              {opcode.parameters.map((param) => (
                <span key={param.name} className={styles.param}>
                  {param.name}
                  {!param.required && '?'}
                  <span className={styles.paramType}>: {param.type}</span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

interface VariableItemProps {
  name: string
  value: unknown
  workflowName: string
  onDragStart: (v: { name: string; workflowName: string; fromX: number; fromY: number; toX: number; toY: number }) => void
  onDragEnd: () => void
}

function VariableItem({ name, value, workflowName, onDragStart, onDragEnd }: VariableItemProps) {
  const { togglePalette } = useUiStore()
  const isDraggingRef = useRef(false)
  const startPosRef = useRef({ x: 0, y: 0 })
  const itemRef = useRef<HTMLDivElement>(null)

  const displayValue = formatVariableValue(value)

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault() // Prevent text selection
    startPosRef.current = { x: e.clientX, y: e.clientY }
    isDraggingRef.current = false

    const handleMouseMove = (moveEvent: MouseEvent) => {
      moveEvent.preventDefault() // Prevent text selection during drag
      const dx = Math.abs(moveEvent.clientX - startPosRef.current.x)
      const dy = Math.abs(moveEvent.clientY - startPosRef.current.y)

      if (!isDraggingRef.current && (dx > 5 || dy > 5)) {
        isDraggingRef.current = true
        // For variable drag, we only need cursor position (no wire from source)
        onDragStart({
          name,
          workflowName,
          fromX: 0, // Not used - variable drag only shows ghost at cursor
          fromY: 0,
          toX: 0, // Will be updated by canvas
          toY: 0,
        })
        togglePalette()
      }
    }

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        onDragEnd()
      }
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
  }

  return (
    <div ref={itemRef} className={styles.variableItem} onMouseDown={handleMouseDown}>
      <span className={styles.variableName}>${name}</span>
      <span className={styles.variableValue}>{displayValue}</span>
      {workflowName !== 'main' && (
        <span className={styles.variableWorkflow}>({workflowName})</span>
      )}
    </div>
  )
}

function formatVariableValue(value: unknown): string {
  if (value === null) return 'null'
  if (value === undefined) return 'undefined'
  if (typeof value === 'string') {
    if (value.length > 15) return `"${value.slice(0, 15)}..."`
    return `"${value}"`
  }
  if (typeof value === 'object') {
    const str = JSON.stringify(value)
    if (str.length > 15) return str.slice(0, 15) + '...'
    return str
  }
  return String(value)
}
