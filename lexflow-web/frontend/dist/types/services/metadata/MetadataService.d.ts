export interface EditorMetadata {
    version: string;
    layout: {
        mode: "auto" | "free";
        nodePositions: Record<string, {
            x: number;
            y: number;
        }>;
        workflowPositions: Record<string, {
            x: number;
            y: number;
        }>;
    };
    viewport: {
        zoom: number;
        panX: number;
        panY: number;
    };
}
export declare function extractMetadata(source: string): EditorMetadata | null;
export declare function injectMetadata(source: string, metadata: EditorMetadata): string;
export declare function createMetadataFromState(layoutMode: "auto" | "free", nodePositions: Record<string, {
    x: number;
    y: number;
}>, workflowPositions: Record<string, {
    x: number;
    y: number;
}>, zoom: number, panX: number, panY: number): EditorMetadata;
