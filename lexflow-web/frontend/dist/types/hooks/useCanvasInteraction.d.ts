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
export declare function useCanvasInteraction({ svgRef, centerX, centerY, }: UseCanvasInteractionProps): UseCanvasInteractionReturn;
export {};
