import type { TreeNode } from "../api/types";
export declare function useSelection(): {
    selectedNodeId: string | null;
    selectedNode: TreeNode | null;
    selectNode: (id: string | null) => void;
    selectedReporter: import("../store").SelectedReporter | null;
    selectReporter: (reporter: import("../store").SelectedReporter | null) => void;
    selectedConnection: import("../store").SelectedConnection | null;
    selectConnection: (conn: import("../store").SelectedConnection | null) => void;
    selectedStartNode: string | null;
    selectStartNode: (workflowName: string | null) => void;
    clearSelection: () => void;
};
