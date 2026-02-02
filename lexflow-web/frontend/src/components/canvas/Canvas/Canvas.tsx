import { useRef, useState, useEffect, useMemo, useCallback } from "react"
import { useUiStore, useWorkflowStore, useSelectionStore } from "@/store"
import type { OpcodeInterface } from "@/api/types"
import * as WorkflowService from "@/services/workflow/WorkflowService"
import { WorkflowNode } from "../WorkflowNode"
import { StartNode } from "../StartNode"
import { Connection } from "../Connection"
import { WireDragPreview, OrphanDragPreview, VariableDragPreview } from "../DragPreview"
import { MiniMap } from "../MiniMap"
import { NodeSearch } from "../NodeSearch"
import { WorkflowGroup } from "../WorkflowGroup"
import { NodeContextMenu } from "../NodeContextMenu"
import { CanvasContextMenu } from "../CanvasContextMenu"
import { AddNodeMenu } from "../AddNodeMenu"
import { useCanvasInteraction } from "@/hooks"
import { layoutAllWorkflows, getWorkflowUnderPoint } from "@/services/layout/LayoutService"
import { toYamlNodeId, getWorkflowNameFromSlotId } from "@/utils/wireUtils"
import { cn } from "@/lib/cn"
import { ZoomOutIcon, ZoomInIcon, FitViewIcon, GridIcon } from "@/components/icons"
import {
  canvasContainerVariants,
  svgVariants,
  canvasToolbarVariants,
  toolbarButtonVariants,
  toolbarDividerVariants,
  zoomLevelVariants,
  layoutButtonVariants,
  errorOverlayVariants,
  errorIconVariants,
  emptyStateVariants,
  emptyStateTitleVariants,
  emptyStateTextVariants,
} from "./styles"
import type { FormattedValue, TreeNode, WorkflowNode as WorkflowNodeType } from "@/api/types"

// Collect all reporter IDs from a node's inputs recursively
function collectAllReporterIds(
  inputs: Record<string, FormattedValue>,
  workflowName: string,
  collected: Set<string> = new Set()
): string[] {
  for (const value of Object.values(inputs)) {
    if (value.type === "reporter" && value.id) {
      const compositeId = `${workflowName}::${value.id}`
      collected.add(compositeId)
      // Recursively collect from nested inputs
      if (value.inputs) {
        collectAllReporterIds(value.inputs, workflowName, collected)
      }
    }
  }
  return Array.from(collected)
}

// Find a node in the tree by composite ID
function findNodeInTree(
  workflows: WorkflowNodeType[],
  compositeId: string
): { node: TreeNode; workflowName: string } | null {
  const [workflowName, nodeId] = compositeId.split("::")
  const workflow = workflows.find((w) => w.name === workflowName)
  if (!workflow) return null

  // Search in main children
  const searchNodes = (nodes: TreeNode[]): TreeNode | null => {
    for (const node of nodes) {
      if (node.id === nodeId) return node
      // Search in branch children
      for (const branch of node.children) {
        const found = searchNodes(branch.children)
        if (found) return found
      }
    }
    return null
  }

  const node = searchNodes(workflow.children)
  if (node) return { node, workflowName }

  // Search in orphans
  if (workflow.orphans) {
    const orphanNode = searchNodes(workflow.orphans)
    if (orphanNode) return { node: orphanNode, workflowName }
  }

  return null
}

