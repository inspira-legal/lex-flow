import { useCallback, useMemo } from "react"
import type { TreeNode } from "@/api/types"
import { cn } from "@/lib/cn"
import {
  MINIMAP_WIDTH,
  MINIMAP_HEIGHT,
  NODE_WIDTH,
  NODE_HEIGHT,
  H_GAP,
  V_GAP,
  WORKFLOW_GAP,
  minimapVariants,
  viewportStyle,
  getNodeColor,
} from "./styles"
import type { MiniMapProps } from "./types"

export function MiniMap({
  workflows,
  bounds,
  zoom,
  panX,
  panY,
  canvasWidth,
  canvasHeight,
  onNavigate,
}: MiniMapProps) {
  // Calculate the scale to fit all workflows in the minimap
  const contentWidth = bounds.maxX - bounds.minX
  const contentHeight = bounds.maxY - bounds.minY
  const scale = Math.min(
    (MINIMAP_WIDTH - 10) / Math.max(contentWidth, 100),
    (MINIMAP_HEIGHT - 10) / Math.max(contentHeight, 100)
  )

  // Calculate viewport rectangle in minimap coordinates
  const viewport = useMemo(() => {
    const centerX = (bounds.maxX + bounds.minX) / 2
    const centerY = (bounds.maxY + bounds.minY) / 2

    const viewWidth = canvasWidth / zoom
    const viewHeight = canvasHeight / zoom

    const viewCenterX = centerX - panX / zoom
    const viewCenterY = centerY - panY / zoom

    const x = (viewCenterX - bounds.minX - viewWidth / 2) * scale + 5
    const y = (viewCenterY - bounds.minY - viewHeight / 2) * scale + 5
    const width = viewWidth * scale
    const height = viewHeight * scale

    return { x, y, width, height }
  }, [bounds, zoom, panX, panY, canvasWidth, canvasHeight, scale])

  // Handle click to navigate
  const handleClick = useCallback(
    (e: React.MouseEvent<SVGSVGElement>) => {
      const svg = e.currentTarget
      const rect = svg.getBoundingClientRect()
      const clickX = e.clientX - rect.left
      const clickY = e.clientY - rect.top

      const contentX = (clickX - 5) / scale + bounds.minX
      const contentY = (clickY - 5) / scale + bounds.minY

      const centerX = (bounds.maxX + bounds.minX) / 2
      const centerY = (bounds.maxY + bounds.minY) / 2

      const newPanX = (centerX - contentX) * zoom
      const newPanY = (centerY - contentY) * zoom

      onNavigate(newPanX, newPanY)
    },
    [bounds, scale, zoom, onNavigate]
  )

  // Get simple node positions for minimap from all workflows
  const nodes = useMemo(() => {
    if (!workflows || workflows.length === 0) return []

    const result: {
      x: number
      y: number
      width: number
      height: number
      color: string
    }[] = []
    let currentY = 0

    for (const workflow of workflows) {
      let x = 0
      let maxY = currentY

      function processNode(node: TreeNode, nodeX: number, nodeY: number): number {
        const height = NODE_HEIGHT + Math.min(Object.keys(node.inputs).length, 2) * 18
        result.push({
          x: (nodeX - bounds.minX) * scale + 5,
          y: (nodeY - bounds.minY) * scale + 5,
          width: NODE_WIDTH * scale,
          height: height * scale,
          color: getNodeColor(node.type),
        })

        maxY = Math.max(maxY, nodeY + height)
        let nextX = nodeX + NODE_WIDTH + H_GAP
        let branchOffset = nodeY + height + V_GAP

        for (const branch of node.children) {
          let branchX = nodeX + NODE_WIDTH + H_GAP

          for (const childNode of branch.children) {
            const childHeight =
              NODE_HEIGHT + Math.min(Object.keys(childNode.inputs).length, 2) * 18
            result.push({
              x: (branchX - bounds.minX) * scale + 5,
              y: (branchOffset - bounds.minY) * scale + 5,
              width: NODE_WIDTH * scale,
              height: childHeight * scale,
              color: getNodeColor(childNode.type),
            })

            maxY = Math.max(maxY, branchOffset + childHeight)
            branchX += NODE_WIDTH + H_GAP
            nextX = Math.max(nextX, branchX)
          }

          branchOffset += NODE_HEIGHT + V_GAP * 2
        }

        return nextX
      }

      for (const node of workflow.children) {
        const nextX = processNode(node, x, currentY)
        x = nextX
      }

      currentY = maxY + WORKFLOW_GAP
    }

    return result
  }, [workflows, bounds, scale])

  if (!workflows || workflows.length === 0 || nodes.length === 0) {
    return null
  }

  return (
    <div className={cn(minimapVariants())} aria-label="Canvas minimap navigation">
      <svg
        width={MINIMAP_WIDTH}
        height={MINIMAP_HEIGHT}
        onClick={handleClick}
        style={{ display: "block", cursor: "pointer" }}
        role="img"
        aria-label="Minimap showing workflow overview. Click to navigate."
      >
        {/* Background */}
        <rect
          x={0}
          y={0}
          width={MINIMAP_WIDTH}
          height={MINIMAP_HEIGHT}
          fill="var(--color-surface-2)"
          rx={4}
        />

        {/* Nodes */}
        {nodes.map((node, i) => (
          <rect
            key={i}
            x={node.x}
            y={node.y}
            width={Math.max(node.width, 2)}
            height={Math.max(node.height, 2)}
            fill={node.color}
            opacity={0.7}
            rx={1}
          />
        ))}

        {/* Viewport indicator */}
        <rect
          x={Math.max(0, viewport.x)}
          y={Math.max(0, viewport.y)}
          width={Math.min(viewport.width, MINIMAP_WIDTH)}
          height={Math.min(viewport.height, MINIMAP_HEIGHT)}
          fill="rgba(59, 130, 246, 0.15)"
          stroke="var(--color-accent-blue)"
          strokeWidth={1.5}
          rx={2}
          style={viewportStyle}
        />
      </svg>
    </div>
  )
}
