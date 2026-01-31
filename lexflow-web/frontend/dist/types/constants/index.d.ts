import type { NodeType } from "../api/types";
import { getGrammar, getBranchColor, getNodeColor, getReporterColor, getControlFlowOpcodeSet, getBranchSlots, getCategories, getCategoryIcon } from "../services/grammar";
export { getBranchColor, getNodeColor, getReporterColor, getControlFlowOpcodeSet, getBranchSlots, getCategories, getCategoryIcon, getGrammar, };
export declare const NODE_DIMENSIONS: {
    readonly WIDTH: 110;
    readonly HEIGHT: 70;
    readonly MIN_HEIGHT: 70;
    readonly EXPANDED_INPUT_HEIGHT: 30;
    readonly SLOT_HEIGHT: 24;
    readonly HEADER_HEIGHT: 32;
    readonly PADDING: 8;
};
export declare const LAYOUT_GAPS: {
    readonly HORIZONTAL: 60;
    readonly VERTICAL: 40;
    readonly WORKFLOW: 80;
};
export declare const START_NODE_DIMENSIONS: {
    readonly WIDTH: 140;
    readonly HEIGHT: 60;
};
export declare const CANVAS_DEFAULTS: {
    readonly ZOOM: 1;
    readonly MIN_ZOOM: 0.25;
    readonly MAX_ZOOM: 2;
    readonly PAN_X: 0;
    readonly PAN_Y: 0;
};
export declare const NODE_TYPE_LABELS: Record<NodeType | string, string>;
export declare const MAX_UNDO_HISTORY = 50;
