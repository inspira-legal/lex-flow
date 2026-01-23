// useWorkflowState - Abstraction hook for workflow state

import { useWorkflowStore } from "../store";

export function useWorkflowState() {
  const source = useWorkflowStore((state) => state.source);
  const setSource = useWorkflowStore((state) => state.setSource);
  const tree = useWorkflowStore((state) => state.tree);
  const setTree = useWorkflowStore((state) => state.setTree);
  const parseError = useWorkflowStore((state) => state.parseError);
  const setParseError = useWorkflowStore((state) => state.setParseError);
  const isParsing = useWorkflowStore((state) => state.isParsing);
  const setIsParsing = useWorkflowStore((state) => state.setIsParsing);
  const canUndo = useWorkflowStore((state) => state.canUndo);
  const canRedo = useWorkflowStore((state) => state.canRedo);
  const undo = useWorkflowStore((state) => state.undo);
  const redo = useWorkflowStore((state) => state.redo);
  const opcodes = useWorkflowStore((state) => state.opcodes);
  const setOpcodes = useWorkflowStore((state) => state.setOpcodes);
  const examples = useWorkflowStore((state) => state.examples);
  const setExamples = useWorkflowStore((state) => state.setExamples);

  return {
    // Source
    source,
    setSource,

    // Tree
    tree,
    setTree,
    parseError,
    setParseError,
    isParsing,
    setIsParsing,

    // History
    canUndo,
    canRedo,
    undo,
    redo,

    // Catalogs
    opcodes,
    setOpcodes,
    examples,
    setExamples,
  };
}
