import { useUiStore } from "@/store"
import { cn } from "@/lib/cn"
import { Header } from "@/components/layout/Header"
import { PanelResizer, useResize } from "@/components/layout/PanelResizer"
import {
  layoutVariants,
  mainVariants,
  editorPanelVariants,
  canvasAreaVariants,
  bottomPanelVariants,
  nodeEditorPanelVariants,
  paletteOverlayVariants,
  paletteDrawerVariants,
} from "./styles"
import type { MainLayoutProps } from "./types"

const EDITOR_MIN_WIDTH = 240
const EDITOR_MAX_WIDTH = 480
const EDITOR_DEFAULT_WIDTH = 320

export function MainLayout({
  canvas,
  editor,
  nodeEditor,
  executionPanel,
  palette,
  className,
}: MainLayoutProps) {
  const {
    isEditorOpen,
    isNodeEditorOpen,
    isPaletteOpen,
    isExecutionPanelOpen,
    togglePalette,
  } = useUiStore()

  const {
    size: editorWidth,
    isResizing: isEditorResizing,
    handleMouseDown: handleEditorResizeStart,
  } = useResize({
    orientation: "horizontal",
    minSize: EDITOR_MIN_WIDTH,
    maxSize: EDITOR_MAX_WIDTH,
    defaultSize: EDITOR_DEFAULT_WIDTH,
  })

  return (
    <div className={cn(layoutVariants(), className)}>
      <Header />

      <div className={mainVariants()}>
        {/* Left: Editor Panel */}
        {isEditorOpen && editor && (
          <aside
            className={editorPanelVariants()}
            style={{ width: `${editorWidth}px` }}
          >
            {editor}
            <PanelResizer
              orientation="horizontal"
              isResizing={isEditorResizing}
              onMouseDown={handleEditorResizeStart}
            />
          </aside>
        )}

        {/* Center: Canvas */}
        <div className={canvasAreaVariants()}>
          {canvas}

          {/* Bottom: Execution Panel */}
          {isExecutionPanelOpen && executionPanel && (
            <div className={bottomPanelVariants()}>{executionPanel}</div>
          )}
        </div>

        {/* Right: Node Editor (slide-in) */}
        <aside className={nodeEditorPanelVariants({ isOpen: isNodeEditorOpen })}>
          {nodeEditor}
        </aside>
      </div>

      {/* Palette Overlay */}
      {isPaletteOpen && palette && (
        <div className={paletteOverlayVariants()} onClick={togglePalette}>
          <div
            className={paletteDrawerVariants()}
            onClick={(e) => e.stopPropagation()}
          >
            {palette}
          </div>
        </div>
      )}
    </div>
  )
}
