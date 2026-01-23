// useNodeOperations - Abstraction hook for node operations
// Uses WorkflowService for business logic

import { useCallback } from "react";
import { useWorkflowStore } from "../store";
import {
  addNode as addNodeService,
  deleteNode as deleteNodeService,
  duplicateNode as duplicateNodeService,
  updateNodeInput as updateNodeInputService,
  connectNodes as connectNodesService,
  disconnectNode as disconnectNodeService,
  connectBranch as connectBranchService,
  disconnectConnection as disconnectConnectionService,
  convertOrphanToReporter as convertOrphanToReporterService,
  deleteReporter as deleteReporterService,
} from "../services/workflow";
import type { OpcodeInterface } from "../api/types";

export function useNodeOperations() {
  const source = useWorkflowStore((state) => state.source);
  const setSource = useWorkflowStore((state) => state.setSource);
  const selectNode = useWorkflowStore((state) => state.selectNode);

  const addNode = useCallback(
    (opcode: OpcodeInterface, workflowName = "main") => {
      const result = addNodeService(source, opcode, workflowName);
      if (result.nodeId) {
        setSource(result.source);
        selectNode(result.nodeId);
      }
      return result.nodeId;
    },
    [source, setSource, selectNode],
  );

  const deleteNode = useCallback(
    (nodeId: string) => {
      const result = deleteNodeService(source, nodeId);
      if (result.success) {
        setSource(result.source);
        selectNode(null);
      }
      return result.success;
    },
    [source, setSource, selectNode],
  );

  const duplicateNode = useCallback(
    (nodeId: string) => {
      const result = duplicateNodeService(source, nodeId);
      if (result.nodeId) {
        setSource(result.source);
        selectNode(result.nodeId);
      }
      return result.nodeId;
    },
    [source, setSource, selectNode],
  );

  const updateNodeInput = useCallback(
    (nodeId: string, inputKey: string, newValue: string) => {
      const result = updateNodeInputService(source, nodeId, inputKey, newValue);
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const connectNodes = useCallback(
    (fromNodeId: string, toNodeId: string) => {
      const result = connectNodesService(source, fromNodeId, toNodeId);
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const disconnectNode = useCallback(
    (nodeId: string) => {
      const result = disconnectNodeService(source, nodeId);
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const connectBranch = useCallback(
    (fromNodeId: string, toNodeId: string, branchLabel: string) => {
      const result = connectBranchService(
        source,
        fromNodeId,
        toNodeId,
        branchLabel,
      );
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const disconnectConnection = useCallback(
    (fromNodeId: string, toNodeId: string, branchLabel?: string) => {
      const result = disconnectConnectionService(
        source,
        fromNodeId,
        toNodeId,
        branchLabel,
      );
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const convertOrphanToReporter = useCallback(
    (
      orphanNodeId: string,
      targetNodeId: string,
      inputKey: string,
      isCompatible: boolean | null,
    ) => {
      if (isCompatible === false) {
        if (
          !confirm(
            `Type mismatch detected. The orphan node's return type may not be compatible with the input "${inputKey}". Continue anyway?`,
          )
        ) {
          return false;
        }
      }
      const result = convertOrphanToReporterService(
        source,
        orphanNodeId,
        targetNodeId,
        inputKey,
      );
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  const deleteReporter = useCallback(
    (parentNodeId: string, inputPath: string[]) => {
      const result = deleteReporterService(source, parentNodeId, inputPath);
      if (result.success) {
        setSource(result.source);
      }
      return result.success;
    },
    [source, setSource],
  );

  return {
    addNode,
    deleteNode,
    duplicateNode,
    updateNodeInput,
    connectNodes,
    disconnectNode,
    connectBranch,
    disconnectConnection,
    convertOrphanToReporter,
    deleteReporter,
  };
}
