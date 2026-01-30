export type ResizeOrientation = "horizontal" | "vertical"

export interface UseResizeOptions {
  orientation: ResizeOrientation
  minSize: number
  maxSize: number
  defaultSize: number
}

export interface UseResizeReturn {
  size: number
  isResizing: boolean
  handleMouseDown: (e: React.MouseEvent) => void
}

export interface PanelResizerProps {
  orientation: ResizeOrientation
  isResizing?: boolean
  onMouseDown: (e: React.MouseEvent) => void
  className?: string
}
