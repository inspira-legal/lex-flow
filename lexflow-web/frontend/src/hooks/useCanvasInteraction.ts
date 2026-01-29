// Canvas interaction hook - handles pan, zoom, wire/orphan/variable dragging

import { useState, useCallback } from "react";
import { useUiStore, useWorkflowStore, useSelectionStore } from "../store";
import { findNearestPortFromRegistry } from "../utils/wireUtils";

interface UseCanvasInteractionProps {
  svgRef: React.RefObject<SVGSVGElement | null>;
  centerX: number;
  centerY: number;
}

interface UseCanvasInteractionReturn {
  handleWheel: (e: React.WheelEvent) => void;
  handleMouseDown: (e: React.MouseEvent) => void;
  handleMouseMove: (e: React.MouseEvent) => void;
  handleMouseUp: () => void;
  isDragging: boolean;
}

export function useCanvasInteraction({
  svgRef,
  centerX,
  centerY,
}: UseCanvasInteractionProps): UseCanvasInteractionReturn {
  const {
    zoom,
    panX,
    panY,
    setZoom,
    setPan,
    isDraggingWorkflow,
    isDraggingNode,
    draggingWire,
    setDraggingWire,
    updateDraggingWire,
    draggingOrphan,
    setDraggingOrphan,
    updateDraggingOrphanEnd,
    draggingVariable,
    setDraggingVariable,
    updateDraggingVariableEnd,
    slotPositions,
  } = useUiStore();

  const { connectNodes, connectBranch } = useWorkflowStore();
  const { selectNode, selectStartNode, selectConnection } = useSelectionStore();

  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Convert screen coordinates to canvas coordinates
  const screenToCanvas = useCallback(
    (clientX: number, clientY: number) => {
      if (!svgRef.current) return { x: 0, y: 0 };
      const rect = svgRef.current.getBoundingClientRect();
      return {
        x: (clientX - rect.left - panX - rect.width / 2) / zoom + centerX,
        y: (clientY - rect.top - panY - rect.height / 2) / zoom + centerY,
      };
    },
    [svgRef, panX, panY, zoom, centerX, centerY],
  );

  // Handle zoom via wheel
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        setZoom(zoom + delta);
      }
    },
    [zoom, setZoom],
  );

  // Handle pan start
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (isDraggingWorkflow || isDraggingNode) return;

      // Only start pan if clicking on background
      const target = e.target as Element;
      const isBackground =
        target === svgRef.current ||
        target.classList.contains("background") ||
        target.tagName === "rect";

      if (isBackground) {
        setIsDragging(true);
        setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
        selectNode(null);
        selectStartNode(null);
        selectConnection(null);
      }
    },
    [
      panX,
      panY,
      selectNode,
      selectStartNode,
      selectConnection,
      isDraggingWorkflow,
      isDraggingNode,
      svgRef,
    ],
  );

  // Handle mouse move - wire/orphan/variable dragging and pan
  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      // Handle wire dragging
      if (draggingWire) {
        const { x: canvasX, y: canvasY } = screenToCanvas(
          e.clientX,
          e.clientY,
        );

        // Find nearest valid port using slot registry
        const nearbyPort = findNearestPortFromRegistry(
          canvasX,
          canvasY,
          draggingWire.sourceNodeId,
          draggingWire.sourcePort,
          slotPositions,
        );

        updateDraggingWire({
          dragX: canvasX,
          dragY: canvasY,
          nearbyPort,
        });
        return;
      }

      // Handle orphan dragging
      if (draggingOrphan) {
        const { x: canvasX, y: canvasY } = screenToCanvas(
          e.clientX,
          e.clientY,
        );
        updateDraggingOrphanEnd(canvasX, canvasY);
        return;
      }

      // Handle variable dragging
      if (draggingVariable) {
        const { x: canvasX, y: canvasY } = screenToCanvas(
          e.clientX,
          e.clientY,
        );
        updateDraggingVariableEnd(canvasX, canvasY);
        return;
      }

      // Handle pan dragging
      if (isDraggingWorkflow || isDraggingNode) return;
      if (isDragging) {
        setPan(e.clientX - dragStart.x, e.clientY - dragStart.y);
      }
    },
    [
      isDragging,
      dragStart,
      setPan,
      isDraggingWorkflow,
      isDraggingNode,
      draggingWire,
      updateDraggingWire,
      draggingOrphan,
      updateDraggingOrphanEnd,
      draggingVariable,
      updateDraggingVariableEnd,
      screenToCanvas,
      slotPositions,
    ],
  );

  // Handle mouse up - complete wire connections, cancel drags, end pan
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);

    // Complete wire connection if near a valid port
    if (draggingWire) {
      if (draggingWire.nearbyPort) {
        if (draggingWire.branchLabel) {
          // Branch connection
          connectBranch(
            draggingWire.sourceNodeId,
            draggingWire.nearbyPort.nodeId,
            draggingWire.branchLabel,
          );
        } else if (draggingWire.sourcePort === "output") {
          // Regular: output to input
          connectNodes(
            draggingWire.sourceNodeId,
            draggingWire.nearbyPort.nodeId,
          );
        } else {
          // Reverse: input to output
          connectNodes(
            draggingWire.nearbyPort.nodeId,
            draggingWire.sourceNodeId,
          );
        }
      }
      setDraggingWire(null);
    }

    // Cancel orphan drag
    if (draggingOrphan) {
      setDraggingOrphan(null);
    }

    // Cancel variable drag
    if (draggingVariable) {
      setDraggingVariable(null);
    }
  }, [
    draggingWire,
    setDraggingWire,
    draggingOrphan,
    setDraggingOrphan,
    draggingVariable,
    setDraggingVariable,
    connectNodes,
    connectBranch,
  ]);

  return {
    handleWheel,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    isDragging,
  };
}
