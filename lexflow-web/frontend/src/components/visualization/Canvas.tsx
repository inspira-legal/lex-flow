import { useRef, useState, useCallback, useEffect, useMemo } from 'react'
import { useUiStore, useWorkflowStore } from '../../store'
import { WorkflowNode } from './WorkflowNode'
import { Connection } from './Connection'
import { MiniMap } from './MiniMap'
import { NodeSearch } from './NodeSearch'
import { WorkflowGroup } from './WorkflowGroup'
import type { TreeNode, WorkflowNode as WorkflowNodeType, FormattedValue } from '../../api/types'
import styles from './Canvas.module.css'

interface LayoutNode {
  node: TreeNode
  x: number
  y: number
  width: number
  height: number
}

interface LayoutConnection {
  from: string
  to: string
  x1: number
  y1: number
  x2: number
  y2: number
  color: string
  label?: string
}

interface LayoutWorkflowGroup {
  name: string
  x: number
  y: number
  width: number
  height: number
  isMain: boolean
}

interface FullLayout {
  nodes: LayoutNode[]
  connections: LayoutConnection[]
  groups: LayoutWorkflowGroup[]
}

const NODE_WIDTH = 180
const NODE_HEIGHT = 80
const H_GAP = 60
const V_GAP = 40
const WORKFLOW_GAP = 80

// Calculate additional height needed for nested reporters in a node
export function calculateNodeHeight(inputs: Record<string, FormattedValue>): number {
  let baseHeight = NODE_HEIGHT
  let reporterHeight = 0

  for (const [_key, value] of Object.entries(inputs)) {
    if (value.type === 'reporter' && value.opcode) {
      // Each reporter adds height, plus nested reporters
      reporterHeight += calculateReporterTotalHeight(value) + 4
    }
  }

  // Add some base height for non-reporter inputs preview
  const nonReporterInputs = Object.values(inputs).filter((v) => v.type !== 'reporter').length
  baseHeight += Math.min(nonReporterInputs, 2) * 18

  return baseHeight + reporterHeight
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
      return `→ ${value.name}`
    default:
      return ''
  }
}

