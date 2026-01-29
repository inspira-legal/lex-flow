import { describe, it, expect } from "vitest";
import { executeCommand } from "../CommandService";
import type { OpcodeInterface } from "../../../api/types";

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

describe("CommandService", () => {
  describe("executeCommand", () => {
    it("executes DELETE_NODE command", () => {
      const result = executeCommand(baseSource, {
        type: "DELETE_NODE",
        nodeId: "hello",
      });

      expect(result.success).toBe(true);
      expect(result.source).not.toContain("hello:");
    });

    it("executes ADD_NODE command and returns nodeId", () => {
      const mockOpcode: OpcodeInterface = {
        name: "io_print",
        description: "Print",
        return_type: undefined,
        parameters: [{ name: "message", type: "str", required: true }],
      };

      const result = executeCommand(baseSource, {
        type: "ADD_NODE",
        opcode: mockOpcode,
        workflowName: "main",
      });

      expect(result.success).toBe(true);
      expect(result.nodeId).toBeDefined();
      expect(result.source).toContain(result.nodeId);
    });

    it("executes DUPLICATE_NODE command", () => {
      const result = executeCommand(baseSource, {
        type: "DUPLICATE_NODE",
        nodeId: "hello",
      });

      expect(result.success).toBe(true);
      expect(result.nodeId).toBeDefined();
      expect(result.nodeId).toContain("hello_copy");
    });

    it("executes UPDATE_INPUT command", () => {
      const result = executeCommand(baseSource, {
        type: "UPDATE_INPUT",
        nodeId: "hello",
        inputKey: "MESSAGE",
        value: "Updated!",
      });

      expect(result.success).toBe(true);
      expect(result.source).toContain('literal: "Updated!"');
    });

    it("executes CONNECT_NODES command", () => {
      const disconnectedSource = baseSource.replace("next: hello", "next: null");
      const result = executeCommand(disconnectedSource, {
        type: "CONNECT_NODES",
        fromId: "start",
        toId: "hello",
      });

      expect(result.success).toBe(true);
      expect(result.source).toContain("next: hello");
    });

    it("executes DISCONNECT_NODE command", () => {
      const result = executeCommand(baseSource, {
        type: "DISCONNECT_NODE",
        nodeId: "start",
      });

      expect(result.success).toBe(true);
      expect(result.source).toMatch(/start:[\s\S]*?next: null/);
    });

    it("executes ADD_VARIABLE command", () => {
      const result = executeCommand(baseSource, {
        type: "ADD_VARIABLE",
        workflowName: "main",
        name: "counter",
        value: 42,
      });

      expect(result.success).toBe(true);
      expect(result.source).toContain("counter: 42");
    });

    it("returns error for unknown command type", () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result = executeCommand(baseSource, {
        type: "UNKNOWN_COMMAND",
      } as any);

      expect(result.success).toBe(false);
      expect(result.error).toContain("Unknown");
    });

    it("returns failure when operation fails", () => {
      const result = executeCommand(baseSource, {
        type: "DELETE_NODE",
        nodeId: "nonexistent",
      });

      expect(result.success).toBe(false);
    });

    it("handles all command types without throwing", () => {
      // Test that each command type is handled (may succeed or fail, but shouldn't throw)
      const commands = [
        { type: "DELETE_NODE", nodeId: "x" },
        { type: "DUPLICATE_NODE", nodeId: "x" },
        { type: "UPDATE_INPUT", nodeId: "x", inputKey: "k", value: "v" },
        { type: "CONNECT_NODES", fromId: "a", toId: "b" },
        { type: "CONNECT_BRANCH", fromId: "a", toId: "b", branchLabel: "THEN" },
        { type: "DISCONNECT_NODE", nodeId: "x" },
        { type: "DISCONNECT_CONNECTION", fromId: "a", toId: "b" },
        { type: "CONVERT_ORPHAN_TO_REPORTER", orphanId: "a", targetId: "b", inputKey: "k" },
        { type: "DELETE_REPORTER", parentId: "a", inputPath: ["k"] },
        { type: "ADD_VARIABLE", workflowName: "main", name: "v", value: 1 },
        { type: "UPDATE_VARIABLE", workflowName: "main", oldName: "v", newName: "v2", value: 2 },
        { type: "DELETE_VARIABLE", workflowName: "main", name: "v" },
        { type: "UPDATE_INTERFACE", workflowName: "main", inputs: [], outputs: [] },
        { type: "ADD_DYNAMIC_BRANCH", nodeId: "x", branchPrefix: "CATCH" },
        { type: "REMOVE_DYNAMIC_BRANCH", nodeId: "x", branchName: "CATCH1" },
        { type: "ADD_DYNAMIC_INPUT", nodeId: "x", inputPrefix: "ARG" },
        { type: "REMOVE_DYNAMIC_INPUT", nodeId: "x", inputName: "ARG1" },
        { type: "ADD_WORKFLOW_CALL_NODE", workflowName: "test", params: [] },
      ] as const;

      for (const cmd of commands) {
        expect(() => {
          executeCommand(baseSource, cmd as any);
        }).not.toThrow();
      }
    });
  });
});
