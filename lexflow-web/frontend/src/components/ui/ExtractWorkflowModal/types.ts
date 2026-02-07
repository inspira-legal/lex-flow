import type { DetailedInput } from "@/api/types";

export interface ExtractWorkflowModalProps {
  isOpen: boolean;
  existingWorkflowNames: string[];
  nodeIds: string[];
  suggestedInputs: string[];
  suggestedOutputs: string[];
  onConfirm: (data: ExtractWorkflowData) => void;
  onCancel: () => void;
}

export interface ExtractWorkflowData {
  name: string;
  inputs: DetailedInput[];
  outputs: string[];
  variables: Record<string, unknown>;
}
