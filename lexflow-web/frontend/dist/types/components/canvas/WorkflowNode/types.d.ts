import type { TreeNode } from "@/api/types";
export interface WorkflowNodeProps {
    node: TreeNode;
    x: number;
    y: number;
    isOrphan?: boolean;
    zoom?: number;
    onDrag?: (dx: number, dy: number) => void;
}
