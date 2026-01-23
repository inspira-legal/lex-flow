// Default LexFlow backend provider implementation
// Uses client-side parsing and LexFlow API for execution

import type { BackendProvider, BackendConfig } from "./types";
import type {
  ParseResponse,
  ValidateResponse,
  ExecuteResponse,
  ExampleInfo,
  ExampleContent,
  OpcodeInterface,
  WorkflowTree,
} from "../api/types";
import { parseWorkflowSource } from "../services/yamlParser";
import { workflowToTree } from "../services/visualization";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function createLexFlowProvider(config: BackendConfig): BackendProvider {
  const { apiBaseUrl } = config;

  return {
    name: "lexflow",
    config,

    async listOpcodes(): Promise<OpcodeInterface[]> {
      return fetchJson<OpcodeInterface[]>(`${apiBaseUrl}/opcodes`);
    },

    async executeWorkflow(
      source: string,
      inputs?: Record<string, unknown>,
      includeMetrics?: boolean,
    ): Promise<ExecuteResponse> {
      return fetchJson<ExecuteResponse>(`${apiBaseUrl}/execute`, {
        method: "POST",
        body: JSON.stringify({
          workflow: source,
          inputs,
          include_metrics: includeMetrics,
        }),
      });
    },

    getWebSocketUrl(): string | null {
      if (config.supportsWebSocket === false) {
        return null;
      }

      // Use explicit wsUrl if provided
      if (config.wsUrl) {
        return `${config.wsUrl}/execute`;
      }

      // Auto-derive from apiBaseUrl
      const url = new URL(apiBaseUrl, window.location.href);
      const protocol = url.protocol === "https:" ? "wss:" : "ws:";
      return `${protocol}//${url.host}/ws/execute`;
    },

    // Client-side parsing (no backend call needed)
    async parseWorkflow(source: string): Promise<ParseResponse> {
      const parseResult = parseWorkflowSource<Record<string, unknown>>(source);

      if (!parseResult.success || !parseResult.data) {
        return {
          success: false,
          error: parseResult.error || "Parse failed",
        };
      }

      const treeResult = workflowToTree(parseResult.data);

      if ("error" in treeResult) {
        return {
          success: false,
          error: treeResult.error,
        };
      }

      const tree = treeResult as WorkflowTree;
      return {
        success: true,
        tree,
        interface: tree.interface,
      };
    },

    async validateWorkflow(source: string): Promise<ValidateResponse> {
      return fetchJson<ValidateResponse>(`${apiBaseUrl}/validate`, {
        method: "POST",
        body: JSON.stringify({ workflow: source }),
      });
    },

    async listExamples(): Promise<ExampleInfo[]> {
      if (config.supportsExamples === false) {
        return [];
      }
      return fetchJson<ExampleInfo[]>(`${apiBaseUrl}/examples`);
    },

    async getExample(path: string): Promise<ExampleContent> {
      return fetchJson<ExampleContent>(`${apiBaseUrl}/examples/${path}`);
    },
  };
}
