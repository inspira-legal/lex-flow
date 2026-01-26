import { useEffect, useState } from "react";
import { useUiStore, useWorkflowStore } from "../../store";
import { getWorkflowUnderPoint } from "../../services/layout/LayoutService";
import styles from "./DragPreview.module.css";

// Helper to find target workflow from mouse position (reads from store directly)
function getTargetWorkflow(e: MouseEvent): string {
  // Select the main canvas SVG (not icons) - it's inside the canvas container
  const svg = document.querySelector('[class*="canvas_"] > svg, [class*="Canvas_"] > svg');
  if (!svg) return "main";

  // Read current state from store
  const { zoom, panX, panY, layoutGroups, canvasCenter } = useUiStore.getState();

  if (layoutGroups.length === 0) return "main";

  const svgRect = svg.getBoundingClientRect();
  const svgWidth = svgRect.width;
  const svgHeight = svgRect.height;

  // Get mouse position relative to SVG
  const mouseX = e.clientX - svgRect.left;
  const mouseY = e.clientY - svgRect.top;

  // Reverse the transform to get canvas coordinates
  // Canvas transform is: translate(panX + svgWidth/2 - centerX*zoom, panY + svgHeight/2 - centerY*zoom) scale(zoom)
  const canvasX = (mouseX - panX - svgWidth / 2) / zoom + canvasCenter.x;
  const canvasY = (mouseY - panY - svgHeight / 2) / zoom + canvasCenter.y;

  return getWorkflowUnderPoint(layoutGroups, canvasX, canvasY) || "main";
}

export function DragPreview() {
  const {
    draggingOpcode,
    setDraggingOpcode,
    draggingWorkflowCall,
    setDraggingWorkflowCall,
    openNodeEditor,
  } = useUiStore();
  const { addNode, addWorkflowCallNode } = useWorkflowStore();
  const [position, setPosition] = useState({ x: 0, y: 0 });

  // Handle workflow call dragging
  useEffect(() => {
    if (!draggingWorkflowCall) return;

    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseUp = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const isOverCanvas =
        target.closest("svg") !== null ||
        target.closest('[class*="canvas"]') !== null;

      if (isOverCanvas && draggingWorkflowCall) {
        const targetWorkflow = getTargetWorkflow(e);
        const newNodeId = addWorkflowCallNode(
          draggingWorkflowCall.workflowName,
          draggingWorkflowCall.params,
          targetWorkflow,
        );
        if (newNodeId) {
          openNodeEditor();
        }
      }

      setDraggingWorkflowCall(null);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [
    draggingWorkflowCall,
    setDraggingWorkflowCall,
    addWorkflowCallNode,
    openNodeEditor,
  ]);

  useEffect(() => {
    if (!draggingOpcode) return;

    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseUp = (e: MouseEvent) => {
      // Check if dropped over canvas (not over palette or other panels)
      const target = e.target as HTMLElement;
      const isOverCanvas =
        target.closest("svg") !== null ||
        target.closest('[class*="canvas"]') !== null;

      if (isOverCanvas && draggingOpcode) {
        const targetWorkflow = getTargetWorkflow(e);
        const newNodeId = addNode(draggingOpcode, targetWorkflow);
        if (newNodeId) {
          openNodeEditor();
        }
      }

      setDraggingOpcode(null);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [draggingOpcode, setDraggingOpcode, addNode, openNodeEditor]);

  if (!draggingOpcode && !draggingWorkflowCall) return null;

  // Workflow call preview
  if (draggingWorkflowCall) {
    return (
      <div
        className={styles.preview}
        style={{
          left: position.x + 16,
          top: position.y + 16,
        }}
      >
        <div className={`${styles.card} ${styles.workflowCard}`}>
          <span className={styles.name}>{draggingWorkflowCall.workflowName}</span>
          <span className={styles.opcode}>workflow_call</span>
        </div>
        <div className={styles.hint}>Drop on canvas to add</div>
      </div>
    );
  }

  // Opcode preview
  if (!draggingOpcode) return null;

  const displayName = draggingOpcode.name
    .replace(
      /^(control_|data_|io_|operator_|list_|dict_|string_|math_|workflow_)/,
      "",
    )
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");

  return (
    <div
      className={styles.preview}
      style={{
        left: position.x + 16,
        top: position.y + 16,
      }}
    >
      <div className={styles.card}>
        <span className={styles.name}>{displayName}</span>
        <span className={styles.opcode}>{draggingOpcode.name}</span>
      </div>
      <div className={styles.hint}>Drop on canvas to add</div>
    </div>
  );
}
