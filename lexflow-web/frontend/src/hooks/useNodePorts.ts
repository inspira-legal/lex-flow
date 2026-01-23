// Node port interaction hook - handles port mousedown/mouseup for wire connections

import { useCallback } from "react";
import { useUiStore, useWorkflowStore } from "../store";
import { NODE_WIDTH } from "../utils/wireUtils";

interface UseNodePortsProps {
  nodeId: string;
  x: number;
  y: number;
}

interface UseNodePortsReturn {
  handleOutputPortMouseDown: (e: React.MouseEvent) => void;
  handleInputPortMouseDown: (e: React.MouseEvent) => void;
  handleOutputPortMouseUp: (e: React.MouseEvent) => void;
  handleInputPortMouseUp: (e: React.MouseEvent) => void;
  handleBranchPortMouseDown: (
    e: React.MouseEvent,
    branchName: string,
    portX: number,
    portY: number,
  ) => void;
  isInputPortHighlighted: boolean;
  isOutputPortHighlighted: boolean;
  isValidDropTarget: boolean;
  isValidOutputDropTarget: boolean;
}

export function useNodePorts({
  nodeId,
  x,
  y,
}: UseNodePortsProps): UseNodePortsReturn {
  const { draggingWire, setDraggingWire } = useUiStore();
  const { connectNodes } = useWorkflowStore();

  // Handle dragging from output port
  const handleOutputPortMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      const outputX = x + NODE_WIDTH;
      const outputY = y + 30;
      setDraggingWire({
        sourceNodeId: nodeId,
        sourcePort: "output",
        sourceX: outputX,
        sourceY: outputY,
        dragX: outputX,
        dragY: outputY,
        nearbyPort: null,
      });
    },
    [nodeId, x, y, setDraggingWire],
  );

  // Handle dragging from a branch port
  const handleBranchPortMouseDown = useCallback(
    (
      e: React.MouseEvent,
      branchName: string,
      portX: number,
      portY: number,
    ) => {
      e.stopPropagation();
      e.preventDefault();
      const outputX = x + portX;
      const outputY = y + portY;
      setDraggingWire({
        sourceNodeId: nodeId,
        sourcePort: "output",
        sourceX: outputX,
        sourceY: outputY,
        dragX: outputX,
        dragY: outputY,
        nearbyPort: null,
        branchLabel: branchName,
      });
    },
    [nodeId, x, y, setDraggingWire],
  );

  // Handle dragging from input port (reverse direction)
  const handleInputPortMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      const inputX = x;
      const inputY = y + 30;
      setDraggingWire({
        sourceNodeId: nodeId,
        sourcePort: "input",
        sourceX: inputX,
        sourceY: inputY,
        dragX: inputX,
        dragY: inputY,
        nearbyPort: null,
      });
    },
    [nodeId, x, y, setDraggingWire],
  );

  // Handle completing connection when dragging from input to output
  const handleOutputPortMouseUp = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      if (
        draggingWire &&
        draggingWire.sourcePort === "input" &&
        draggingWire.sourceNodeId !== nodeId
      ) {
        connectNodes(nodeId, draggingWire.sourceNodeId);
        setDraggingWire(null);
      }
    },
    [nodeId, draggingWire, connectNodes, setDraggingWire],
  );

  // Handle dropping on input port
  const handleInputPortMouseUp = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      if (
        draggingWire &&
        draggingWire.sourcePort === "output" &&
        draggingWire.sourceNodeId !== nodeId
      ) {
        connectNodes(draggingWire.sourceNodeId, nodeId);
        setDraggingWire(null);
      }
    },
    [nodeId, draggingWire, connectNodes, setDraggingWire],
  );

  // Check if ports should be highlighted based on proximity
  const isInputPortHighlighted =
    draggingWire?.nearbyPort?.nodeId === nodeId &&
    draggingWire?.nearbyPort?.port === "input";

  const isOutputPortHighlighted =
    draggingWire?.nearbyPort?.nodeId === nodeId &&
    draggingWire?.nearbyPort?.port === "output";

  // Check if this node is a valid drop target
  const isValidDropTarget =
    !!draggingWire &&
    draggingWire.sourcePort === "output" &&
    draggingWire.sourceNodeId !== nodeId;

  const isValidOutputDropTarget =
    !!draggingWire &&
    draggingWire.sourcePort === "input" &&
    draggingWire.sourceNodeId !== nodeId;

  return {
    handleOutputPortMouseDown,
    handleInputPortMouseDown,
    handleOutputPortMouseUp,
    handleInputPortMouseUp,
    handleBranchPortMouseDown,
    isInputPortHighlighted,
    isOutputPortHighlighted,
    isValidDropTarget,
    isValidOutputDropTarget,
  };
}
