// useCanvasView - Abstraction hook for canvas view state

import { useCallback } from "react";
import { useUiStore } from "../store";
import { CANVAS_DEFAULTS } from "../constants";

export function useCanvasView() {
  const zoom = useUiStore((state) => state.zoom);
  const setZoom = useUiStore((state) => state.setZoom);
  const panX = useUiStore((state) => state.panX);
  const panY = useUiStore((state) => state.panY);
  const setPan = useUiStore((state) => state.setPan);
  const resetView = useUiStore((state) => state.resetView);
  const isDraggingWorkflow = useUiStore((state) => state.isDraggingWorkflow);
  const setIsDraggingWorkflow = useUiStore(
    (state) => state.setIsDraggingWorkflow,
  );

  const zoomIn = useCallback(() => {
    setZoom(Math.min(zoom * 1.2, CANVAS_DEFAULTS.MAX_ZOOM));
  }, [zoom, setZoom]);

  const zoomOut = useCallback(() => {
    setZoom(Math.max(zoom / 1.2, CANVAS_DEFAULTS.MIN_ZOOM));
  }, [zoom, setZoom]);

  const zoomToFit = useCallback(() => {
    setZoom(CANVAS_DEFAULTS.ZOOM);
    setPan(CANVAS_DEFAULTS.PAN_X, CANVAS_DEFAULTS.PAN_Y);
  }, [setZoom, setPan]);

  return {
    // View state
    zoom,
    panX,
    panY,

    // Actions
    setZoom,
    setPan,
    resetView,
    zoomIn,
    zoomOut,
    zoomToFit,

    // Dragging
    isDraggingWorkflow,
    setIsDraggingWorkflow,
  };
}
