import { describe, it, expect } from "vitest";
import {
  deleteNode,
  addNode,
  addNodeAndConnect,
  duplicateNode,
  updateNodeInput,
  connectNodes,
  disconnectNode,
  connectBranch,
  addVariable,
  updateVariable,
  deleteVariable,
  updateWorkflowInterface,
} from "../WorkflowService";
import type { OpcodeInterface } from "../../../api/types";

// Base workflow source for tests
const baseSource = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: hello
      hello:
        opcode: io_print
        next: null
        inputs:
          MESSAGE: { literal: "Hello" }
`;

const workflowWithOrphan = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: null
      orphan:
        opcode: io_print
        next: null
        inputs:
          MESSAGE: { literal: "I am orphan" }
`;

const workflowWithVariables = `workflows:
  - name: main
    interface:
      inputs: ["name"]
      outputs: []
    variables:
      count: 0
      message: "hello"
    nodes:
      start:
        next: null
`;

describe("WorkflowService", () => {
  describe("deleteNode", () => {
    it("removes node from YAML", () => {
      const result = deleteNode(baseSource, "hello");

      expect(result.success).toBe(true);
      expect(result.source).not.toContain("hello:");
      expect(result.source).toContain("start:");
    });

    it("returns failure for non-existent node", () => {
      const result = deleteNode(baseSource, "nonexistent");

      expect(result.success).toBe(false);
      expect(result.source).toBe(baseSource);
    });

    it("preserves other nodes when deleting", () => {
      const result = deleteNode(baseSource, "hello");

      expect(result.success).toBe(true);
      expect(result.source).toContain("start:");
      expect(result.source).toContain("next: hello"); // Connection preserved (cleanup is separate)
    });
  });

  describe("addNode", () => {
    const mockOpcode: OpcodeInterface = {
      name: "io_print",
      description: "Print a message",
      return_type: undefined,
      parameters: [
        { name: "message", type: "str", required: true, default: "" },
      ],
    };

    it("creates node with unique ID", () => {
      const result = addNode(baseSource, mockOpcode, "main");

      expect(result.nodeId).toBeDefined();
      expect(result.nodeId).toContain("io_");
      expect(result.source).toContain(result.nodeId);
      expect(result.source).toContain("opcode: io_print");
    });

    it("generates incrementing IDs when prefix exists", () => {
      // First add
      const result1 = addNode(baseSource, mockOpcode, "main");
      // Second add
      const result2 = addNode(result1.source, mockOpcode, "main");

      expect(result1.nodeId).not.toBe(result2.nodeId);
    });

    it("adds node with default input values", () => {
      const result = addNode(baseSource, mockOpcode, "main");

      expect(result.source).toContain("MESSAGE:");
    });

    it("returns null for non-existent workflow", () => {
      const result = addNode(baseSource, mockOpcode, "nonexistent");

      expect(result.nodeId).toBeNull();
    });
  });

  describe("addNodeAndConnect", () => {
    const mockOpcode: OpcodeInterface = {
      name: "io_print",
      description: "Print a message",
      return_type: undefined,
      parameters: [
        { name: "message", type: "str", required: true, default: "" },
      ],
    };

    it("adds a node and connects it to source node", () => {
      const result = addNodeAndConnect(baseSource, mockOpcode, "start", "main");

      expect(result.success).toBe(true);
      expect(result.nodeId).toBeDefined();
      expect(result.nodeId).toContain("io_");
      expect(result.source).toContain(result.nodeId);
      expect(result.source).toContain("opcode: io_print");

      // Verify connection
      const lines = result.source.split("\n");
      const startNodeLines = lines.filter((l) => l.includes("next:") && lines[lines.indexOf(l) - 1]?.includes("start:"));
      expect(startNodeLines.some((l) => l.includes(result.nodeId!))).toBe(true);
    });

    it("replaces existing connection when source already has next", () => {
      // baseSource has start pointing to hello
      const result = addNodeAndConnect(baseSource, mockOpcode, "start", "main");

      expect(result.success).toBe(true);
      expect(result.nodeId).toBeDefined();

      // start should now point to the new node, not hello
      const lines = result.source.split("\n");
      const startIndex = lines.findIndex((l) => l.includes("start:"));
      const nextLine = lines[startIndex + 1];
      expect(nextLine).toContain(result.nodeId!);
      expect(nextLine).not.toContain("hello");
    });

    it("returns failure when source node does not exist", () => {
      const result = addNodeAndConnect(baseSource, mockOpcode, "nonexistent", "main");

      expect(result.success).toBe(false);
      expect(result.nodeId).toBeNull();
    });

    it("returns failure when workflow does not exist", () => {
      const result = addNodeAndConnect(baseSource, mockOpcode, "start", "nonexistent");

      expect(result.success).toBe(false);
      expect(result.nodeId).toBeNull();
    });

    it("creates node with correct inputs and connection", () => {
      const result = addNodeAndConnect(baseSource, mockOpcode, "hello", "main");

      expect(result.success).toBe(true);
      expect(result.nodeId).toBeDefined();

      // Check inputs are present
      expect(result.source).toContain("MESSAGE:");

      // Check connection from hello to new node
      const lines = result.source.split("\n");
      const helloIndex = lines.findIndex((l) => l.trim() === "hello:");
      let foundNext = false;
      for (let i = helloIndex + 1; i < lines.length; i++) {
        if (lines[i].includes("next:") && lines[i].includes(result.nodeId!)) {
          foundNext = true;
          break;
        }
        if (lines[i].trim() && !lines[i].startsWith("  ")) break;
      }
      expect(foundNext).toBe(true);
    });
  });

  describe("duplicateNode", () => {
    it("creates a copy with new ID", () => {
      const result = duplicateNode(baseSource, "hello");

      expect(result.nodeId).toBeDefined();
      expect(result.nodeId).toContain("hello_copy");
      expect(result.source).toContain("hello:");
      expect(result.source).toContain(result.nodeId);
    });

    it("sets next to null on duplicated node", () => {
      // Create source with connected node
      const sourceWithConnection = baseSource;
      const result = duplicateNode(sourceWithConnection, "hello");

      // The duplicate should have next: null
      const lines = result.source.split("\n");
      const copyStart = lines.findIndex((l) => l.includes(result.nodeId + ":"));
      const copyNextLine = lines
        .slice(copyStart)
        .find((l) => l.includes("next:"));
      expect(copyNextLine).toContain("null");
    });

    it("returns null for non-existent node", () => {
      const result = duplicateNode(baseSource, "nonexistent");

      expect(result.nodeId).toBeNull();
    });
  });

  describe("updateNodeInput", () => {
    it("updates literal value", () => {
      const result = updateNodeInput(
        baseSource,
        "hello",
        "MESSAGE",
        "New message",
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain('MESSAGE: { literal: "New message" }');
    });

    it("handles variable references ($ prefix)", () => {
      const result = updateNodeInput(baseSource, "hello", "MESSAGE", "$myVar");

      expect(result.success).toBe(true);
      expect(result.source).toContain('MESSAGE: { variable: "myVar" }');
    });

    it("handles JSON values", () => {
      const result = updateNodeInput(baseSource, "hello", "MESSAGE", "42");

      expect(result.success).toBe(true);
      expect(result.source).toContain("MESSAGE: { literal: 42 }");
    });

    it("returns failure for non-existent node", () => {
      const result = updateNodeInput(
        baseSource,
        "nonexistent",
        "MESSAGE",
        "test",
      );

      expect(result.success).toBe(false);
    });

    it("returns failure for non-existent input", () => {
      const result = updateNodeInput(
        baseSource,
        "hello",
        "NONEXISTENT",
        "test",
      );

      expect(result.success).toBe(false);
    });
  });

  describe("connectNodes", () => {
    it("sets next property", () => {
      const result = connectNodes(workflowWithOrphan, "start", "orphan");

      expect(result.success).toBe(true);
      expect(result.source).toContain("next: orphan");
    });

    it("overwrites existing next property", () => {
      const result = connectNodes(baseSource, "start", "different_node");

      expect(result.success).toBe(true);
      // Should change from hello to different_node
      expect(result.source).toMatch(/next: different_node/);
    });

    it("returns failure for non-existent source node", () => {
      const result = connectNodes(baseSource, "nonexistent", "hello");

      expect(result.success).toBe(false);
    });
  });

  describe("disconnectNode", () => {
    it("sets next to null", () => {
      const result = disconnectNode(baseSource, "start");

      expect(result.success).toBe(true);
      expect(result.source).toContain("next: null");
    });

    it("returns failure for non-existent node", () => {
      const result = disconnectNode(baseSource, "nonexistent");

      expect(result.success).toBe(false);
    });
  });

  describe("addVariable", () => {
    it("adds variable to workflow", () => {
      const result = addVariable(workflowWithVariables, "main", "newVar", 42);

      expect(result.success).toBe(true);
      expect(result.source).toContain("newVar: 42");
    });

    it("handles string values", () => {
      const result = addVariable(
        workflowWithVariables,
        "main",
        "greeting",
        "hi",
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain("greeting: hi");
    });

    it("returns failure for non-existent workflow", () => {
      const result = addVariable(
        workflowWithVariables,
        "nonexistent",
        "var",
        1,
      );

      expect(result.success).toBe(false);
    });
  });

  describe("updateVariable", () => {
    it("updates variable name and value", () => {
      const result = updateVariable(
        workflowWithVariables,
        "main",
        "count",
        "counter",
        100,
      );

      expect(result.success).toBe(true);
      expect(result.source).not.toContain("count:");
      expect(result.source).toContain("counter: 100");
    });

    it("updates only value when name stays same", () => {
      const result = updateVariable(
        workflowWithVariables,
        "main",
        "count",
        "count",
        999,
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain("count: 999");
    });

    it("returns failure for non-existent variable", () => {
      const result = updateVariable(
        workflowWithVariables,
        "main",
        "nonexistent",
        "new",
        1,
      );

      expect(result.success).toBe(false);
    });
  });

  describe("deleteVariable", () => {
    it("removes variable from workflow", () => {
      const result = deleteVariable(workflowWithVariables, "main", "count");

      expect(result.success).toBe(true);
      expect(result.source).not.toContain("count:");
      expect(result.source).toContain("message:"); // Other variable preserved
    });

    it("returns failure for non-existent variable", () => {
      const result = deleteVariable(
        workflowWithVariables,
        "main",
        "nonexistent",
      );

      expect(result.success).toBe(false);
    });
  });

  describe("updateWorkflowInterface", () => {
    it("updates inputs and outputs with detailed format", () => {
      const result = updateWorkflowInterface(
        workflowWithVariables,
        "main",
        [
          { name: "a", type: "string", required: true },
          { name: "b", type: "number", required: false },
        ],
        ["result"],
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain('- name: "a"');
      expect(result.source).toContain('  type: "string"');
      expect(result.source).toContain("  required: true");
      expect(result.source).toContain('- name: "b"');
      expect(result.source).toContain('  type: "number"');
      expect(result.source).toContain("  required: false");
      expect(result.source).toContain('outputs: ["result"]');
    });

    it("handles empty arrays", () => {
      const result = updateWorkflowInterface(
        workflowWithVariables,
        "main",
        [],
        [],
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain("inputs: []");
      expect(result.source).toContain("outputs: []");
    });

    it("returns failure for non-existent workflow", () => {
      const result = updateWorkflowInterface(
        workflowWithVariables,
        "nonexistent",
        [],
        [],
      );

      expect(result.success).toBe(false);
    });
  });

  describe("connectBranch", () => {
    const controlFlowSource = `workflows:
  - name: main
    interface:
      inputs: []
      outputs: []
    variables: {}
    nodes:
      start:
        next: condition
      condition:
        opcode: control_if
        next: null
        inputs:
          CONDITION: { literal: true }
          THEN:
            branch: null
          ELSE:
            branch: null
      then_node:
        opcode: io_print
        next: null
        inputs:
          MESSAGE: { literal: "then" }
`;

    it("connects THEN branch", () => {
      const result = connectBranch(
        controlFlowSource,
        "condition",
        "then_node",
        "THEN",
      );

      expect(result.success).toBe(true);
      expect(result.source).toContain("branch: then_node");
    });
  });
});
