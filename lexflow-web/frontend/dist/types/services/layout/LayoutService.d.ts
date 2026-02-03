import type { FormattedValue, TreeNode, WorkflowNode, WorkflowInterface } from "../../api/types";
export interface LayoutNode {
    node: TreeNode;
    x: number;
    y: number;
    width: number;
    height: number;
    isOrphan?: boolean;
    workflowName: string;
}
export interface LayoutConnection {
    from: string;
    to: string;
    fromPort: "input" | "output" | string;
    toPort: "input" | "output";
    color: string;
    label?: string;
}
export interface LayoutWorkflowGroup {
    name: string;
    x: number;
    y: number;
    width: number;
    height: number;
    isMain: boolean;
}
export interface LayoutStartNode {
    workflowName: string;
    workflowInterface: WorkflowInterface;
    variables: Record<string, unknown>;
    x: number;
    y: number;
}
export interface FullLayout {
    nodes: LayoutNode[];
    connections: LayoutConnection[];
    groups: LayoutWorkflowGroup[];
    startNodes: LayoutStartNode[];
}
export declare function calculateReporterTotalHeight(value: FormattedValue, includeLabel?: boolean): number;
export declare function formatValueShort(value: FormattedValue): string;
export declare function calculateNodeDimensions(nodeId: string, inputs: Record<string, FormattedValue>, opcode: string | undefined, expandedReporters: Record<string, boolean>, workflowName?: string): {
    width: number;
    height: number;
};
export declare function calculateNodeHeight(_inputs: Record<string, FormattedValue>, opcode?: string): number;
export interface Position {
    x: number;
    y: number;
}
export declare function applyPositionOffset(basePosition: Position, offset: Position | undefined): Position;
export declare function screenToCanvas(screenX: number, screenY: number, panX: number, panY: number, zoom: number): Position;
export declare function canvasToScreen(canvasX: number, canvasY: number, panX: number, panY: number, zoom: number): Position;
export declare function clampZoom(zoom: number, minZoom?: number, maxZoom?: number): number;
export interface BoundingBox {
    minX: number;
    minY: number;
    maxX: number;
    maxY: number;
    width: number;
    height: number;
}
export declare function calculateBoundingBox(positions: Position[]): BoundingBox | null;
export declare function calculateCenter(box: BoundingBox): Position;
export declare function getBranchColor(name: string): string;
export declare function layoutAllWorkflows(workflows: WorkflowNode[], positionOffsets: Record<string, {
    x: number;
    y: number;
}>, nodePositionOffsets?: Record<string, {
    x: number;
    y: number;
}>, expandedReporters?: Record<string, boolean>): FullLayout;
export declare function layoutSingleWorkflow(workflow: WorkflowNode, offsetX: number, offsetY: number, nodePositionOffsets?: Record<string, {
    x: number;
    y: number;
}>, expandedReporters?: Record<string, boolean>): {
    nodes: LayoutNode[];
    connections: LayoutConnection[];
    bounds: {
        minX: number;
        minY: number;
        maxX: number;
        maxY: number;
    };
    startNode: LayoutStartNode | null;
};
export declare function getWorkflowUnderPoint(groups: LayoutWorkflowGroup[], x: number, y: number): string | null;
export declare const layoutService: {
    calculateReporterTotalHeight: typeof calculateReporterTotalHeight;
    formatValueShort: typeof formatValueShort;
    calculateNodeHeight: typeof calculateNodeHeight;
    applyPositionOffset: typeof applyPositionOffset;
    screenToCanvas: typeof screenToCanvas;
    canvasToScreen: typeof canvasToScreen;
    clampZoom: typeof clampZoom;
    calculateBoundingBox: typeof calculateBoundingBox;
    calculateCenter: typeof calculateCenter;
    getBranchColor: typeof getBranchColor;
    layoutAllWorkflows: typeof layoutAllWorkflows;
    layoutSingleWorkflow: typeof layoutSingleWorkflow;
    getWorkflowUnderPoint: typeof getWorkflowUnderPoint;
};
