import { useEffect, useState } from "react";
import { useUiStore, useWorkflowStore } from "../../store";
import styles from "./DragPreview.module.css";

export function DragPreview() {
  const { draggingOpcode, setDraggingOpcode, openNodeEditor } = useUiStore();
  const { addNode } = useWorkflowStore();
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (!draggingOpcode) return;

    const handleMouseMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    const handleMouseUp = (e: MouseEvent) => {
      // Check if dropped over canvas (not over palette or other panels)
      const target = e.target as HTMLElement;
      console.log(
        "[DragPreview] mouseUp target:",
        target.tagName,
        target.className,
      );
      const isOverCanvas =
        target.closest("svg") !== null ||
        target.closest('[class*="canvas"]') !== null;
      console.log(
        "[DragPreview] isOverCanvas:",
        isOverCanvas,
        "draggingOpcode:",
        draggingOpcode?.name,
      );

      if (isOverCanvas && draggingOpcode) {
        console.log("[DragPreview] Calling addNode");
        const newNodeId = addNode(draggingOpcode);
        console.log("[DragPreview] addNode returned:", newNodeId);
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
