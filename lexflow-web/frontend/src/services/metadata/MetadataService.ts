// Service for extracting and injecting editor metadata in workflow YAML files

import yaml from "js-yaml";

export interface EditorMetadata {
  version: string;
  layout: {
    mode: "auto" | "free";
    nodePositions: Record<string, { x: number; y: number }>;
    workflowPositions: Record<string, { x: number; y: number }>;
  };
  viewport: {
    zoom: number;
    panX: number;
    panY: number;
  };
}

interface WorkflowDocument {
  metadata?: {
    editor?: EditorMetadata;
  };
  workflows?: unknown[];
}

const CURRENT_VERSION = "1.0";

export function extractMetadata(source: string): EditorMetadata | null {
  try {
    const doc = yaml.load(source) as WorkflowDocument | null;
    if (!doc?.metadata?.editor) return null;

    const editor = doc.metadata.editor;

    // Validate structure
    if (typeof editor.version !== "string") return null;
    if (!editor.layout || !editor.viewport) return null;

    return editor;
  } catch {
    return null;
  }
}

export function injectMetadata(
  source: string,
  metadata: EditorMetadata,
): string {
  try {
    const doc = yaml.load(source) as WorkflowDocument | null;
    if (!doc) return source;

    // Add or update metadata
    doc.metadata = {
      ...doc.metadata,
      editor: metadata,
    };

    // Dump back to YAML with metadata at the end
    return yaml.dump(doc, {
      indent: 2,
      lineWidth: -1, // Don't wrap lines
      noRefs: true,
      sortKeys: (a, b) => {
        // Ensure metadata comes after workflows
        if (a === "metadata") return 1;
        if (b === "metadata") return -1;
        return 0;
      },
    });
  } catch {
    return source;
  }
}

export function createMetadataFromState(
  layoutMode: "auto" | "free",
  nodePositions: Record<string, { x: number; y: number }>,
  workflowPositions: Record<string, { x: number; y: number }>,
  zoom: number,
  panX: number,
  panY: number,
): EditorMetadata {
  return {
    version: CURRENT_VERSION,
    layout: {
      mode: layoutMode,
      nodePositions: { ...nodePositions },
      workflowPositions: { ...workflowPositions },
    },
    viewport: {
      zoom,
      panX,
      panY,
    },
  };
}
