// Command types for centralized editing operations
// All editing operations are expressed as serializable commands

import type { OpcodeInterface, DetailedInput } from "../../api/types";

// Union type for all workflow commands
export type WorkflowCommand =
  | { type: "ADD_NODE"; opcode: OpcodeInterface; workflowName?: string }
  | { type: "DELETE_NODE"; nodeId: string }
  | { type: "DUPLICATE_NODE"; nodeId: string }
  | { type: "UPDATE_INPUT"; nodeId: string; inputKey: string; value: string }
  | { type: "CONNECT_NODES"; fromId: string; toId: string }
  | { type: "CONNECT_BRANCH"; fromId: string; toId: string; branchLabel: string }
  | { type: "DISCONNECT_NODE"; nodeId: string }
  | {
      type: "DISCONNECT_CONNECTION";
      fromId: string;
      toId: string;
      branchLabel?: string;
    }
  | {
      type: "CONVERT_ORPHAN_TO_REPORTER";
      orphanId: string;
      targetId: string;
      inputKey: string;
    }
  | { type: "DELETE_REPORTER"; parentId: string; inputPath: string[] }
  | {
      type: "ADD_VARIABLE";
      workflowName: string;
      name: string;
      value: unknown;
    }
  | {
      type: "UPDATE_VARIABLE";
      workflowName: string;
      oldName: string;
      newName: string;
      value: unknown;
    }
  | { type: "DELETE_VARIABLE"; workflowName: string; name: string }
  | {
      type: "UPDATE_INTERFACE";
      workflowName: string;
      inputs: DetailedInput[];
      outputs: string[];
    }
  | { type: "ADD_DYNAMIC_BRANCH"; nodeId: string; branchPrefix: string }
  | { type: "REMOVE_DYNAMIC_BRANCH"; nodeId: string; branchName: string }
  | { type: "ADD_DYNAMIC_INPUT"; nodeId: string; inputPrefix: string }
  | { type: "REMOVE_DYNAMIC_INPUT"; nodeId: string; inputName: string }
  | {
      type: "ADD_WORKFLOW_CALL_NODE";
      workflowName: string;
      params: string[];
      targetWorkflow?: string;
    };

// Result of executing a command
export interface CommandResult {
  success: boolean;
  source?: string;
  nodeId?: string; // For ADD/DUPLICATE operations that create new nodes
  error?: string;
}
