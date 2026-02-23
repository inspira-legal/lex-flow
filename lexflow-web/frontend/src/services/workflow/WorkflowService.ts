// WorkflowService - Business logic for YAML workflow manipulation
// Pure functions that take source and return modified source

import type { OpcodeInterface, DetailedInput } from "../../api/types";

export interface NodeResult {
  source: string;
  nodeId: string | null;
}

export interface OperationResult {
  source: string;
  success: boolean;
}

// Helper to format value for YAML
export function formatYamlValue(value: unknown): string {
  if (value === null) return "null";
  if (value === undefined) return "null";
  if (typeof value === "string") {
    if (
      value === "" ||
      value.includes(":") ||
      value.includes("#") ||
      value.includes("\n") ||
      value.startsWith(" ") ||
      value.endsWith(" ") ||
      /^[[{}>|*&!%@`]/.test(value)
    ) {
      return JSON.stringify(value);
    }
    if (
      /^-?\d+(\.\d+)?$/.test(value) ||
      value === "true" ||
      value === "false" ||
      value === "null"
    ) {
      return JSON.stringify(value);
    }
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return JSON.stringify(value);
}

// Find the line range for a specific workflow's nodes section
function findWorkflowNodesRange(
  source: string,
  workflowName: string,
): { startLine: number; endLine: number; nodesIndent: number } | null {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let nodesStartLine = -1;
  let nodesIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Track which workflow we're in
    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
    }

    // Find the nodes section within the target workflow
    if (inTargetWorkflow) {
      const nodesMatch = line.match(/^(\s*)nodes:\s*$/);
      if (nodesMatch) {
        nodesStartLine = i;
        nodesIndent = nodesMatch[1].length;

        // Find where the nodes section ends
        let nodesEndLine = i + 1;
        while (nodesEndLine < lines.length) {
          const nextLine = lines[nodesEndLine];
          if (nextLine.trim() === "" || nextLine.trim().startsWith("#")) {
            nodesEndLine++;
            continue;
          }
          const nextIndent = nextLine.search(/\S/);
          if (nextIndent !== -1 && nextIndent <= nodesIndent) {
            break;
          }
          nodesEndLine++;
        }

        return {
          startLine: nodesStartLine,
          endLine: nodesEndLine,
          nodesIndent,
        };
      }
    }
  }

  return null;
}

// Find node line range in source, optionally scoped to a specific workflow
export function findNodeLineRange(
  source: string,
  nodeId: string,
  workflowName?: string,
): { startLine: number; endLine: number; indent: number } | null {
  const lines = source.split("\n");

  let searchStartLine = 0;
  let searchEndLine = lines.length;

  // If workflow name is specified, only search within that workflow's nodes section
  if (workflowName) {
    const workflowRange = findWorkflowNodesRange(source, workflowName);
    if (!workflowRange) return null;
    searchStartLine = workflowRange.startLine;
    searchEndLine = workflowRange.endLine;
  }

  let nodeStartLine = -1;
  let nodeIndent = -1;

  for (let i = searchStartLine; i < searchEndLine; i++) {
    const line = lines[i];
    const match = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
    if (match && match[2] === nodeId) {
      nodeStartLine = i;
      nodeIndent = match[1].length;
      break;
    }
  }

  if (nodeStartLine === -1) return null;

  let nodeEndLine = nodeStartLine + 1;
  while (nodeEndLine < lines.length) {
    const line = lines[nodeEndLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      nodeEndLine++;
      continue;
    }
    const currentIndent = line.search(/\S/);
    if (currentIndent !== -1 && currentIndent <= nodeIndent) {
      break;
    }
    nodeEndLine++;
  }

  return { startLine: nodeStartLine, endLine: nodeEndLine, indent: nodeIndent };
}

// Generate unique node ID based on existing IDs in source
export function generateUniqueNodeId(source: string, prefix: string): string {
  const lines = source.split("\n");
  const existingIds = new Set<string>();

  for (const line of lines) {
    const match = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
    if (match) existingIds.add(match[1]);
  }

  let newId = `${prefix}_1`;
  let counter = 1;
  while (existingIds.has(newId)) {
    counter++;
    newId = `${prefix}_${counter}`;
  }

  return newId;
}

// Delete a node from the source
export function deleteNode(source: string, nodeId: string): OperationResult {
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  const lines = source.split("\n");
  const newLines = [
    ...lines.slice(0, range.startLine),
    ...lines.slice(range.endLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Add a new node to a workflow
export function addNode(
  source: string,
  opcode: OpcodeInterface,
  workflowName = "main",
): NodeResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let nodesLineIndex = -1;
  let nodesIndent = -1;
  let lastNodeEndIndex = -1;
  let lastNodeIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
    }

    if (inTargetWorkflow) {
      const nodesMatch = line.match(/^(\s*)nodes:\s*$/);
      if (nodesMatch) {
        nodesLineIndex = i;
        nodesIndent = nodesMatch[1].length;
        continue;
      }

      if (nodesLineIndex !== -1) {
        const nodeIdMatch = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
        if (nodeIdMatch) {
          const indent = nodeIdMatch[1].length;
          if (indent === nodesIndent + 2) {
            lastNodeIndent = indent;
            let j = i + 1;
            while (j < lines.length) {
              const nextLine = lines[j];
              if (nextLine.trim() === "" || nextLine.trim().startsWith("#")) {
                j++;
                continue;
              }
              const nextIndent = nextLine.search(/\S/);
              if (nextIndent !== -1 && nextIndent <= indent) {
                break;
              }
              j++;
            }
            lastNodeEndIndex = j;
          }
        }
      }
    }
  }

  if (nodesLineIndex === -1) {
    return { source, nodeId: null };
  }

  const prefix = opcode.name.split("_")[0];
  const newId = generateUniqueNodeId(source, prefix);

  const indent = " ".repeat(
    lastNodeIndent !== -1 ? lastNodeIndent : nodesIndent + 2,
  );
  const inputIndent = indent + "  ";
  const valueIndent = inputIndent + "  ";

  let nodeYaml = `${indent}${newId}:\n`;
  nodeYaml += `${inputIndent}opcode: ${opcode.name}\n`;
  nodeYaml += `${inputIndent}next: null\n`;

  if (opcode.parameters.length > 0) {
    nodeYaml += `${inputIndent}inputs:\n`;
    for (const param of opcode.parameters) {
      const paramName = param.name.toUpperCase();
      const defaultValue =
        param.default !== undefined ? JSON.stringify(param.default) : '""';
      nodeYaml += `${valueIndent}${paramName}: { literal: ${defaultValue} }\n`;
    }
  }

  const insertIndex =
    lastNodeEndIndex !== -1 ? lastNodeEndIndex : nodesLineIndex + 1;

  const newLines = [
    ...lines.slice(0, insertIndex),
    nodeYaml.trimEnd(),
    ...lines.slice(insertIndex),
  ];

  return { source: newLines.join("\n"), nodeId: newId };
}

// Add a new node and connect it to an existing source node
export function addNodeAndConnect(
  source: string,
  opcode: OpcodeInterface,
  sourceNodeId: string,
  workflowName = "main",
): NodeResult & { success: boolean } {
  // Step 1: Add the new node
  const addResult = addNode(source, opcode, workflowName);
  if (!addResult.nodeId) {
    return { source, nodeId: null, success: false };
  }

  // Step 2: Connect source node's next to the new node
  const connectResult = connectNodes(
    addResult.source,
    sourceNodeId,
    addResult.nodeId,
    workflowName
  );
  if (!connectResult.success) {
    return { source, nodeId: null, success: false };
  }

  return {
    source: connectResult.source,
    nodeId: addResult.nodeId,
    success: true,
  };
}

// Duplicate an existing node
export function duplicateNode(source: string, nodeId: string): NodeResult {
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, nodeId: null };
  }

  const lines = source.split("\n");
  const nodeLines = lines.slice(range.startLine, range.endLine);

  let newId = `${nodeId}_copy`;
  let counter = 1;
  const existingIds = new Set<string>();
  for (const line of lines) {
    const match = line.match(/^\s+([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
    if (match) existingIds.add(match[1]);
  }
  while (existingIds.has(newId)) {
    counter++;
    newId = `${nodeId}_copy_${counter}`;
  }

  const newNodeLines = [...nodeLines];
  newNodeLines[0] = newNodeLines[0].replace(nodeId + ":", newId + ":");

  for (let i = 1; i < newNodeLines.length; i++) {
    if (newNodeLines[i].match(/^\s+next:\s*\S/)) {
      const indent = newNodeLines[i].match(/^(\s+)next:/)?.[1] || "        ";
      newNodeLines[i] = `${indent}next: null`;
    }
  }

  const newLines = [
    ...lines.slice(0, range.endLine),
    ...newNodeLines,
    ...lines.slice(range.endLine),
  ];

  return { source: newLines.join("\n"), nodeId: newId };
}

// Update a node's input value
export function updateNodeInput(
  source: string,
  nodeId: string,
  inputKey: string,
  newValue: string,
): OperationResult {
  const lines = source.split("\n");

  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  let inputsLineIndex = -1;
  let targetInputLine = -1;
  let targetInputIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];

    if (line.match(/^\s+inputs:\s*$/)) {
      inputsLineIndex = i;
      continue;
    }

    if (inputsLineIndex !== -1) {
      const inputMatch = line.match(
        new RegExp(`^(\\s+)(${inputKey}):\\s*(.*)$`),
      );
      if (inputMatch) {
        targetInputLine = i;
        targetInputIndent = inputMatch[1].length;
        break;
      }
    }
  }

  if (targetInputLine === -1) {
    return { source, success: false };
  }

  // Find where this input value ends (handles multi-line block format YAML)
  // Value ends when we hit a line with indent <= targetInputIndent (sibling or parent)
  let inputValueEndLine = targetInputLine + 1;
  while (inputValueEndLine < lines.length) {
    const line = lines[inputValueEndLine];
    // Empty lines or comments within the value block
    if (line.trim() === "" || line.trim().startsWith("#")) {
      inputValueEndLine++;
      continue;
    }
    const lineIndent = line.search(/\S/);
    // If indent is <= the input key's indent, we've left the value block
    if (lineIndent !== -1 && lineIndent <= targetInputIndent) {
      break;
    }
    inputValueEndLine++;
  }

  let formattedValue: string;
  if (newValue.startsWith("$")) {
    formattedValue = `{ variable: "${newValue.slice(1)}" }`;
  } else {
    try {
      const parsed = JSON.parse(newValue);
      formattedValue = `{ literal: ${JSON.stringify(parsed)} }`;
    } catch {
      formattedValue = `{ literal: "${newValue}" }`;
    }
  }

  const indent = " ".repeat(targetInputIndent);
  const newLines = [
    ...lines.slice(0, targetInputLine),
    `${indent}${inputKey}: ${formattedValue}`,
    ...lines.slice(inputValueEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Connect two nodes via next pointer
export function connectNodes(
  source: string,
  fromNodeId: string,
  toNodeId: string,
  workflowName?: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, fromNodeId, workflowName);
  if (!range) {
    return { source, success: false };
  }

  let nextLineIndex = -1;
  for (let i = range.startLine + 1; i < range.endLine; i++) {
    if (lines[i].match(/^\s+next:\s*/)) {
      nextLineIndex = i;
      break;
    }
  }

  const inputIndent = " ".repeat(range.indent + 2);

  if (nextLineIndex !== -1) {
    lines[nextLineIndex] = `${inputIndent}next: ${toNodeId}`;
  } else {
    let insertIndex = range.startLine + 1;
    while (insertIndex < range.endLine) {
      const line = lines[insertIndex];
      if (line.trim() !== "" && !line.trim().startsWith("#")) {
        break;
      }
      insertIndex++;
    }
    lines.splice(insertIndex, 0, `${inputIndent}next: ${toNodeId}`);
  }

  return { source: lines.join("\n"), success: true };
}

// Disconnect a node (set next to null)
export function disconnectNode(
  source: string,
  nodeId: string,
  workflowName?: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, nodeId, workflowName);
  if (!range) {
    return { source, success: false };
  }

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    if (lines[i].match(/^\s+next:\s*/)) {
      const indent =
        lines[i].match(/^(\s+)next:/)?.[1] || " ".repeat(range.indent + 2);
      lines[i] = `${indent}next: null`;
      return { source: lines.join("\n"), success: true };
    }
  }

  return { source, success: true };
}

// Connect a branch (THEN, ELSE, BODY, TRY, CATCH, FINALLY)
export function connectBranch(
  source: string,
  fromNodeId: string,
  toNodeId: string,
  branchLabel: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, fromNodeId);
  if (!range) {
    return { source, success: false };
  }

  let inputsLine = -1;
  let inputsIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const inputsMatch = line.match(/^(\s+)inputs:\s*$/);
    if (inputsMatch) {
      inputsLine = i;
      inputsIndent = inputsMatch[1].length;
      break;
    }
  }

  if (inputsLine === -1) {
    return { source, success: false };
  }

  const isCatchBranch = branchLabel.startsWith("CATCH");
  const branchIndent = " ".repeat(inputsIndent + 2);
  const branchValueIndent = " ".repeat(inputsIndent + 4);

  let branchLabelLine = -1;
  let inlineBranchLine = -1; // Track inline format like: BODY: { literal: null }
  let inputsEndLine = inputsLine + 1;

  while (inputsEndLine < lines.length) {
    const line = lines[inputsEndLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      inputsEndLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= inputsIndent && line.trim()) break;

    // Check for block-style label: BODY:
    const labelMatch = line.match(/^\s+([A-Z]+\d*):\s*$/);
    if (labelMatch && labelMatch[1] === branchLabel) {
      branchLabelLine = inputsEndLine;
      break;
    }

    // Check for inline-style label: BODY: { literal: null } or BODY: { branch: xyz }
    const inlineMatch = line.match(/^\s+([A-Z]+\d*):\s*\{.*\}\s*$/);
    if (inlineMatch && inlineMatch[1] === branchLabel) {
      inlineBranchLine = inputsEndLine;
      break;
    }
    inputsEndLine++;
  }

  if (branchLabelLine !== -1) {
    const branchLabelIndent =
      lines[branchLabelLine].match(/^(\s*)/)?.[1].length || 0;
    let searchLine = branchLabelLine + 1;

    if (isCatchBranch) {
      let bodyLine = -1;
      while (searchLine < lines.length) {
        const line = lines[searchLine];
        if (line.trim() === "" || line.trim().startsWith("#")) {
          searchLine++;
          continue;
        }
        const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
        if (lineIndent <= branchLabelIndent && line.trim()) break;
        if (line.match(/^\s+body:\s*$/)) {
          bodyLine = searchLine;
          break;
        }
        searchLine++;
      }

      if (bodyLine !== -1) {
        const bodyIndent = lines[bodyLine].match(/^(\s*)/)?.[1].length || 0;
        let bodySearchLine = bodyLine + 1;
        while (bodySearchLine < lines.length) {
          const line = lines[bodySearchLine];
          if (line.trim() === "" || line.trim().startsWith("#")) {
            bodySearchLine++;
            continue;
          }
          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
          if (lineIndent <= bodyIndent && line.trim()) break;
          const branchMatch = line.match(/^(\s+)branch:\s*/);
          if (branchMatch) {
            lines[bodySearchLine] = `${branchMatch[1]}branch: ${toNodeId}`;
            return { source: lines.join("\n"), success: true };
          }
          bodySearchLine++;
        }
        const bodyBranchIndent = " ".repeat(bodyIndent + 2);
        lines.splice(bodyLine + 1, 0, `${bodyBranchIndent}branch: ${toNodeId}`);
        return { source: lines.join("\n"), success: true };
      } else {
        const catchBodyIndent = " ".repeat(branchLabelIndent + 2);
        const catchBranchIndent = " ".repeat(branchLabelIndent + 4);
        let insertLine = branchLabelLine + 1;
        while (insertLine < lines.length) {
          const line = lines[insertLine];
          if (line.trim() === "" || line.trim().startsWith("#")) {
            insertLine++;
            continue;
          }
          const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
          if (lineIndent <= branchLabelIndent && line.trim()) break;
          insertLine++;
        }
        lines.splice(
          insertLine,
          0,
          `${catchBodyIndent}body:`,
          `${catchBranchIndent}branch: ${toNodeId}`,
        );
        return { source: lines.join("\n"), success: true };
      }
    } else {
      while (searchLine < lines.length) {
        const line = lines[searchLine];
        if (line.trim() === "" || line.trim().startsWith("#")) {
          searchLine++;
          continue;
        }
        const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
        if (lineIndent <= branchLabelIndent && line.trim()) break;

        const branchMatch = line.match(/^(\s+)branch:\s*/);
        if (branchMatch) {
          lines[searchLine] = `${branchMatch[1]}branch: ${toNodeId}`;
          return { source: lines.join("\n"), success: true };
        }
        searchLine++;
      }
      lines.splice(
        branchLabelLine + 1,
        0,
        `${branchValueIndent}branch: ${toNodeId}`,
      );
      return { source: lines.join("\n"), success: true };
    }
  } else if (inlineBranchLine !== -1) {
    // Handle inline format: BODY: { literal: null } -> convert to block format
    const inlineIndent =
      lines[inlineBranchLine].match(/^(\s*)/)?.[1].length || 0;
    const valueIndent = " ".repeat(inlineIndent + 2);

    if (isCatchBranch) {
      // For CATCH branches, create the full CATCH structure
      const catchBodyIndent = " ".repeat(inlineIndent + 2);
      const catchBranchIndent = " ".repeat(inlineIndent + 4);
      lines.splice(
        inlineBranchLine,
        1, // Remove the inline line
        `${" ".repeat(inlineIndent)}${branchLabel}:`,
        `${catchBodyIndent}exception_type: "Exception"`,
        `${catchBodyIndent}body:`,
        `${catchBranchIndent}branch: ${toNodeId}`,
      );
    } else {
      // For non-CATCH branches (BODY, THEN, ELSE, FINALLY), convert to block format
      lines.splice(
        inlineBranchLine,
        1, // Remove the inline line
        `${" ".repeat(inlineIndent)}${branchLabel}:`,
        `${valueIndent}branch: ${toNodeId}`,
      );
    }
    return { source: lines.join("\n"), success: true };
  } else {
    if (isCatchBranch) {
      const catchBodyIndent = " ".repeat(inputsIndent + 4);
      const catchBranchIndent = " ".repeat(inputsIndent + 6);
      lines.splice(
        inputsEndLine,
        0,
        `${branchIndent}${branchLabel}:`,
        `${catchBodyIndent}exception_type: "Exception"`,
        `${catchBodyIndent}body:`,
        `${catchBranchIndent}branch: ${toNodeId}`,
      );
    } else {
      lines.splice(
        inputsEndLine,
        0,
        `${branchIndent}${branchLabel}:`,
        `${branchValueIndent}branch: ${toNodeId}`,
      );
    }
    return { source: lines.join("\n"), success: true };
  }
}

// Disconnect a specific connection
export function disconnectConnection(
  source: string,
  fromNodeId: string,
  toNodeId: string,
  branchLabel?: string,
  workflowName?: string,
): OperationResult {
  if (!branchLabel) {
    return disconnectNode(source, fromNodeId, workflowName);
  }

  const lines = source.split("\n");
  const range = findNodeLineRange(source, fromNodeId, workflowName);
  if (!range) {
    return { source, success: false };
  }

  let inputsLine = -1;
  let inputsIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const inputsMatch = line.match(/^(\s+)inputs:\s*$/);
    if (inputsMatch) {
      inputsLine = i;
      inputsIndent = inputsMatch[1].length;
      break;
    }
  }

  if (inputsLine === -1) {
    return { source, success: false };
  }

  const isCatchBranch = branchLabel.startsWith("CATCH");
  let branchLabelLine = -1;
  let searchLine = inputsLine + 1;

  while (searchLine < lines.length) {
    const line = lines[searchLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      searchLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= inputsIndent && line.trim()) break;

    const labelMatch = line.match(/^\s+([A-Z]+\d*):\s*$/);
    if (labelMatch && labelMatch[1] === branchLabel) {
      branchLabelLine = searchLine;
      break;
    }
    searchLine++;
  }

  if (branchLabelLine === -1) {
    return { source, success: false };
  }

  const branchLabelIndent =
    lines[branchLabelLine].match(/^(\s*)/)?.[1].length || 0;
  let branchLineIndex = branchLabelLine + 1;

  while (branchLineIndex < lines.length) {
    const line = lines[branchLineIndex];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      branchLineIndex++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= branchLabelIndent && line.trim()) break;

    if (isCatchBranch) {
      const bodyMatch = line.match(/^(\s+)body:\s*$/);
      if (bodyMatch) {
        const bodyIndent = bodyMatch[1].length;
        let bodyLine = branchLineIndex + 1;
        while (bodyLine < lines.length) {
          const innerLine = lines[bodyLine];
          if (innerLine.trim() === "" || innerLine.trim().startsWith("#")) {
            bodyLine++;
            continue;
          }
          const innerIndent = innerLine.match(/^(\s*)/)?.[1].length || 0;
          if (innerIndent <= bodyIndent && innerLine.trim()) break;
          const branchMatch = innerLine.match(/^(\s+)branch:\s*(\S+)/);
          if (branchMatch && branchMatch[2] === toNodeId) {
            const indent = branchMatch[1];
            lines[bodyLine] = `${indent}branch: null`;
            return { source: lines.join("\n"), success: true };
          }
          bodyLine++;
        }
      }
    } else {
      const branchMatch = line.match(/^(\s+)branch:\s*(\S+)/);
      if (branchMatch && branchMatch[2] === toNodeId) {
        const indent = branchMatch[1];
        lines[branchLineIndex] = `${indent}branch: null`;
        return { source: lines.join("\n"), success: true };
      }
    }
    branchLineIndex++;
  }

  return { source, success: false };
}

// Convert orphan node to reporter
export function convertOrphanToReporter(
  source: string,
  orphanNodeId: string,
  targetNodeId: string,
  inputKey: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, targetNodeId);
  if (!range) {
    return { source, success: false };
  }

  let inputsLineIndex = -1;
  let targetInputLine = -1;
  let targetInputIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    if (line.match(/^\s+inputs:\s*$/)) {
      inputsLineIndex = i;
      continue;
    }
    if (inputsLineIndex !== -1) {
      const inputMatch = line.match(
        new RegExp(`^(\\s+)(${inputKey}):\\s*(.*)$`),
      );
      if (inputMatch) {
        targetInputLine = i;
        targetInputIndent = inputMatch[1].length;
        break;
      }
    }
  }

  if (targetInputLine === -1) {
    return { source, success: false };
  }

  // Find where this input value ends (handles multi-line block format YAML)
  // Value ends when we hit a line with indent <= targetInputIndent (sibling or parent)
  let inputValueEndLine = targetInputLine + 1;
  while (inputValueEndLine < lines.length) {
    const line = lines[inputValueEndLine];
    // Empty lines or comments within the value block
    if (line.trim() === "" || line.trim().startsWith("#")) {
      inputValueEndLine++;
      continue;
    }
    const lineIndent = line.search(/\S/);
    // If indent is <= the input key's indent, we've left the value block
    if (lineIndent !== -1 && lineIndent <= targetInputIndent) {
      break;
    }
    inputValueEndLine++;
  }

  const indent = " ".repeat(targetInputIndent);
  const newLines = [
    ...lines.slice(0, targetInputLine),
    `${indent}${inputKey}: { node: "${orphanNodeId}" }`,
    ...lines.slice(inputValueEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Delete a reporter (replace with literal placeholder)
export function deleteReporter(
  source: string,
  parentNodeId: string,
  inputPath: string[],
): OperationResult {
  if (inputPath.length === 0) {
    return { source, success: false };
  }

  const lines = source.split("\n");
  const range = findNodeLineRange(source, parentNodeId);
  if (!range) {
    return { source, success: false };
  }

  let currentLine = range.startLine;
  let currentIndent = range.indent;
  let inputsSectionFound = false;

  for (let i = range.startLine + 1; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === "" || line.trim().startsWith("#")) continue;
    const lineIndent = line.search(/\S/);
    if (lineIndent !== -1 && lineIndent <= range.indent) break;
    if (line.match(/^\s+inputs:\s*$/)) {
      inputsSectionFound = true;
      currentLine = i;
      currentIndent = lineIndent;
      break;
    }
  }

  if (!inputsSectionFound) {
    return { source, success: false };
  }

  for (let pathIdx = 0; pathIdx < inputPath.length - 1; pathIdx++) {
    const pathKey = inputPath[pathIdx];
    let found = false;

    for (let i = currentLine + 1; i < lines.length; i++) {
      const line = lines[i];
      if (line.trim() === "" || line.trim().startsWith("#")) continue;
      const lineIndent = line.search(/\S/);
      if (lineIndent !== -1 && lineIndent <= currentIndent) break;

      const keyMatch = line.match(new RegExp(`^(\\s+)(${pathKey}):\\s*`));
      if (keyMatch) {
        currentLine = i;
        currentIndent = keyMatch[1].length;
        found = true;

        for (let j = i + 1; j < lines.length; j++) {
          const nestedLine = lines[j];
          if (nestedLine.trim() === "" || nestedLine.trim().startsWith("#"))
            continue;
          const nestedIndent = nestedLine.search(/\S/);
          if (nestedIndent !== -1 && nestedIndent <= currentIndent) break;
          if (nestedLine.match(/^\s+inputs:\s*$/)) {
            currentLine = j;
            currentIndent = nestedIndent;
            break;
          }
        }
        break;
      }
    }

    if (!found) {
      return { source, success: false };
    }
  }

  const targetKey = inputPath[inputPath.length - 1];
  let targetLine = -1;
  let targetIndent = -1;

  for (let i = currentLine + 1; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === "" || line.trim().startsWith("#")) continue;
    const lineIndent = line.search(/\S/);
    if (lineIndent !== -1 && lineIndent <= currentIndent) break;

    const keyMatch = line.match(new RegExp(`^(\\s+)(${targetKey}):\\s*`));
    if (keyMatch) {
      targetLine = i;
      targetIndent = keyMatch[1].length;
      break;
    }
  }

  if (targetLine === -1) {
    return { source, success: false };
  }

  let blockEndLine = targetLine + 1;
  while (blockEndLine < lines.length) {
    const line = lines[blockEndLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      blockEndLine++;
      continue;
    }
    const lineIndent = line.search(/\S/);
    if (lineIndent !== -1 && lineIndent <= targetIndent) break;
    blockEndLine++;
  }

  const indent = " ".repeat(targetIndent);
  const newLines = [
    ...lines.slice(0, targetLine),
    `${indent}${targetKey}: { literal: null }`,
    ...lines.slice(blockEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Format detailed inputs as multi-line YAML
function formatDetailedInputsYaml(
  inputs: DetailedInput[],
  baseIndent: string,
): string[] {
  if (inputs.length === 0) return [`${baseIndent}inputs: []`];
  const lines = [`${baseIndent}inputs:`];
  const itemIndent = baseIndent + "  ";
  for (const input of inputs) {
    lines.push(`${itemIndent}- name: "${input.name}"`);
    lines.push(`${itemIndent}  type: "${input.type}"`);
    lines.push(`${itemIndent}  required: ${input.required}`);
  }
  return lines;
}

// Update workflow interface
export function updateWorkflowInterface(
  source: string,
  workflowName: string,
  inputs: DetailedInput[],
  outputs: string[],
): OperationResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let interfaceStartLine = -1;
  let interfaceEndLine = -1;
  let interfaceIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
    }

    if (inTargetWorkflow) {
      const interfaceMatch = line.match(/^(\s*)interface:\s*$/);
      if (interfaceMatch) {
        interfaceStartLine = i;
        interfaceIndent = interfaceMatch[1].length;
        let j = i + 1;
        while (j < lines.length) {
          const nextLine = lines[j];
          if (nextLine.trim() === "" || nextLine.trim().startsWith("#")) {
            j++;
            continue;
          }
          const nextIndent = nextLine.search(/\S/);
          if (nextIndent !== -1 && nextIndent <= interfaceIndent) break;
          j++;
        }
        interfaceEndLine = j;
        break;
      }
    }
  }

  if (interfaceStartLine === -1) {
    return { source, success: false };
  }

  const indent = " ".repeat(interfaceIndent);
  const propIndent = " ".repeat(interfaceIndent + 2);
  const outputsStr =
    outputs.length > 0 ? `[${outputs.map((o) => `"${o}"`).join(", ")}]` : "[]";
  const newInterfaceYaml = [
    `${indent}interface:`,
    ...formatDetailedInputsYaml(inputs, propIndent),
    `${propIndent}outputs: ${outputsStr}`,
  ];

  const newLines = [
    ...lines.slice(0, interfaceStartLine),
    ...newInterfaceYaml,
    ...lines.slice(interfaceEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Add variable to workflow
export function addVariable(
  source: string,
  workflowName: string,
  name: string,
  defaultValue: unknown,
): OperationResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let variablesLine = -1;
  let variablesIndent = -1;
  let variablesEndLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
    }

    if (inTargetWorkflow) {
      const varsMatch = line.match(/^(\s*)variables:\s*(.*)$/);
      if (varsMatch) {
        variablesLine = i;
        variablesIndent = varsMatch[1].length;
        const restOfLine = varsMatch[2].trim();

        if (restOfLine === "{}" || restOfLine === "") {
          variablesEndLine = i + 1;
        } else {
          let j = i + 1;
          while (j < lines.length) {
            const nextLine = lines[j];
            if (nextLine.trim() === "" || nextLine.trim().startsWith("#")) {
              j++;
              continue;
            }
            const nextIndent = nextLine.search(/\S/);
            if (nextIndent !== -1 && nextIndent <= variablesIndent) break;
            j++;
          }
          variablesEndLine = j;
        }
        break;
      }
    }
  }

  if (variablesLine === -1) {
    return { source, success: false };
  }

  const varIndent = " ".repeat(variablesIndent + 2);
  const valueStr = formatYamlValue(defaultValue);

  if (lines[variablesLine].includes("{}")) {
    const indent = " ".repeat(variablesIndent);
    const newLines = [
      ...lines.slice(0, variablesLine),
      `${indent}variables:`,
      `${varIndent}${name}: ${valueStr}`,
      ...lines.slice(variablesLine + 1),
    ];
    return { source: newLines.join("\n"), success: true };
  } else {
    const newLines = [
      ...lines.slice(0, variablesEndLine),
      `${varIndent}${name}: ${valueStr}`,
      ...lines.slice(variablesEndLine),
    ];
    return { source: newLines.join("\n"), success: true };
  }
}

// Update variable in workflow
export function updateVariable(
  source: string,
  workflowName: string,
  oldName: string,
  newName: string,
  newValue: unknown,
): OperationResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let inVariables = false;
  let variablesIndent = -1;
  let varLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
      inVariables = false;
    }

    if (inTargetWorkflow) {
      const varsMatch = line.match(/^(\s*)variables:\s*/);
      if (varsMatch) {
        inVariables = true;
        variablesIndent = varsMatch[1].length;
        continue;
      }

      if (inVariables) {
        const lineIndent = line.search(/\S/);
        if (
          line.trim() !== "" &&
          !line.trim().startsWith("#") &&
          lineIndent !== -1 &&
          lineIndent <= variablesIndent
        ) {
          inVariables = false;
          continue;
        }

        const varMatch = line.match(new RegExp(`^(\\s+)${oldName}:\\s*(.*)$`));
        if (varMatch) {
          varLine = i;
          break;
        }
      }
    }
  }

  if (varLine === -1) {
    return { source, success: false };
  }

  const varIndent = lines[varLine].match(/^(\s+)/)?.[1] || "    ";
  const valueStr = formatYamlValue(newValue);
  lines[varLine] = `${varIndent}${newName}: ${valueStr}`;

  return { source: lines.join("\n"), success: true };
}

// Delete variable from workflow
export function deleteVariable(
  source: string,
  workflowName: string,
  name: string,
): OperationResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let inVariables = false;
  let variablesIndent = -1;
  let varLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === workflowName;
      inVariables = false;
    }

    if (inTargetWorkflow) {
      const varsMatch = line.match(/^(\s*)variables:\s*/);
      if (varsMatch) {
        inVariables = true;
        variablesIndent = varsMatch[1].length;
        continue;
      }

      if (inVariables) {
        const lineIndent = line.search(/\S/);
        if (
          line.trim() !== "" &&
          !line.trim().startsWith("#") &&
          lineIndent !== -1 &&
          lineIndent <= variablesIndent
        ) {
          inVariables = false;
          continue;
        }

        const varMatch = line.match(new RegExp(`^(\\s+)${name}:\\s*(.*)$`));
        if (varMatch) {
          varLine = i;
          break;
        }
      }
    }
  }

  if (varLine === -1) {
    return { source, success: false };
  }

  const newLines = [...lines.slice(0, varLine), ...lines.slice(varLine + 1)];
  return { source: newLines.join("\n"), success: true };
}

// Add a workflow_call node with properly named ARG inputs
export function addWorkflowCallNode(
  source: string,
  workflowName: string,
  params: string[],
  targetWorkflow = "main",
): NodeResult {
  const lines = source.split("\n");

  let inTargetWorkflow = false;
  let nodesLineIndex = -1;
  let nodesIndent = -1;
  let lastNodeEndIndex = -1;
  let lastNodeIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      inTargetWorkflow = nameMatch[1] === targetWorkflow;
    }

    if (inTargetWorkflow) {
      const nodesMatch = line.match(/^(\s*)nodes:\s*$/);
      if (nodesMatch) {
        nodesLineIndex = i;
        nodesIndent = nodesMatch[1].length;
        continue;
      }

      if (nodesLineIndex !== -1) {
        const nodeIdMatch = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
        if (nodeIdMatch) {
          const indent = nodeIdMatch[1].length;
          if (indent === nodesIndent + 2) {
            lastNodeIndent = indent;
            let j = i + 1;
            while (j < lines.length) {
              const nextLine = lines[j];
              if (nextLine.trim() === "" || nextLine.trim().startsWith("#")) {
                j++;
                continue;
              }
              const nextIndent = nextLine.search(/\S/);
              if (nextIndent !== -1 && nextIndent <= indent) {
                break;
              }
              j++;
            }
            lastNodeEndIndex = j;
          }
        }
      }
    }
  }

  if (nodesLineIndex === -1) {
    return { source, nodeId: null };
  }

  const newId = generateUniqueNodeId(source, `call_${workflowName}`);

  const indent = " ".repeat(
    lastNodeIndent !== -1 ? lastNodeIndent : nodesIndent + 2,
  );
  const inputIndent = indent + "  ";
  const valueIndent = inputIndent + "  ";

  let nodeYaml = `${indent}${newId}:\n`;
  nodeYaml += `${inputIndent}opcode: workflow_call\n`;
  nodeYaml += `${inputIndent}next: null\n`;
  nodeYaml += `${inputIndent}inputs:\n`;
  nodeYaml += `${valueIndent}WORKFLOW: { literal: "${workflowName}" }\n`;

  // Add ARG1, ARG2, etc. for each parameter
  params.forEach((_, i) => {
    nodeYaml += `${valueIndent}ARG${i + 1}: { literal: null }\n`;
  });

  const insertIndex =
    lastNodeEndIndex !== -1 ? lastNodeEndIndex : nodesLineIndex + 1;

  const newLines = [
    ...lines.slice(0, insertIndex),
    nodeYaml.trimEnd(),
    ...lines.slice(insertIndex),
  ];

  return { source: newLines.join("\n"), nodeId: newId };
}

// Add a dynamic branch to a control flow node (e.g., CATCH2 for try, BRANCH3 for fork)
export function addDynamicBranch(
  source: string,
  nodeId: string,
  branchPrefix: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  // Find the inputs section and existing branches
  let inputsLine = -1;
  let inputsIndent = -1;
  const existingBranches: string[] = [];

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const inputsMatch = line.match(/^(\s+)inputs:\s*$/);
    if (inputsMatch) {
      inputsLine = i;
      inputsIndent = inputsMatch[1].length;
      continue;
    }

    if (inputsLine !== -1) {
      // Look for existing branches matching the prefix
      const branchMatch = line.match(
        new RegExp(`^\\s+(${branchPrefix}\\d+):\\s*`),
      );
      if (branchMatch) {
        existingBranches.push(branchMatch[1]);
      }
    }
  }

  if (inputsLine === -1) {
    return { source, success: false };
  }

  // Find the next branch number
  let maxNum = 0;
  for (const branch of existingBranches) {
    const num = parseInt(branch.replace(branchPrefix, ""));
    if (num > maxNum) maxNum = num;
  }
  const newBranchName = `${branchPrefix}${maxNum + 1}`;

  // Find where to insert (after the last branch of this type, or at end of inputs)
  let insertLine = inputsLine + 1;
  while (insertLine < lines.length) {
    const line = lines[insertLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      insertLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= inputsIndent && line.trim()) break;
    insertLine++;
  }

  const branchIndent = " ".repeat(inputsIndent + 2);
  const valueIndent = " ".repeat(inputsIndent + 4);

  // For CATCH branches, add with exception_type and body structure
  let newBranchYaml: string[];
  if (branchPrefix === "CATCH") {
    const bodyIndent = " ".repeat(inputsIndent + 6);
    newBranchYaml = [
      `${branchIndent}${newBranchName}:`,
      `${valueIndent}exception_type: "Exception"`,
      `${valueIndent}body:`,
      `${bodyIndent}branch: null`,
    ];
  } else {
    // For BRANCH (fork) and others
    newBranchYaml = [
      `${branchIndent}${newBranchName}:`,
      `${valueIndent}branch: null`,
    ];
  }

  const newLines = [
    ...lines.slice(0, insertLine),
    ...newBranchYaml,
    ...lines.slice(insertLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Remove a dynamic branch from a control flow node
export function removeDynamicBranch(
  source: string,
  nodeId: string,
  branchName: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  // Find the branch label line
  let branchLabelLine = -1;
  let branchIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const labelMatch = line.match(new RegExp(`^(\\s+)${branchName}:\\s*`));
    if (labelMatch) {
      branchLabelLine = i;
      branchIndent = labelMatch[1].length;
      break;
    }
  }

  if (branchLabelLine === -1) {
    return { source, success: false };
  }

  // Find where this branch block ends
  let branchEndLine = branchLabelLine + 1;
  while (branchEndLine < lines.length) {
    const line = lines[branchEndLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      branchEndLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= branchIndent && line.trim()) break;
    branchEndLine++;
  }

  const newLines = [
    ...lines.slice(0, branchLabelLine),
    ...lines.slice(branchEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Add a dynamic input to a node (e.g., ARG3 for workflow_call)
export function addDynamicInput(
  source: string,
  nodeId: string,
  inputPrefix: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  // Find the inputs section and existing inputs
  let inputsLine = -1;
  let inputsIndent = -1;
  const existingInputs: string[] = [];

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const inputsMatch = line.match(/^(\s+)inputs:\s*$/);
    if (inputsMatch) {
      inputsLine = i;
      inputsIndent = inputsMatch[1].length;
      continue;
    }

    if (inputsLine !== -1) {
      // Look for existing inputs matching the prefix
      const inputMatch = line.match(
        new RegExp(`^\\s+(${inputPrefix}\\d+):\\s*`),
      );
      if (inputMatch) {
        existingInputs.push(inputMatch[1]);
      }
    }
  }

  if (inputsLine === -1) {
    return { source, success: false };
  }

  // Find the next input number
  let maxNum = 0;
  for (const input of existingInputs) {
    const num = parseInt(input.replace(inputPrefix, ""));
    if (num > maxNum) maxNum = num;
  }
  const newInputName = `${inputPrefix}${maxNum + 1}`;

  // Find where to insert (at end of inputs section)
  let insertLine = inputsLine + 1;
  while (insertLine < lines.length) {
    const line = lines[insertLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      insertLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= inputsIndent && line.trim()) break;
    insertLine++;
  }

  const inputIndent = " ".repeat(inputsIndent + 2);
  const newInputLine = `${inputIndent}${newInputName}: { literal: null }`;

  const newLines = [
    ...lines.slice(0, insertLine),
    newInputLine,
    ...lines.slice(insertLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Remove a dynamic input from a node
export function removeDynamicInput(
  source: string,
  nodeId: string,
  inputName: string,
): OperationResult {
  const lines = source.split("\n");
  const range = findNodeLineRange(source, nodeId);
  if (!range) {
    return { source, success: false };
  }

  // Find the input line
  let inputLine = -1;
  let inputIndent = -1;

  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const line = lines[i];
    const inputMatch = line.match(new RegExp(`^(\\s+)${inputName}:\\s*`));
    if (inputMatch) {
      inputLine = i;
      inputIndent = inputMatch[1].length;
      break;
    }
  }

  if (inputLine === -1) {
    return { source, success: false };
  }

  // Find where this input value ends (in case of multi-line)
  let inputEndLine = inputLine + 1;
  while (inputEndLine < lines.length) {
    const line = lines[inputEndLine];
    if (line.trim() === "" || line.trim().startsWith("#")) {
      inputEndLine++;
      continue;
    }
    const lineIndent = line.match(/^(\s*)/)?.[1].length || 0;
    if (lineIndent <= inputIndent && line.trim()) break;
    inputEndLine++;
  }

  const newLines = [...lines.slice(0, inputLine), ...lines.slice(inputEndLine)];

  return { source: newLines.join("\n"), success: true };
}

// Add a new workflow to the source
export function addWorkflow(
  source: string,
  name: string,
  inputs: DetailedInput[] = [],
  outputs: string[] = [],
  variables: Record<string, unknown> = {},
): OperationResult {
  // Validate workflow name is a valid identifier
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name)) {
    return { source, success: false };
  }

  // Check for duplicate workflow name
  const lines = source.split("\n");
  for (const line of lines) {
    const nameMatch = line.match(/^\s*-?\s*name:\s*(\w+)/);
    if (nameMatch && nameMatch[1] === name) {
      return { source, success: false };
    }
  }

  // Find the end of the workflows array
  let lastWorkflowEndLine = -1;
  let inWorkflows = false;
  let workflowIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Look for "workflows:" line
    const workflowsMatch = line.match(/^(\s*)workflows:\s*$/);
    if (workflowsMatch) {
      inWorkflows = true;
      workflowIndent = workflowsMatch[1].length;
      continue;
    }

    if (inWorkflows) {
      // Check if we've left the workflows section
      const lineIndent = line.search(/\S/);
      if (
        line.trim() !== "" &&
        lineIndent !== -1 &&
        lineIndent <= workflowIndent
      ) {
        break;
      }
      lastWorkflowEndLine = i;
    }
  }

  // If no workflows section found, can't add
  if (!inWorkflows) {
    return { source, success: false };
  }

  // Build the new workflow YAML with 2-space indentation
  const indent = "  ";
  const propIndent = "    ";
  const varIndent = "      ";

  const outputsStr =
    outputs.length > 0 ? `[${outputs.map((o) => `"${o}"`).join(", ")}]` : "[]";
  const inputsLines = formatDetailedInputsYaml(inputs, varIndent);

  let workflowYaml = `${indent}- name: ${name}\n`;
  workflowYaml += `${propIndent}interface:\n`;
  workflowYaml += inputsLines.map((l) => l + "\n").join("");
  workflowYaml += `${varIndent}outputs: ${outputsStr}\n`;

  // Add variables section
  const varEntries = Object.entries(variables);
  if (varEntries.length === 0) {
    workflowYaml += `${propIndent}variables: {}\n`;
  } else {
    workflowYaml += `${propIndent}variables:\n`;
    for (const [varName, varValue] of varEntries) {
      workflowYaml += `${varIndent}${varName}: ${formatYamlValue(varValue)}\n`;
    }
  }

  // Add nodes section with just a start node
  workflowYaml += `${propIndent}nodes:\n`;
  workflowYaml += `${varIndent}start:\n`;
  workflowYaml += `${varIndent}  next: null`;

  // Insert after the last workflow
  const insertLine = lastWorkflowEndLine + 1;
  const newLines = [
    ...lines.slice(0, insertLine),
    workflowYaml,
    ...lines.slice(insertLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// Delete a workflow from the source
export function deleteWorkflow(source: string, name: string): OperationResult {
  // Cannot delete "main" workflow
  if (name === "main") {
    return { source, success: false };
  }

  const lines = source.split("\n");

  // Find the workflow's starting line (- name: workflowName)
  let workflowStartLine = -1;
  let workflowIndent = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Match "  - name: workflowName" pattern
    const nameMatch = line.match(/^(\s*)-\s*name:\s*(\w+)/);
    if (nameMatch && nameMatch[2] === name) {
      workflowStartLine = i;
      workflowIndent = nameMatch[1].length;
      break;
    }
  }

  if (workflowStartLine === -1) {
    return { source, success: false };
  }

  // Find where this workflow ends (next workflow or end of workflows section)
  let workflowEndLine = workflowStartLine + 1;
  while (workflowEndLine < lines.length) {
    const line = lines[workflowEndLine];

    // Empty lines are part of the workflow
    if (line.trim() === "" || line.trim().startsWith("#")) {
      workflowEndLine++;
      continue;
    }

    const lineIndent = line.search(/\S/);

    // If we hit another workflow entry (same indent level with "- name:")
    const nextWorkflowMatch = line.match(/^(\s*)-\s*name:\s*\w+/);
    if (nextWorkflowMatch && nextWorkflowMatch[1].length === workflowIndent) {
      break;
    }

    // If we hit something at the same or lower indent that's not part of the workflow
    if (
      lineIndent !== -1 &&
      lineIndent <= workflowIndent &&
      !line.trim().startsWith("-")
    ) {
      break;
    }

    workflowEndLine++;
  }

  // Remove the workflow lines
  const newLines = [
    ...lines.slice(0, workflowStartLine),
    ...lines.slice(workflowEndLine),
  ];

  return { source: newLines.join("\n"), success: true };
}

// ====== Extract to Workflow Feature ======

export interface ChainValidationResult {
  isValid: boolean;
  orderedNodeIds: string[];
  firstNodeId: string | null;
  lastNodeId: string | null;
  predecessorNodeId: string | null; // Node before first selected
  successorNodeId: string | null; // Node after last selected
  errors: string[];
}

// Branching opcodes that cannot be extracted
const BRANCHING_OPCODES = [
  "control_if",
  "control_for",
  "control_for_each",
  "control_while",
  "control_repeat_until",
  "control_try",
  "control_fork",
];

// Find which workflow a node belongs to by searching the source
function findNodeWorkflow(source: string, nodeId: string): string | null {
  const lines = source.split("\n");
  let currentWorkflow: string | null = null;
  let inNodes = false;
  let workflowIndent = -1;

  for (const line of lines) {
    const nameMatch = line.match(/^(\s*)-?\s*name:\s*(\w+)/);
    if (nameMatch) {
      currentWorkflow = nameMatch[2];
      workflowIndent = nameMatch[1].length;
      inNodes = false;
    }

    const nodesMatch = line.match(/^(\s*)nodes:\s*$/);
    if (nodesMatch && currentWorkflow) {
      inNodes = true;
    }

    if (inNodes) {
      const nodeMatch = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
      if (nodeMatch && nodeMatch[2] === nodeId) {
        return currentWorkflow;
      }

      // Check if we've left the workflow
      const lineIndent = line.search(/\S/);
      if (line.trim() && lineIndent !== -1 && lineIndent <= workflowIndent) {
        inNodes = false;
      }
    }
  }

  return null;
}

// Get the opcode of a node
function getNodeOpcode(source: string, nodeId: string): string | null {
  const range = findNodeLineRange(source, nodeId);
  if (!range) return null;

  const lines = source.split("\n");
  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const opcodeMatch = lines[i].match(/^\s+opcode:\s*(\S+)/);
    if (opcodeMatch) {
      return opcodeMatch[1];
    }
  }
  return null;
}

// Get the next pointer of a node
function getNodeNext(
  source: string,
  nodeId: string,
  workflowName?: string,
): string | null {
  const range = findNodeLineRange(source, nodeId, workflowName);
  if (!range) return null;

  const lines = source.split("\n");
  for (let i = range.startLine + 1; i < range.endLine; i++) {
    const nextMatch = lines[i].match(/^\s+next:\s*(\S+)/);
    if (nextMatch) {
      const next = nextMatch[1];
      return next === "null" ? null : next;
    }
  }
  return null;
}

// Find node that points to a given node
function findPredecessor(
  source: string,
  nodeId: string,
  workflowName: string,
): string | null {
  const workflowRange = findWorkflowNodesRange(source, workflowName);
  if (!workflowRange) return null;

  const lines = source.split("\n");
  let currentNode: string | null = null;

  for (let i = workflowRange.startLine; i < workflowRange.endLine; i++) {
    const line = lines[i];

    // Track current node
    const nodeMatch = line.match(/^(\s+)([a-zA-Z_][a-zA-Z0-9_]*):\s*$/);
    if (nodeMatch) {
      currentNode = nodeMatch[2];
    }

    // Check next pointer
    const nextMatch = line.match(/^\s+next:\s*(\S+)/);
    if (nextMatch && nextMatch[1] === nodeId && currentNode) {
      return currentNode;
    }
  }

  return null;
}

// Find all reporter node IDs referenced by a set of nodes (recursively)
function findReporterNodes(source: string, nodeIds: string[]): string[] {
  const reporterIds: string[] = [];
  const visited = new Set<string>();

  function findReportersInNode(nodeId: string) {
    if (visited.has(nodeId)) return;
    visited.add(nodeId);

    const range = findNodeLineRange(source, nodeId);
    if (!range) return;

    const lines = source.split("\n");
    const nodeContent = lines.slice(range.startLine, range.endLine).join("\n");

    // Find all { node: "reporter_id" } or { node: reporter_id } references
    // Match both quoted and unquoted node IDs
    const quotedMatches = nodeContent.matchAll(
      /\{\s*node:\s*["']([^"']+)["']\s*\}/g,
    );
    for (const match of quotedMatches) {
      const reporterId = match[1];
      if (!reporterIds.includes(reporterId) && !nodeIds.includes(reporterId)) {
        reporterIds.push(reporterId);
        findReportersInNode(reporterId);
      }
    }

    // Also match unquoted node IDs: { node: some_id }
    const unquotedMatches = nodeContent.matchAll(
      /\{\s*node:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}/g,
    );
    for (const match of unquotedMatches) {
      const reporterId = match[1];
      if (!reporterIds.includes(reporterId) && !nodeIds.includes(reporterId)) {
        reporterIds.push(reporterId);
        findReportersInNode(reporterId);
      }
    }
  }

  for (const nodeId of nodeIds) {
    findReportersInNode(nodeId);
  }

  return reporterIds;
}

// Validate that selected nodes form a linear chain
export function validateLinearChain(
  source: string,
  nodeIds: string[],
  workflowName: string,
): ChainValidationResult {
  const errors: string[] = [];

  if (nodeIds.length < 2) {
    return {
      isValid: false,
      orderedNodeIds: [],
      firstNodeId: null,
      lastNodeId: null,
      predecessorNodeId: null,
      successorNodeId: null,
      errors: ["Select at least 2 nodes to extract"],
    };
  }

  // Verify all nodes are in the same workflow
  for (const nodeId of nodeIds) {
    const nodeWorkflow = findNodeWorkflow(source, nodeId);
    if (nodeWorkflow !== workflowName) {
      errors.push(`Node "${nodeId}" is not in workflow "${workflowName}"`);
    }
  }
  if (errors.length > 0) {
    return {
      isValid: false,
      orderedNodeIds: [],
      firstNodeId: null,
      lastNodeId: null,
      predecessorNodeId: null,
      successorNodeId: null,
      errors,
    };
  }

  // Check for branching opcodes
  for (const nodeId of nodeIds) {
    const opcode = getNodeOpcode(source, nodeId);
    if (opcode && BRANCHING_OPCODES.includes(opcode)) {
      errors.push(
        `Cannot extract "${nodeId}": branching nodes (${opcode}) are not supported`,
      );
    }
  }
  if (errors.length > 0) {
    return {
      isValid: false,
      orderedNodeIds: [],
      firstNodeId: null,
      lastNodeId: null,
      predecessorNodeId: null,
      successorNodeId: null,
      errors,
    };
  }

  // Build next pointer map for selected nodes
  const nodeSet = new Set(nodeIds);
  const nextMap: Record<string, string | null> = {};
  for (const nodeId of nodeIds) {
    nextMap[nodeId] = getNodeNext(source, nodeId, workflowName);
  }

  // Find the first node (one that no other selected node points to)
  const pointedTo = new Set(
    Object.values(nextMap).filter((n) => n && nodeSet.has(n)),
  );
  const candidates = nodeIds.filter((id) => !pointedTo.has(id));

  if (candidates.length !== 1) {
    return {
      isValid: false,
      orderedNodeIds: [],
      firstNodeId: null,
      lastNodeId: null,
      predecessorNodeId: null,
      successorNodeId: null,
      errors: ["Selected nodes do not form a single connected chain"],
    };
  }

  // Walk the chain and build ordered list
  const orderedNodeIds: string[] = [];
  let current: string | null = candidates[0];
  const visited = new Set<string>();

  while (current && nodeSet.has(current) && !visited.has(current)) {
    visited.add(current);
    orderedNodeIds.push(current);
    current = nextMap[current] || null;
  }

  // Verify all nodes are in the chain
  if (orderedNodeIds.length !== nodeIds.length) {
    return {
      isValid: false,
      orderedNodeIds: [],
      firstNodeId: null,
      lastNodeId: null,
      predecessorNodeId: null,
      successorNodeId: null,
      errors: [
        "Selected nodes are not contiguous (some nodes are disconnected)",
      ],
    };
  }

  const firstNodeId = orderedNodeIds[0];
  const lastNodeId = orderedNodeIds[orderedNodeIds.length - 1];

  // Find predecessor and successor
  const predecessorNodeId = findPredecessor(source, firstNodeId, workflowName);
  const successorNodeId = getNodeNext(source, lastNodeId, workflowName);

  return {
    isValid: true,
    orderedNodeIds,
    firstNodeId,
    lastNodeId,
    predecessorNodeId,
    successorNodeId,
    errors: [],
  };
}

export interface ChainVariables {
  suggestedInputs: string[];
  suggestedOutputs: string[];
}

// Analyze variables used and assigned in a chain of nodes
export function analyzeChainVariables(
  source: string,
  nodeIds: string[],
): ChainVariables {
  const variablesUsed = new Set<string>();
  const variablesSet = new Set<string>();

  for (const nodeId of nodeIds) {
    const range = findNodeLineRange(source, nodeId);
    if (!range) continue;

    const lines = source.split("\n");
    const nodeContent = lines.slice(range.startLine, range.endLine).join("\n");

    // Find variables referenced in inputs: { variable: "name" }
    const variableMatches = nodeContent.matchAll(
      /\{\s*variable:\s*["']([^"']+)["']\s*\}/g,
    );
    for (const match of variableMatches) {
      variablesUsed.add(match[1]);
    }

    // Find variables being set via data_set_variable_to opcode
    const opcode = getNodeOpcode(source, nodeId);
    if (opcode === "data_set_variable_to") {
      // Find VARIABLE input which contains the variable name
      const varNameMatch = nodeContent.match(
        /VARIABLE:\s*\{\s*literal:\s*["']([^"']+)["']\s*\}/,
      );
      if (varNameMatch) {
        variablesSet.add(varNameMatch[1]);
      }
    }
  }

  // Inputs: variables used but not set within the chain
  // Outputs: variables set within the chain
  const suggestedInputs = [...variablesUsed].filter(
    (v) => !variablesSet.has(v),
  );
  const suggestedOutputs = [...variablesSet];

  return { suggestedInputs, suggestedOutputs };
}

export interface ExtractToWorkflowResult {
  source: string;
  success: boolean;
  newWorkflowCallNodeId: string | null;
  errors: string[];
}

// Extract selected nodes into a new workflow
export function extractToWorkflow(
  source: string,
  nodeIds: string[],
  sourceWorkflowName: string,
  newWorkflowName: string,
  newWorkflowInputs: DetailedInput[],
  newWorkflowOutputs: string[],
  newWorkflowVariables: Record<string, unknown>,
): ExtractToWorkflowResult {
  // Validate the chain first
  const validation = validateLinearChain(source, nodeIds, sourceWorkflowName);
  if (!validation.isValid) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: validation.errors,
    };
  }

  const {
    orderedNodeIds,
    firstNodeId,
    lastNodeId,
    predecessorNodeId,
    successorNodeId,
  } = validation;

  // Find all reporter nodes referenced by the chain nodes
  const reporterNodeIds = findReporterNodes(source, orderedNodeIds);

  let result = source;

  // Step 1: Create the new workflow
  const addWorkflowResult = addWorkflow(
    result,
    newWorkflowName,
    newWorkflowInputs,
    newWorkflowOutputs,
    newWorkflowVariables,
  );
  if (!addWorkflowResult.success) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [`Failed to create workflow "${newWorkflowName}"`],
    };
  }
  result = addWorkflowResult.source;

  // Step 2: Extract node YAML blocks (in reverse order to preserve line numbers)
  // First extract chain nodes, then reporter nodes
  const chainBlocks: Array<{ id: string; yaml: string; indent: number }> = [];
  const reporterBlocks: Array<{ id: string; yaml: string; indent: number }> =
    [];

  // Extract chain nodes (in reverse to preserve line numbers)
  for (const nodeId of [...orderedNodeIds].reverse()) {
    const range = findNodeLineRange(result, nodeId, sourceWorkflowName);
    if (!range) {
      return {
        source,
        success: false,
        newWorkflowCallNodeId: null,
        errors: [`Could not find node "${nodeId}"`],
      };
    }

    const lines = result.split("\n");
    const nodeYaml = lines.slice(range.startLine, range.endLine).join("\n");
    chainBlocks.unshift({ id: nodeId, yaml: nodeYaml, indent: range.indent });

    // Delete from source workflow
    const deleteResult = deleteNode(result, nodeId);
    if (!deleteResult.success) {
      return {
        source,
        success: false,
        newWorkflowCallNodeId: null,
        errors: [`Failed to delete node "${nodeId}"`],
      };
    }
    result = deleteResult.source;
  }

  // Extract reporter nodes (in reverse to preserve line numbers)
  for (const nodeId of [...reporterNodeIds].reverse()) {
    // Try with workflow scope first, then global
    let range = findNodeLineRange(result, nodeId, sourceWorkflowName);
    if (!range) {
      range = findNodeLineRange(result, nodeId);
    }
    if (!range) {
      continue;
    }

    const lines = result.split("\n");
    const nodeYaml = lines.slice(range.startLine, range.endLine).join("\n");
    reporterBlocks.unshift({
      id: nodeId,
      yaml: nodeYaml,
      indent: range.indent,
    });

    // Delete from source workflow
    const deleteResult = deleteNode(result, nodeId);
    if (deleteResult.success) {
      result = deleteResult.source;
    }
  }

  // Combine: chain nodes first, then reporters
  const nodeBlocks = [...chainBlocks, ...reporterBlocks];

  // Step 3: Insert nodes into new workflow after start node
  // Find the new workflow's nodes section
  const newWorkflowRange = findWorkflowNodesRange(result, newWorkflowName);
  if (!newWorkflowRange) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [
        `Could not find nodes section in new workflow "${newWorkflowName}"`,
      ],
    };
  }

  // Find the start node's end in the new workflow
  const startRange = findNodeLineRange(result, "start", newWorkflowName);
  if (!startRange) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [`Could not find start node in new workflow`],
    };
  }

  // Calculate the target indent for nodes in new workflow
  const targetIndent = startRange.indent;

  // Build the nodes YAML with adjusted indentation
  const insertLines: string[] = [];
  for (let i = 0; i < nodeBlocks.length; i++) {
    const block = nodeBlocks[i];
    const blockLines = block.yaml.split("\n");

    // Adjust indentation
    const indentDiff = targetIndent - block.indent;
    const adjustedLines = blockLines.map((line) => {
      if (line.trim() === "") return line;
      if (indentDiff > 0) {
        return " ".repeat(indentDiff) + line;
      } else if (indentDiff < 0) {
        return line.slice(-indentDiff);
      }
      return line;
    });

    insertLines.push(...adjustedLines);
  }

  // Insert after start node
  const lines = result.split("\n");
  const insertPoint = startRange.endLine;
  lines.splice(insertPoint, 0, ...insertLines);
  result = lines.join("\n");

  // Step 4: Update start.next to point to first extracted node
  const connectStartResult = connectNodes(
    result,
    "start",
    firstNodeId!,
    newWorkflowName,
  );
  if (!connectStartResult.success) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [`Failed to connect start to "${firstNodeId}"`],
    };
  }
  result = connectStartResult.source;

  // Step 5: Set last node's next to null (end of new workflow)
  const disconnectLastResult = disconnectNode(
    result,
    lastNodeId!,
    newWorkflowName,
  );
  if (!disconnectLastResult.success) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [`Failed to disconnect last node "${lastNodeId}"`],
    };
  }
  result = disconnectLastResult.source;

  // Step 6: Add workflow_call node in source workflow
  const callNodeResult = addWorkflowCallNode(
    result,
    newWorkflowName,
    newWorkflowInputs.map((i) => i.name),
    sourceWorkflowName,
  );
  if (!callNodeResult.nodeId) {
    return {
      source,
      success: false,
      newWorkflowCallNodeId: null,
      errors: [`Failed to create workflow_call node`],
    };
  }
  result = callNodeResult.source;
  const newCallNodeId = callNodeResult.nodeId;

  // Step 7: Wire predecessor to workflow_call
  if (predecessorNodeId) {
    // Check if predecessor is "start"
    const connectPredResult = connectNodes(
      result,
      predecessorNodeId === "start" ? "start" : predecessorNodeId,
      newCallNodeId,
      sourceWorkflowName,
    );
    if (!connectPredResult.success) {
      return {
        source,
        success: false,
        newWorkflowCallNodeId: null,
        errors: [`Failed to connect predecessor to workflow_call`],
      };
    }
    result = connectPredResult.source;
  }

  // Step 8: Wire workflow_call to successor
  if (successorNodeId) {
    const connectSuccResult = connectNodes(
      result,
      newCallNodeId,
      successorNodeId,
      sourceWorkflowName,
    );
    if (!connectSuccResult.success) {
      return {
        source,
        success: false,
        newWorkflowCallNodeId: null,
        errors: [`Failed to connect workflow_call to successor`],
      };
    }
    result = connectSuccResult.source;
  }

  return {
    source: result,
    success: true,
    newWorkflowCallNodeId: newCallNodeId,
    errors: [],
  };
}

// Export all functions as a service object for convenience
export const workflowService = {
  formatYamlValue,
  findNodeLineRange,
  generateUniqueNodeId,
  deleteNode,
  addNode,
  addNodeAndConnect,
  addWorkflowCallNode,
  duplicateNode,
  updateNodeInput,
  connectNodes,
  disconnectNode,
  connectBranch,
  disconnectConnection,
  convertOrphanToReporter,
  deleteReporter,
  updateWorkflowInterface,
  addVariable,
  updateVariable,
  deleteVariable,
  addDynamicBranch,
  removeDynamicBranch,
  addDynamicInput,
  removeDynamicInput,
  addWorkflow,
  deleteWorkflow,
  validateLinearChain,
  analyzeChainVariables,
  extractToWorkflow,
};
