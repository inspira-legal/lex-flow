/**
 * Grammar service for the LexFlow grammar schema.
 *
 * The grammar is imported directly from the copied grammar.json file.
 * This eliminates async loading and provides synchronous access.
 */

import type { Grammar, Construct } from "../../types/grammar";
import {
  getBranchColor as grammarGetBranchColor,
  getNodeColor as grammarGetNodeColor,
  getReporterColor as grammarGetReporterColor,
  getControlFlowOpcodes,
  getConstruct as grammarGetConstruct,
} from "../../types/grammar";

// Import grammar directly (copied at build time)
import grammarJson from "../../grammar.json";

// Type assertion for the imported JSON
const grammar: Grammar = grammarJson as Grammar;

/**
 * Get the grammar schema (synchronous).
 */
export function getGrammar(): Grammar {
  return grammar;
}

/**
 * Get branch color by name.
 */
export function getBranchColor(branchName: string): string {
  return grammarGetBranchColor(grammar, branchName);
}

/**
 * Get node color by type.
 */
export function getNodeColor(nodeType: string): string {
  return grammarGetNodeColor(grammar, nodeType);
}

/**
 * Get reporter color by opcode.
 */
export function getReporterColor(opcode: string): string {
  return grammarGetReporterColor(grammar, opcode);
}

/**
 * Get the set of control flow opcodes.
 */
export function getControlFlowOpcodeSet(): Set<string> {
  return getControlFlowOpcodes(grammar);
}

/**
 * Get a construct by opcode.
 */
export function getConstruct(opcode: string): Construct | undefined {
  return grammarGetConstruct(grammar, opcode);
}

/**
 * Get branch slots for a control flow opcode.
 * Uses grammar-driven logic with support for dynamic branches.
 */
export function getBranchSlots(
  opcode: string,
  connectedBranches: string[],
): Array<{ name: string; connected: boolean }> {
  const construct = getConstruct(opcode);

  if (!construct || !construct.branches) {
    return [];
  }

  const connectedSet = new Set(connectedBranches);
  const slots: Array<{ name: string; connected: boolean }> = [];

  // Handle dynamic branches (try/fork and similar)
  if (construct.dynamic_branches) {
    // Get static branches and identify dynamic branch patterns
    const staticBranches: string[] = [];
    const dynamicPatterns: Array<{ prefix: string; minCount: number }> = [];

    for (const branch of construct.branches) {
      // Check if this is a numbered branch (e.g., CATCH1, BRANCH1)
      const match = branch.name.match(/^([A-Z]+)(\d+)$/);
      if (match) {
        const prefix = match[1];
        // Check if we already have this pattern
        const existing = dynamicPatterns.find((p) => p.prefix === prefix);
        if (!existing) {
          // Determine minimum count based on required flag
          dynamicPatterns.push({
            prefix,
            minCount: branch.required ? 1 : 0,
          });
        }
      } else {
        staticBranches.push(branch.name);
      }
    }

    // Add static branches first
    for (const branchName of staticBranches) {
      slots.push({ name: branchName, connected: connectedSet.has(branchName) });
    }

    // Handle dynamic branches
    for (const pattern of dynamicPatterns) {
      // Find all connected branches matching this pattern
      const connectedDynamic = connectedBranches.filter((n) =>
        n.startsWith(pattern.prefix) && /^\d+$/.test(n.slice(pattern.prefix.length))
      );
      const maxConnected = connectedDynamic.length > 0
        ? Math.max(...connectedDynamic.map((n) => parseInt(n.slice(pattern.prefix.length))))
        : 0;

      // Determine how many slots to show (at least minCount, or maxConnected)
      const slotCount = Math.max(pattern.minCount, maxConnected);

      // Always show at least one slot for dynamic branches
      const actualSlotCount = slotCount > 0 ? slotCount : 1;

      for (let i = 1; i <= actualSlotCount; i++) {
        const name = `${pattern.prefix}${i}`;
        slots.push({ name, connected: connectedSet.has(name) });
      }
    }

    return slots;
  }

  // Standard branches from schema
  for (const branch of construct.branches) {
    slots.push({ name: branch.name, connected: connectedSet.has(branch.name) });
  }

  return slots;
}

/**
 * Get categories from grammar.
 */
export function getCategories() {
  return grammar.categories;
}

/**
 * Get category icon by opcode prefix.
 */
export function getCategoryIcon(opcode: string): string {
  for (const category of grammar.categories) {
    if (opcode.startsWith(category.prefix)) {
      return category.icon;
    }
  }
  return "⚙"; // Default icon
}

/**
 * Get category by opcode prefix.
 */
export function getCategoryByOpcode(opcode: string) {
  for (const category of grammar.categories) {
    if (opcode.startsWith(category.prefix)) {
      return category;
    }
  }
  return null;
}

// Export types
export type { Grammar, Construct } from "../../types/grammar";
