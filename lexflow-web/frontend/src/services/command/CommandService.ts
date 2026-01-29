// CommandService - Single entry point for all editing operations
// Provides serializable, testable command execution

import * as WorkflowService from "../workflow/WorkflowService";
import type { WorkflowCommand, CommandResult } from "./types";

/**
 * Execute a workflow editing command on the given source.
 * Returns the result with new source (if successful) and any created node ID.
 */
export function executeCommand(
  source: string,
  command: WorkflowCommand
): CommandResult {
  switch (command.type) {
    case "ADD_NODE": {
      const result = WorkflowService.addNode(
        source,
        command.opcode,
        command.workflowName
      );
      return {
        success: result.nodeId !== null,
        source: result.source,
        nodeId: result.nodeId ?? undefined,
      };
    }

    case "DELETE_NODE": {
      const result = WorkflowService.deleteNode(source, command.nodeId);
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "DUPLICATE_NODE": {
      const result = WorkflowService.duplicateNode(source, command.nodeId);
      return {
        success: result.nodeId !== null,
        source: result.source,
        nodeId: result.nodeId ?? undefined,
      };
    }

    case "UPDATE_INPUT": {
      const result = WorkflowService.updateNodeInput(
        source,
        command.nodeId,
        command.inputKey,
        command.value
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "CONNECT_NODES": {
      const result = WorkflowService.connectNodes(
        source,
        command.fromId,
        command.toId
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "CONNECT_BRANCH": {
      const result = WorkflowService.connectBranch(
        source,
        command.fromId,
        command.toId,
        command.branchLabel
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "DISCONNECT_NODE": {
      const result = WorkflowService.disconnectNode(source, command.nodeId);
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "DISCONNECT_CONNECTION": {
      const result = WorkflowService.disconnectConnection(
        source,
        command.fromId,
        command.toId,
        command.branchLabel
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "CONVERT_ORPHAN_TO_REPORTER": {
      const result = WorkflowService.convertOrphanToReporter(
        source,
        command.orphanId,
        command.targetId,
        command.inputKey
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "DELETE_REPORTER": {
      const result = WorkflowService.deleteReporter(
        source,
        command.parentId,
        command.inputPath
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "ADD_VARIABLE": {
      const result = WorkflowService.addVariable(
        source,
        command.workflowName,
        command.name,
        command.value
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "UPDATE_VARIABLE": {
      const result = WorkflowService.updateVariable(
        source,
        command.workflowName,
        command.oldName,
        command.newName,
        command.value
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "DELETE_VARIABLE": {
      const result = WorkflowService.deleteVariable(
        source,
        command.workflowName,
        command.name
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "UPDATE_INTERFACE": {
      const result = WorkflowService.updateWorkflowInterface(
        source,
        command.workflowName,
        command.inputs,
        command.outputs
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "ADD_DYNAMIC_BRANCH": {
      const result = WorkflowService.addDynamicBranch(
        source,
        command.nodeId,
        command.branchPrefix
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "REMOVE_DYNAMIC_BRANCH": {
      const result = WorkflowService.removeDynamicBranch(
        source,
        command.nodeId,
        command.branchName
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "ADD_DYNAMIC_INPUT": {
      const result = WorkflowService.addDynamicInput(
        source,
        command.nodeId,
        command.inputPrefix
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "REMOVE_DYNAMIC_INPUT": {
      const result = WorkflowService.removeDynamicInput(
        source,
        command.nodeId,
        command.inputName
      );
      return {
        success: result.success,
        source: result.source,
      };
    }

    case "ADD_WORKFLOW_CALL_NODE": {
      const result = WorkflowService.addWorkflowCallNode(
        source,
        command.workflowName,
        command.params,
        command.targetWorkflow
      );
      return {
        success: result.nodeId !== null,
        source: result.source,
        nodeId: result.nodeId ?? undefined,
      };
    }

    default: {
      // Exhaustive check
      const _exhaustiveCheck: never = command;
      return {
        success: false,
        error: `Unknown command type: ${(_exhaustiveCheck as WorkflowCommand).type}`,
      };
    }
  }
}
