import type { WorkflowNode as WorkflowNodeType } from "@/api/types"

export interface MiniMapProps {
  workflows: WorkflowNodeType[]
  bounds: { minX: number; minY: number; maxX: number; maxY: number }
  zoom: number
  panX: number
  panY: number
  canvasWidth: number
  canvasHeight: number
  onNavigate: (panX: number, panY: number) => void
}
