// API client for LexFlow backend

import type {
  WorkflowInput,
  ParseResponse,
  ValidateResponse,
  ExecuteResponse,
  ExampleInfo,
  ExampleContent,
  OpcodeInterface,
} from "./types";

const API_BASE = "/api";

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

export const api = {
  async parse(workflow: string): Promise<ParseResponse> {
    const body: WorkflowInput = { workflow };
    return fetchJson<ParseResponse>(`${API_BASE}/parse`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async validate(workflow: string): Promise<ValidateResponse> {
    const body: WorkflowInput = { workflow };
    return fetchJson<ValidateResponse>(`${API_BASE}/validate`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async execute(
    workflow: string,
    inputs?: Record<string, unknown>,
    includeMetrics?: boolean,
  ): Promise<ExecuteResponse> {
    const body: WorkflowInput = {
      workflow,
      inputs,
      include_metrics: includeMetrics,
    };
    return fetchJson<ExecuteResponse>(`${API_BASE}/execute`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async listExamples(): Promise<ExampleInfo[]> {
    return fetchJson<ExampleInfo[]>(`${API_BASE}/examples`);
  },

  async getExample(path: string): Promise<ExampleContent> {
    return fetchJson<ExampleContent>(`${API_BASE}/examples/${path}`);
  },

  async listOpcodes(): Promise<OpcodeInterface[]> {
    return fetchJson<OpcodeInterface[]>(`${API_BASE}/opcodes`);
  },
};