export function Canvas() {
  const { zoom, panX, panY, setZoom, setPan, resetView, workflowPositions, setWorkflowPosition, isDraggingWorkflow } = useUiStore()
  const { tree, parseError, selectNode } = useWorkflowStore()

  const svgRef = useRef<SVGSVGElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [canvasSize, setCanvasSize] = useState({ width: 800, height: 600 })

  // Track canvas size for minimap viewport calculation
  useEffect(() => {
    const updateSize = () => {
      if (svgRef.current) {
        setCanvasSize({
          width: svgRef.current.clientWidth,
          height: svgRef.current.clientHeight,
        })
      }
    }

    updateSize()
    window.addEventListener('resize', updateSize)
    return () => window.removeEventListener('resize', updateSize)
  }, [])

  // Handle zoom
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        const delta = e.deltaY > 0 ? -0.1 : 0.1
        setZoom(zoom + delta)
      }
    },
    [zoom, setZoom]
  )

  // Handle pan
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (isDraggingWorkflow) return
      if (e.target === svgRef.current || (e.target as Element).classList.contains(styles.background)) {
        setIsDragging(true)
        setDragStart({ x: e.clientX - panX, y: e.clientY - panY })
        selectNode(null)
      }
    },
    [panX, panY, selectNode, isDraggingWorkflow]
  )

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isDraggingWorkflow) return
      if (isDragging) {
        setPan(e.clientX - dragStart.x, e.clientY - dragStart.y)
      }
    },
    [isDragging, dragStart, setPan, isDraggingWorkflow]
  )

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  // Handle minimap navigation
  const handleMinimapNavigate = useCallback(
    (newPanX: number, newPanY: number) => {
      setPan(newPanX, newPanY)
    },
    [setPan]
  )

  // Layout all workflows
  const { nodes: layoutNodes, connections, groups } = tree
    ? layoutAllWorkflows(tree.workflows, workflowPositions)
    : { nodes: [], connections: [], groups: [] }

  // Calculate canvas bounds (include group padding)
  const groupPadding = 24
  const labelHeight = 28
  const bounds =
    groups.length > 0
      ? groups.reduce(
          (acc, g) => ({
            minX: Math.min(acc.minX, g.x - groupPadding),
            minY: Math.min(acc.minY, g.y - groupPadding - labelHeight),
            maxX: Math.max(acc.maxX, g.x + g.width + groupPadding),
            maxY: Math.max(acc.maxY, g.y + g.height + groupPadding),
          }),
          { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }
        )
      : { minX: 0, minY: 0, maxX: 800, maxY: 600 }

  // Calculate initial center only when tree changes (not when dragging workflows)
  const { centerX, centerY } = useMemo(() => {
    if (!tree) return { centerX: 400, centerY: 300 }

    // Calculate bounds based on default layout (no position offsets)
    const defaultLayout = layoutAllWorkflows(tree.workflows, {})
    const defaultBounds = defaultLayout.groups.reduce(
      (acc, g) => ({
        minX: Math.min(acc.minX, g.x - groupPadding),
        minY: Math.min(acc.minY, g.y - groupPadding - labelHeight),
        maxX: Math.max(acc.maxX, g.x + g.width + groupPadding),
        maxY: Math.max(acc.maxY, g.y + g.height + groupPadding),
      }),
      { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity }
    )

    return {
      centerX: (defaultBounds.maxX + defaultBounds.minX) / 2,
      centerY: (defaultBounds.maxY + defaultBounds.minY) / 2,
    }
  }, [tree])

  return (
    <div className={styles.canvas}>
      {/* Node Search */}
      <NodeSearch />

      {/* Zoom Controls */}
      <div className={styles.zoomControls}>
        <button onClick={() => setZoom(zoom - 0.1)} title="Zoom Out">
          −
        </button>
        <span className={styles.zoomLevel}>{Math.round(zoom * 100)}%</span>
        <button onClick={() => setZoom(zoom + 0.1)} title="Zoom In">
          +
        </button>
        <button onClick={resetView} title="Reset View">
          ⌂
        </button>
      </div>

      {/* Mini-map */}
      {tree && (
        <MiniMap
          workflows={tree.workflows}
          bounds={bounds}
          zoom={zoom}
          panX={panX}
          panY={panY}
          canvasWidth={canvasSize.width}
          canvasHeight={canvasSize.height}
          onNavigate={handleMinimapNavigate}
        />
      )}

      {/* Error display */}
      {parseError && (
        <div className={styles.errorOverlay}>
          <span className={styles.errorIcon}>⚠</span>
          <span>{parseError}</span>
        </div>
      )}

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        className={styles.svg}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      >
        {/* Background for click handling */}
        <rect className={styles.background} width="100%" height="100%" fill="transparent" />

        {/* Main group with pan/zoom transform */}
        <g
          transform={`translate(${panX + (svgRef.current?.clientWidth || 800) / 2 - centerX * zoom}, ${panY + (svgRef.current?.clientHeight || 600) / 2 - centerY * zoom}) scale(${zoom})`}
        >
          {/* Workflow groups (render first, as background) */}
          {groups.map((group) => (
            <WorkflowGroup
              key={group.name}
              name={group.name}
              x={group.x}
              y={group.y}
              width={group.width}
              height={group.height}
              isMain={group.isMain}
              zoom={zoom}
              onDrag={(dx, dy) => {
                // Read current position from store to avoid stale closure
                const currentOffset = useUiStore.getState().workflowPositions[group.name] || { x: 0, y: 0 }
                setWorkflowPosition(group.name, currentOffset.x + dx, currentOffset.y + dy)
              }}
            />
          ))}

          {/* Connections (render second, below nodes) */}
          {connections.map((conn, i) => (
            <Connection
              key={`${conn.from}-${conn.to}-${i}`}
              x1={conn.x1}
              y1={conn.y1}
              x2={conn.x2}
              y2={conn.y2}
              color={conn.color}
              label={conn.label}
            />
          ))}

          {/* Nodes */}
          {layoutNodes.map((ln) => (
            <WorkflowNode key={ln.node.id} node={ln.node} x={ln.x} y={ln.y} />
          ))}
        </g>
      </svg>

      {/* Empty state */}
      {!parseError && !tree && (
        <div className={styles.emptyState}>
          <h2>No Workflow</h2>
          <p>Edit YAML in the editor or load an example</p>
        </div>
      )}
    </div>
  )
}

