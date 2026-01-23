import { useUiStore } from "../../store";
import { Header } from "./Header";
import styles from "./MainLayout.module.css";

interface MainLayoutProps {
  canvas: React.ReactNode;
  editor?: React.ReactNode;
  nodeEditor?: React.ReactNode;
  executionPanel?: React.ReactNode;
  palette?: React.ReactNode;
}

export function MainLayout({
  canvas,
  editor,
  nodeEditor,
  executionPanel,
  palette,
}: MainLayoutProps) {
  const {
    isEditorOpen,
    isNodeEditorOpen,
    isPaletteOpen,
    isExecutionPanelOpen,
  } = useUiStore();

  return (
    <div className={styles.layout}>
      <Header />

      <div className={styles.main}>
        {/* Left: Editor Panel */}
        {isEditorOpen && editor && (
          <aside className={styles.editorPanel}>{editor}</aside>
        )}

        {/* Center: Canvas */}
        <div className={styles.canvasArea}>
          {canvas}

          {/* Bottom: Execution Panel */}
          {isExecutionPanelOpen && executionPanel && (
            <div className={styles.bottomPanel}>{executionPanel}</div>
          )}
        </div>

        {/* Right: Node Editor (slide-in) */}
        <aside
          className={`${styles.nodeEditorPanel} ${isNodeEditorOpen ? styles.open : ""}`}
        >
          {nodeEditor}
        </aside>
      </div>

      {/* Palette Drawer (overlay) */}
      {isPaletteOpen && palette && (
        <div className={styles.paletteOverlay}>
          <div className={styles.paletteDrawer}>{palette}</div>
        </div>
      )}
    </div>
  );
}
