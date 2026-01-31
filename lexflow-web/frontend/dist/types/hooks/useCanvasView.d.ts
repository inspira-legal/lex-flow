export declare function useCanvasView(): {
    zoom: number;
    panX: number;
    panY: number;
    setZoom: (zoom: number) => void;
    setPan: (x: number, y: number) => void;
    resetView: () => void;
    zoomIn: () => void;
    zoomOut: () => void;
    zoomToFit: () => void;
    isDraggingWorkflow: boolean;
    setIsDraggingWorkflow: (dragging: boolean) => void;
};