// Layout all workflows with custom position offsets
function layoutAllWorkflows(
  workflows: WorkflowNodeType[],
  positionOffsets: Record<string, { x: number; y: number }>
): FullLayout {
  const allNodes: LayoutNode[] = []
  const allConnections: LayoutConnection[] = []
  const groups: LayoutWorkflowGroup[] = []

  // First pass: calculate default positions (stacked vertically)
  let defaultY = 0
  const defaultPositions: Record<string, { x: number; y: number }> = {}

  for (const workflow of workflows) {
    defaultPositions[workflow.name] = { x: 0, y: defaultY }
    // Estimate height for default stacking
    const estimatedHeight = Math.max(workflow.children.length * (NODE_HEIGHT + V_GAP), NODE_HEIGHT + 100)
    defaultY += estimatedHeight + WORKFLOW_GAP
  }

  // Second pass: layout each workflow at default position + offset
  for (const workflow of workflows) {
    const defaultPos = defaultPositions[workflow.name]
    const offset = positionOffsets[workflow.name] || { x: 0, y: 0 }
    const pos = { x: defaultPos.x + offset.x, y: defaultPos.y + offset.y }

    const { nodes, connections, bounds } = layoutSingleWorkflow(workflow, pos.x, pos.y)

    allNodes.push(...nodes)
    allConnections.push(...connections)

    // Add workflow group
    groups.push({
      name: workflow.name,
      x: bounds.minX,
      y: bounds.minY,
      width: bounds.maxX - bounds.minX,
      height: bounds.maxY - bounds.minY,
      isMain: workflow.name === 'main',
    })
  }

  return { nodes: allNodes, connections: allConnections, groups }
}

