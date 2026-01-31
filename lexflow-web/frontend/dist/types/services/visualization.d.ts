import type { WorkflowTree } from "../api/types";
interface WorkflowData {
    workflows?: WorkflowDefinition[];
    nodes?: Record<string, NodeDefinition>;
    name?: string;
    interface?: {
        inputs?: string[];
        outputs?: string[];
    };
    variables?: Record<string, unknown>;
}
interface WorkflowDefinition {
    name?: string;
    nodes?: Record<string, NodeDefinition>;
    interface?: {
        inputs?: string[];
        outputs?: string[];
    };
    variables?: Record<string, unknown>;
}
interface NodeDefinition {
    opcode?: string;
    inputs?: Record<string, unknown>;
    next?: string;
    isReporter?: boolean;
}
export declare function workflowToTree(workflowData: WorkflowData): WorkflowTree | {
    error: string;
};
export {};
