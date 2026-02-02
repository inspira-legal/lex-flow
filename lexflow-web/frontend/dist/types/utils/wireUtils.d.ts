import type { NodeSlotPositions, SlotPosition } from "../store/uiStore";
export declare const WIRE_SNAP_DISTANCE = 25;
export declare const NODE_WIDTH = 180;
export declare function toYamlNodeId(registryId: string): string;
export declare function getWorkflowNameFromSlotId(slotId: string): string | undefined;
export declare function calculateDistance(x1: number, y1: number, x2: number, y2: number): number;
export declare function getPortPositionFromRegistry(nodeId: string, port: "input" | "output" | string, slotPositions: Record<string, NodeSlotPositions>): SlotPosition | null;
export declare function getPortPosition(nodeX: number, nodeY: number, port: "input" | "output"): {
    x: number;
    y: number;
};
interface LayoutNode {
    node: {
        id: string;
    };
    x: number;
    y: number;
    isOrphan?: boolean;
}
interface NearbyPort {
    nodeId: string;
    port: "input" | "output";
    x: number;
    y: number;
}
export declare function findNearestPortFromRegistry(dragX: number, dragY: number, sourceNodeId: string, sourcePort: "input" | "output", slotPositions: Record<string, NodeSlotPositions>): NearbyPort | null;
export declare function findNearestPort(dragX: number, dragY: number, sourceNodeId: string, sourcePort: "input" | "output", layoutNodes: LayoutNode[]): NearbyPort | null;
export {};