// Layout a single workflow starting at given offset
function layoutSingleWorkflow(
  workflow: WorkflowNodeType,
  offsetX: number,
  offsetY: number
): {
  nodes: LayoutNode[]
  connections: LayoutConnection[]
  bounds: { minX: number; minY: number; maxX: number; maxY: number }
} {
  const layoutNodes: LayoutNode[] = []
  const connections: LayoutConnection[] = []
  const nodePositions = new Map<string, { x: number; y: number; height: number }>()

  // Track bounds
  let minX = Infinity,
    minY = Infinity,
    maxX = -Infinity,
    maxY = -Infinity

  function updateBounds(x: number, y: number, width: number, height: number) {
    minX = Math.min(minX, x)
    minY = Math.min(minY, y)
    maxX = Math.max(maxX, x + width)
    maxY = Math.max(maxY, y + height)
  }

  // Layout main flow
  function layoutNode(node: TreeNode, x: number, y: number): number {
    // Calculate height including nested reporters
    const height = calculateNodeHeight(node.inputs)

    layoutNodes.push({
      node,
      x,
      y,
      width: NODE_WIDTH,
      height,
    })
    nodePositions.set(node.id, { x, y, height })
    updateBounds(x, y, NODE_WIDTH, height)

    let nextX = x + NODE_WIDTH + H_GAP

    // Layout branch children
    if (node.children.length > 0) {
      let branchOffset = y + height + V_GAP

      for (const branch of node.children) {
        const branchColor = getBranchColor(branch.name)

        // Layout branch nodes
        let branchX = x + NODE_WIDTH + H_GAP
        let prevNodeId = node.id
        let prevX = x + NODE_WIDTH
        let prevY = y + height / 2

        for (const childNode of branch.children) {
          const childHeight = calculateNodeHeight(childNode.inputs)

          layoutNodes.push({
            node: childNode,
            x: branchX,
            y: branchOffset,
            width: NODE_WIDTH,
            height: childHeight,
          })
          nodePositions.set(childNode.id, { x: branchX, y: branchOffset, height: childHeight })
          updateBounds(branchX, branchOffset, NODE_WIDTH, childHeight)

          // Connection
          connections.push({
            from: prevNodeId,
            to: childNode.id,
            x1: prevX,
            y1: prevY,
            x2: branchX,
            y2: branchOffset + childHeight / 2,
            color: branchColor,
            label: prevNodeId === node.id ? branch.name : undefined,
          })

          prevNodeId = childNode.id
          prevX = branchX + NODE_WIDTH
          prevY = branchOffset + childHeight / 2
          branchX += NODE_WIDTH + H_GAP

          // Recursively layout nested branches
          if (childNode.children.length > 0) {
            branchX = Math.max(branchX, layoutBranches(childNode, branchX, branchOffset))
          }
        }

        nextX = Math.max(nextX, branchX)
        branchOffset += NODE_HEIGHT + V_GAP * 2
      }
    }

    return nextX
  }

  function layoutBranches(node: TreeNode, startX: number, startY: number): number {
    let maxX = startX
    let branchY = startY + NODE_HEIGHT + V_GAP

    for (const branch of node.children) {
      const branchColor = getBranchColor(branch.name)
      let branchX = startX

      let prevNodeId = node.id
      let prevX = nodePositions.get(node.id)?.x || startX
      prevX += NODE_WIDTH
      let prevY = nodePositions.get(node.id)?.y || startY
      prevY += NODE_HEIGHT / 2

      for (const childNode of branch.children) {
        const childHeight = calculateNodeHeight(childNode.inputs)

        layoutNodes.push({
          node: childNode,
          x: branchX,
          y: branchY,
          width: NODE_WIDTH,
          height: childHeight,
        })
        nodePositions.set(childNode.id, { x: branchX, y: branchY, height: childHeight })
        updateBounds(branchX, branchY, NODE_WIDTH, childHeight)

        connections.push({
          from: prevNodeId,
          to: childNode.id,
          x1: prevX,
          y1: prevY,
          x2: branchX,
          y2: branchY + childHeight / 2,
          color: branchColor,
          label: prevNodeId === node.id ? branch.name : undefined,
        })

        prevNodeId = childNode.id
        prevX = branchX + NODE_WIDTH
        prevY = branchY + childHeight / 2
        branchX += NODE_WIDTH + H_GAP
      }

      maxX = Math.max(maxX, branchX)
      branchY += NODE_HEIGHT + V_GAP
    }

    return maxX
  }

  // Layout all nodes in the workflow
  let x = offsetX
  let prevNode: TreeNode | null = null

  for (const node of workflow.children) {
    const y = offsetY
    const nextX = layoutNode(node, x, y)

    // Connect sequential nodes
    if (prevNode) {
      const prevPos = nodePositions.get(prevNode.id)!
      const currPos = nodePositions.get(node.id)!
      connections.push({
        from: prevNode.id,
        to: node.id,
        x1: prevPos.x + NODE_WIDTH,
        y1: prevPos.y + NODE_HEIGHT / 2,
        x2: currPos.x,
        y2: currPos.y + NODE_HEIGHT / 2,
        color: '#475569',
      })
    }

    prevNode = node
    x = nextX
  }

  // Handle empty workflow
  if (minX === Infinity) {
    minX = offsetX
    minY = offsetY
    maxX = offsetX + 200
    maxY = offsetY + 60
  }

  return {
    nodes: layoutNodes,
    connections,
    bounds: { minX, minY, maxX, maxY },
  }
}

function getBranchColor(name: string): string {
  switch (name) {
    case 'THEN':
      return '#34D399' // Green
    case 'ELSE':
      return '#F87171' // Red
    case 'BODY':
      return '#22D3EE' // Cyan
    case 'TRY':
      return '#3B82F6' // Blue
    case 'CATCH':
      return '#F87171' // Red
    case 'FINALLY':
      return '#FACC15' // Yellow
    default:
      return '#9C27B0' // Purple
  }
}