export function Canvas() {
  const {
    zoom,
    panX,
    panY,
    setZoom,
    setPan,
    resetView,
    workflowPositions,
    setWorkflowPosition,
    nodePositions,
    setNodePosition,
    layoutMode,
    setLayoutMode,
    setLayoutGroups,
    setCanvasCenter,
    contextMenu,
    hideContextMenu,
    setReportersExpanded,
    setMultipleReportersExpanded,
    expandedReporters,
    canvasContextMenu,
    showCanvasContextMenu,
    hideCanvasContextMenu,
    showCreateWorkflowModal,
    showConfirmDialog,
    showExtractWorkflowModal,
    addNodeMenu,
    hideAddNodeMenu,
    openNodeEditor,
  } = useUiStore()
  const { tree, parseError, source, disconnectConnection, deleteNode, duplicateNode, deleteWorkflow, addNodeConnected, opcodes } = useWorkflowStore()
  const { selectedConnection, selectConnection, selectedNodeIds, clearMultiSelection, selectNode } = useSelectionStore()

  const svgRef = useRef<SVGSVGElement>(null)
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
    window.addEventListener("resize", updateSize)
    return () => window.removeEventListener("resize", updateSize)
  }, [])

  // Layout all workflows
  const {
    nodes: layoutNodes,
    connections,
    groups,
    startNodes,
  } = tree
    ? layoutAllWorkflows(tree.workflows, workflowPositions, nodePositions, expandedReporters)
    : { nodes: [], connections: [], groups: [], startNodes: [] }

  // Calculate canvas bounds
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

  // Calculate initial center only when tree changes
  const { centerX, centerY } = useMemo(() => {
    if (!tree) return { centerX: 400, centerY: 300 }

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

  // Sync layout groups to UI store for drop target detection
  // Use JSON.stringify to avoid infinite loop from new array reference on each render
  const groupsJson = JSON.stringify(groups)
  useEffect(() => {
    setLayoutGroups(groups)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [groupsJson, setLayoutGroups])

  // Sync canvas center to UI store for coordinate transformation in DragPreview
  useEffect(() => {
    setCanvasCenter(centerX, centerY)
  }, [centerX, centerY, setCanvasCenter])

  // Handle goto-workflow event (navigate canvas to a workflow's position)
  useEffect(() => {
    const handleGoToWorkflow = (e: Event) => {
      const customEvent = e as CustomEvent<{ workflowName: string }>
      const targetName = customEvent.detail.workflowName

      // Find the workflow group
      const group = groups.find((g) => g.name === targetName)
      if (!group) return

      // Calculate pan to center the workflow in the viewport
      const viewportCenterX = canvasSize.width / 2
      const viewportCenterY = canvasSize.height / 2
      const workflowCenterX = group.x + group.width / 2
      const workflowCenterY = group.y + group.height / 2

      // Calculate the offset from current center
      const newPanX =
        viewportCenterX - workflowCenterX * zoom - (canvasSize.width / 2 - centerX * zoom)
      const newPanY =
        viewportCenterY - workflowCenterY * zoom - (canvasSize.height / 2 - centerY * zoom)

      setPan(newPanX, newPanY)
    }

    window.addEventListener("lexflow:goto-workflow", handleGoToWorkflow)
    return () => window.removeEventListener("lexflow:goto-workflow", handleGoToWorkflow)
  }, [groups, zoom, setPan, canvasSize, centerX, centerY])

  // Use canvas interaction hook
  const { handleWheel, handleMouseDown, handleMouseMove, handleMouseUp, isDragging } =
    useCanvasInteraction({ svgRef, centerX, centerY })

  // Handle canvas right-click for context menu
  const handleCanvasContextMenu = useCallback(
    (e: React.MouseEvent) => {
      // Only show canvas context menu if click is on the SVG itself, background rect, or workflow group
      const target = e.target as Element
      const isBackground = target.tagName === "svg" || (target.tagName === "rect" && target.getAttribute("fill") === "transparent")
      const isWorkflowGroup = target.closest("[data-workflow-group]") !== null

      if (isBackground || isWorkflowGroup) {
        e.preventDefault()

        // Convert screen coords to canvas coords to detect which workflow was clicked
        if (svgRef.current) {
          const rect = svgRef.current.getBoundingClientRect()
          const canvasX = (e.clientX - rect.left - panX - rect.width / 2) / zoom + centerX
          const canvasY = (e.clientY - rect.top - panY - rect.height / 2) / zoom + centerY

          const workflowName = getWorkflowUnderPoint(groups, canvasX, canvasY)
          showCanvasContextMenu(e.clientX, e.clientY, workflowName || undefined)
        } else {
          showCanvasContextMenu(e.clientX, e.clientY)
        }
      }
    },
    [showCanvasContextMenu, svgRef, panX, panY, zoom, centerX, centerY, groups]
  )

  // Handle minimap navigation
  const handleMinimapNavigate = useCallback(
    (newPanX: number, newPanY: number) => {
      setPan(newPanX, newPanY)
    },
    [setPan]
  )

  // Handle add node menu selection
  const handleAddNodeSelect = useCallback(
    (opcode: OpcodeInterface) => {
      console.log("[AddNode] handleAddNodeSelect called", { opcode, addNodeMenu })
      if (!addNodeMenu) {
        console.log("[AddNode] addNodeMenu is null, returning")
        return
      }

      console.log("[AddNode] Calling addNodeConnected", {
        opcode: opcode.name,
        sourceNodeId: addNodeMenu.sourceNodeId,
        workflowName: addNodeMenu.workflowName
      })

      const newNodeId = addNodeConnected(
        opcode,
        addNodeMenu.sourceNodeId,
        addNodeMenu.workflowName
      )

      console.log("[AddNode] Result:", { newNodeId })

      if (newNodeId) {
        // Update selection to new node
        selectNode(newNodeId)
        // Open the node editor
        openNodeEditor()
      }

      hideAddNodeMenu()
    },
    [addNodeMenu, addNodeConnected, selectNode, openNodeEditor, hideAddNodeMenu]
  )

  return (
    <div className={cn(canvasContainerVariants())} data-canvas-container>
      {/* Node Search */}
      <NodeSearch />

      {/* Zoom Controls */}
      {/* Canvas Toolbar */}
      <div className={cn(canvasToolbarVariants())} role="toolbar" aria-label="Canvas controls">
        <button
          className={cn(toolbarButtonVariants())}
          onClick={() => setZoom(zoom - 0.1)}
          aria-label="Zoom out"
        >
          <ZoomOutIcon />
        </button>
        <span className={cn(zoomLevelVariants())} aria-live="polite">
          {Math.round(zoom * 100)}%
        </span>
        <button
          className={cn(toolbarButtonVariants())}
          onClick={() => setZoom(zoom + 0.1)}
          aria-label="Zoom in"
        >
          <ZoomInIcon />
        </button>
        <button
          className={cn(toolbarButtonVariants())}
          onClick={resetView}
          aria-label="Fit to view"
        >
          <FitViewIcon />
        </button>

        <div className={cn(toolbarDividerVariants())} />

        <button
          className={cn(layoutButtonVariants({ active: layoutMode === "auto" }))}
          onClick={() => setLayoutMode("auto")}
          aria-label="Auto layout"
          aria-pressed={layoutMode === "auto"}
        >
          <GridIcon />
          Auto
        </button>
        <button
          className={cn(layoutButtonVariants({ active: layoutMode === "free" }))}
          onClick={() => setLayoutMode("free")}
          aria-label="Free layout"
          aria-pressed={layoutMode === "free"}
        >
          Free
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
        <div className={cn(errorOverlayVariants())}>
          <span className={cn(errorIconVariants())}>⚠</span>
          <span>{parseError}</span>
        </div>
      )}

      {/* SVG Canvas */}
      <svg
        ref={svgRef}
        className={cn(svgVariants())}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onContextMenu={handleCanvasContextMenu}
        style={{ cursor: isDragging ? "grabbing" : "grab" }}
        role="application"
        aria-label="Workflow canvas. Use mouse to pan and scroll to zoom."
      >
        {/* Background for click handling */}
        <rect width="100%" height="100%" fill="transparent" style={{ cursor: "inherit" }} />

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
                const currentOffset = useUiStore.getState().workflowPositions[group.name] || {
                  x: 0,
                  y: 0,
                }
                setWorkflowPosition(group.name, currentOffset.x + dx, currentOffset.y + dy)
              }}
            />
          ))}

          {/* Connections (render second, below nodes) */}
          {connections.map((conn, i) => (
            <Connection
              key={`${conn.from}-${conn.to}-${i}`}
              fromNodeId={conn.from}
              toNodeId={conn.to}
              fromPort={conn.fromPort}
              toPort={conn.toPort}
              color={conn.color}
              label={conn.label}
              isSelected={
                selectedConnection?.fromNodeId === conn.from &&
                selectedConnection?.toNodeId === conn.to
              }
              onSelect={() =>
                selectConnection({
                  fromNodeId: conn.from,
                  toNodeId: conn.to,
                  label: conn.label,
                })
              }
              onDelete={() => {
                // Get workflow name from slot ID (handles both start-* and workflowName::nodeId)
                const workflowName = getWorkflowNameFromSlotId(conn.from)
                disconnectConnection(toYamlNodeId(conn.from), toYamlNodeId(conn.to), conn.label, workflowName)
                selectConnection(null)
              }}
            />
          ))}

          {/* Start Nodes */}
          {startNodes.map((sn) => (
            <StartNode
              key={`start-${sn.workflowName}`}
              workflowName={sn.workflowName}
              workflowInterface={sn.workflowInterface}
              variables={sn.variables}
              x={sn.x}
              y={sn.y}
              zoom={zoom}
              onDrag={
                layoutMode === "free"
                  ? (dx, dy) => {
                      const currentOffset = workflowPositions[sn.workflowName] || { x: 0, y: 0 }
                      setWorkflowPosition(
                        sn.workflowName,
                        currentOffset.x + dx,
                        currentOffset.y + dy
                      )
                    }
                  : undefined
              }
            />
          ))}

          {/* Nodes */}
          {layoutNodes.map((ln) => {
            const compositeId = `${ln.workflowName}::${ln.node.id}`
            return (
              <WorkflowNode
                key={compositeId}
                node={ln.node}
                x={ln.x}
                y={ln.y}
                isOrphan={ln.isOrphan}
                zoom={zoom}
                workflowName={ln.workflowName}
                onDrag={
                  layoutMode === "free"
                    ? (dx, dy) => {
                        const currentOffset = nodePositions[compositeId] || {
                          x: 0,
                          y: 0,
                        }
                        setNodePosition(compositeId, currentOffset.x + dx, currentOffset.y + dy)
                      }
                    : undefined
                }
              />
            )
          })}

          {/* Wire drag preview (rendered last, on top) */}
          <WireDragPreview />

          {/* Orphan drag preview */}
          <OrphanDragPreview />

          {/* Variable drag preview */}
          <VariableDragPreview />
        </g>
      </svg>

      {/* Empty state */}
      {!parseError && !tree && (
        <div className={cn(emptyStateVariants())}>
          <h2 className={cn(emptyStateTitleVariants())}>No Workflow</h2>
          <p className={cn(emptyStateTextVariants())}>Edit YAML in the editor or load an example</p>
        </div>
      )}

      {/* Node context menu */}
      {contextMenu && (() => {
        // Context menu nodeId is now a composite ID (workflowName::nodeId)
        // Extract raw nodeId for YAML operations, keep compositeId for UI state
        const rawNodeId = toYamlNodeId(contextMenu.nodeId)

        return (
          <NodeContextMenu
            x={contextMenu.x}
            y={contextMenu.y}
            nodeId={rawNodeId}
            hasReporters={contextMenu.hasReporters}
            reportersExpanded={contextMenu.reportersExpanded}
            isOrphan={contextMenu.isOrphan}
            onExpandReporters={() => {
              // Expand the node itself
              setReportersExpanded(contextMenu.nodeId, true)
              // Find the node and expand all nested reporters
              if (tree) {
                const result = findNodeInTree(tree.workflows, contextMenu.nodeId)
                if (result) {
                  const allReporterIds = collectAllReporterIds(result.node.inputs, result.workflowName)
                  if (allReporterIds.length > 0) {
                    setMultipleReportersExpanded(allReporterIds, true)
                  }
                }
              }
            }}
            onCollapseReporters={() => {
              // Collapse the node itself
              setReportersExpanded(contextMenu.nodeId, false)
              // Find the node and collapse all nested reporters
              if (tree) {
                const result = findNodeInTree(tree.workflows, contextMenu.nodeId)
                if (result) {
                  const allReporterIds = collectAllReporterIds(result.node.inputs, result.workflowName)
                  if (allReporterIds.length > 0) {
                    setMultipleReportersExpanded(allReporterIds, false)
                  }
                }
              }
            }}
            onDelete={() => {
              deleteNode(rawNodeId)
              clearMultiSelection()
            }}
            onDuplicate={() => duplicateNode(rawNodeId)}
            onClose={hideContextMenu}
            selectedNodeIds={selectedNodeIds}
            onExtractToWorkflow={() => {
              // Convert composite IDs to raw node IDs for YAML operations
              const compositeIds = selectedNodeIds.length > 0 ? selectedNodeIds : [contextMenu.nodeId]
              const rawNodeIds = compositeIds.map(toYamlNodeId)
              if (rawNodeIds.length < 2) return

              // Extract workflow name from the first composite ID
              let workflowName = getWorkflowNameFromSlotId(compositeIds[0]) || "main"

              // Validate the chain first
              const validation = WorkflowService.validateLinearChain(source, rawNodeIds, workflowName)
              if (!validation.isValid) {
                showConfirmDialog({
                  title: "Cannot Extract",
                  message: validation.errors.join("\n"),
                  confirmLabel: "OK",
                  onConfirm: () => {},
                })
                return
              }

              // Analyze variables for suggestions
              const variables = WorkflowService.analyzeChainVariables(source, rawNodeIds)

              // Show the extract workflow modal
              showExtractWorkflowModal(
                validation.orderedNodeIds,
                workflowName,
                variables.suggestedInputs,
                variables.suggestedOutputs
              )
            }}
          />
        )
      })()}

      {/* Canvas context menu (background right-click) */}
      {canvasContextMenu && (
        <CanvasContextMenu
          x={canvasContextMenu.x}
          y={canvasContextMenu.y}
          workflowName={canvasContextMenu.workflowName}
          onCreateWorkflow={showCreateWorkflowModal}
          onDeleteWorkflow={(name) => {
            showConfirmDialog({
              title: "Delete Workflow",
              message: `Are you sure you want to delete the workflow "${name}"? This action cannot be undone.`,
              confirmLabel: "Delete",
              variant: "danger",
              onConfirm: () => deleteWorkflow(name),
            })
          }}
          onClose={hideCanvasContextMenu}
        />
      )}

      {/* Add node menu */}
      {addNodeMenu && (
        <AddNodeMenu
          x={addNodeMenu.x}
          y={addNodeMenu.y}
          opcodes={opcodes}
          onSelect={handleAddNodeSelect}
          onClose={hideAddNodeMenu}
        />
      )}
    </div>
  )
}
