# Customizing LexFlow Web

This guide explains how to customize LexFlow Web, including configuring backends, creating custom providers, and modifying the frontend.

## Backend Configuration

### Environment Variables

Configure the frontend to connect to different backends using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |
| `VITE_WS_URL` | (auto) | WebSocket URL (auto-derived if not set) |

**Examples:**

```bash
# Connect to a remote backend
VITE_API_BASE_URL=https://api.example.com/lexflow npm run dev

# Use a different local port
VITE_API_BASE_URL=http://localhost:3000/api npm run dev

# Specify explicit WebSocket URL
VITE_WS_URL=wss://api.example.com/ws npm run dev
```

### For Production Builds

Create a `.env.production` file:

```bash
# .env.production
VITE_API_BASE_URL=https://api.yourservice.com
VITE_WS_URL=wss://api.yourservice.com/ws
```

Then build:

```bash
npm run build
```

## Backend Provider System

The frontend uses a provider abstraction for all backend communication. This allows you to:

- Connect to different backends
- Add custom execution engines
- Run the frontend offline (parsing only)
- Mock backends for testing

### Provider Interface

```typescript
interface BackendConfig {
  apiBaseUrl: string              // e.g., '/api' or 'https://remote.com/api'
  wsUrl?: string                  // WebSocket URL (auto-derived if not set)
  supportsExamples?: boolean      // Whether backend has /examples endpoint
  supportsWebSocket?: boolean     // Whether backend supports streaming
}

interface BackendProvider {
  name: string
  config: BackendConfig

  // Required methods
  listOpcodes(): Promise<OpcodeInterface[]>
  executeWorkflow(source, inputs?, metrics?): Promise<ExecuteResponse>
  getWebSocketUrl(): string | null
  parseWorkflow(source: string): Promise<ParseResponse>

  // Optional methods
  validateWorkflow?(source: string): Promise<ValidateResponse>
  listExamples?(): Promise<ExampleInfo[]>
  getExample?(path: string): Promise<ExampleContent>
}
```

### Default Provider (LexFlowProvider)

The default provider connects to the LexFlow backend:

```typescript
// main.tsx
import { createLexFlowProvider, BackendProviderWrapper } from './providers'
import { getConfig } from './config'

const config = getConfig()
const provider = createLexFlowProvider({
  apiBaseUrl: config.apiBaseUrl,
  wsUrl: config.wsUrl,
  supportsExamples: true,
  supportsWebSocket: true,
})

createRoot(document.getElementById('root')!).render(
  <BackendProviderWrapper provider={provider}>
    <App />
  </BackendProviderWrapper>
)
```

**Key feature**: `parseWorkflow()` runs client-side using the TypeScript visualization service. No API call is made for parsing - this happens entirely in the browser.

## Creating a Custom Provider

### Example: Offline-Only Provider

A provider that only does client-side parsing, no execution:

```typescript
// frontend/src/providers/OfflineProvider.ts
import type { BackendProvider, BackendConfig } from './types'
import type {
  ParseResponse,
  ExecuteResponse,
  OpcodeInterface,
} from '../api/types'
import { parseWorkflowSource } from '../services/yamlParser'
import { workflowToTree } from '../services/visualization'

export function createOfflineProvider(): BackendProvider {
  const config: BackendConfig = {
    apiBaseUrl: '',
    supportsExamples: false,
    supportsWebSocket: false,
  }

  return {
    name: 'offline',
    config,

    async listOpcodes(): Promise<OpcodeInterface[]> {
      // Return a static list of opcodes
      return [
        { name: 'io_print', parameters: [{ name: 'STRING', type: 'str', required: true }] },
        { name: 'operator_add', parameters: [
          { name: 'A', type: 'number', required: true },
          { name: 'B', type: 'number', required: true },
        ]},
        // ... add more opcodes
      ]
    },

    async executeWorkflow(): Promise<ExecuteResponse> {
      return {
        success: false,
        error: 'Execution not available in offline mode',
      }
    },

    getWebSocketUrl(): string | null {
      return null  // No WebSocket support
    },

    async parseWorkflow(source: string): Promise<ParseResponse> {
      // Client-side parsing (same as default provider)
      const parseResult = parseWorkflowSource<Record<string, unknown>>(source)

      if (!parseResult.success || !parseResult.data) {
        return { success: false, error: parseResult.error || 'Parse failed' }
      }

      const treeResult = workflowToTree(parseResult.data)
      if ('error' in treeResult) {
        return { success: false, error: treeResult.error }
      }

      return { success: true, tree: treeResult, interface: treeResult.interface }
    },
  }
}
```

### Example: Remote API Provider

Connect to a different backend API:

```typescript
// frontend/src/providers/RemoteProvider.ts
import type { BackendProvider, BackendConfig } from './types'
import type {
  ParseResponse,
  ExecuteResponse,
  OpcodeInterface,
  ExampleInfo,
  ExampleContent,
} from '../api/types'
import { parseWorkflowSource } from '../services/yamlParser'
import { workflowToTree } from '../services/visualization'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,  // Add auth if needed
    },
    ...options,
  })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }
  return response.json()
}

export function createRemoteProvider(baseUrl: string): BackendProvider {
  const config: BackendConfig = {
    apiBaseUrl: baseUrl,
    supportsExamples: true,
    supportsWebSocket: true,
  }

  return {
    name: 'remote',
    config,

    async listOpcodes(): Promise<OpcodeInterface[]> {
      return fetchJson(`${baseUrl}/opcodes`)
    },

    async executeWorkflow(
      source: string,
      inputs?: Record<string, unknown>,
      includeMetrics?: boolean
    ): Promise<ExecuteResponse> {
      return fetchJson(`${baseUrl}/execute`, {
        method: 'POST',
        body: JSON.stringify({
          workflow: source,
          inputs,
          include_metrics: includeMetrics,
        }),
      })
    },

    getWebSocketUrl(): string | null {
      const url = new URL(baseUrl)
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
      return `${protocol}//${url.host}/ws/execute`
    },

    // Client-side parsing (no API call)
    async parseWorkflow(source: string): Promise<ParseResponse> {
      const parseResult = parseWorkflowSource<Record<string, unknown>>(source)
      if (!parseResult.success || !parseResult.data) {
        return { success: false, error: parseResult.error || 'Parse failed' }
      }
      const treeResult = workflowToTree(parseResult.data)
      if ('error' in treeResult) {
        return { success: false, error: treeResult.error }
      }
      return { success: true, tree: treeResult, interface: treeResult.interface }
    },

    async listExamples(): Promise<ExampleInfo[]> {
      return fetchJson(`${baseUrl}/examples`)
    },

    async getExample(path: string): Promise<ExampleContent> {
      return fetchJson(`${baseUrl}/examples/${encodeURIComponent(path)}`)
    },
  }
}
```

### Using Custom Providers

Update `main.tsx` to use your custom provider:

```typescript
// main.tsx
import { createOfflineProvider } from './providers/OfflineProvider'
import { createRemoteProvider } from './providers/RemoteProvider'
import { BackendProviderWrapper } from './providers'

// Choose provider based on environment or config
const provider = import.meta.env.VITE_OFFLINE_MODE
  ? createOfflineProvider()
  : createRemoteProvider(import.meta.env.VITE_API_BASE_URL || '/api')

createRoot(document.getElementById('root')!).render(
  <BackendProviderWrapper provider={provider}>
    <App />
  </BackendProviderWrapper>
)
```

## Implementing a Custom Backend

To create a backend that LexFlow Web can connect to, implement these endpoints:

### Required Endpoints

**GET /api/opcodes**

Returns list of available opcodes:

```json
[
  {
    "name": "io_print",
    "description": "Print a string to output",
    "parameters": [
      { "name": "STRING", "type": "str", "required": true }
    ],
    "return_type": null
  },
  {
    "name": "operator_add",
    "description": "Add two numbers",
    "parameters": [
      { "name": "A", "type": "number", "required": true },
      { "name": "B", "type": "number", "required": true }
    ],
    "return_type": "number"
  }
]
```

**POST /api/execute**

Execute a workflow:

Request:
```json
{
  "workflow": "workflows:\n  - name: main\n    ...",
  "inputs": { "name": "Alice" },
  "include_metrics": true
}
```

Response:
```json
{
  "success": true,
  "result": 42,
  "output": "Hello, Alice!\n",
  "metrics": { "total_time": 0.0012 }
}
```

### Optional Endpoints

**WebSocket /ws/execute**

For streaming execution output:

Client sends:
```json
{
  "type": "start",
  "workflow": "...",
  "inputs": {},
  "include_metrics": false
}
```

Server sends:
```json
{ "type": "output", "line": "Hello, World!" }
{ "type": "output", "line": "Processing..." }
{ "type": "complete", "result": 42, "metrics": null }
```

Or on error:
```json
{ "type": "error", "message": "Division by zero" }
```

**GET /api/examples**

List example workflows:
```json
[
  { "name": "Hello World", "path": "basics/hello_world", "category": "Basics" },
  { "name": "Loop Example", "path": "control_flow/loops", "category": "Control Flow" }
]
```

**GET /api/examples/{path}**

Get example content:
```json
{
  "name": "Hello World",
  "path": "basics/hello_world",
  "content": "workflows:\n  - name: main\n    ..."
}
```

**POST /api/validate**

Validate workflow syntax:

Request:
```json
{ "workflow": "invalid yaml {{" }
```

Response:
```json
{
  "valid": false,
  "errors": ["YAML parse error at line 1"]
}
```

## Customizing the Frontend

### Modifying Components

Key components to customize:

| Component | Location | Purpose |
|-----------|----------|---------|
| `Canvas` | `components/visualization/` | Main workflow visualization |
| `NodePalette` | `components/palette/` | Opcode browser |
| `CodeEditor` | `components/editor/` | Monaco-based editor |
| `NodeEditorPanel` | `components/node-editor/` | Property editor |
| `ExecutionPanel` | `components/execution/` | Run and output |

### Adding New Node Types

1. Update the visualization service (`services/visualization.ts`):
   ```typescript
   function getNodeType(opcode: string): NodeType {
     if (opcode.startsWith('custom_')) return 'custom'  // Add new category
     // ... existing categories
   }
   ```

2. Add colors in `api/types.ts`:
   ```typescript
   export const NODE_COLORS: Record<NodeType | string, string> = {
     custom: '#FF6B6B',  // Custom color
     // ... existing colors
   }
   ```

3. Update the Canvas component to render the new type.

### Theming

CSS variables are defined in `styles/variables.css`:

```css
:root {
  --color-bg: #1a1a2e;
  --color-surface: #16213e;
  --color-primary: #0f3460;
  --color-accent: #e94560;
  --color-text: #eaeaea;
  /* ... */
}
```

Override these for custom themes.

## Testing

### Testing Custom Providers

```typescript
// __tests__/providers.test.ts
import { createOfflineProvider } from '../src/providers/OfflineProvider'

describe('OfflineProvider', () => {
  const provider = createOfflineProvider()

  it('should parse workflows client-side', async () => {
    const result = await provider.parseWorkflow(`
      workflows:
        - name: main
          nodes:
            start:
              opcode: workflow_start
              next: null
    `)
    expect(result.success).toBe(true)
    expect(result.tree?.workflows).toHaveLength(1)
  })

  it('should return error for execution', async () => {
    const result = await provider.executeWorkflow('...')
    expect(result.success).toBe(false)
    expect(result.error).toContain('offline')
  })
})
```

### Mocking Providers in Tests

```typescript
// __tests__/App.test.tsx
import { render } from '@testing-library/react'
import { BackendProviderWrapper } from '../src/providers'
import { App } from '../src/App'

const mockProvider = {
  name: 'mock',
  config: { apiBaseUrl: '/api' },
  listOpcodes: jest.fn().mockResolvedValue([]),
  executeWorkflow: jest.fn().mockResolvedValue({ success: true }),
  getWebSocketUrl: () => null,
  parseWorkflow: jest.fn().mockResolvedValue({ success: true, tree: null }),
}

test('renders app with mock provider', () => {
  render(
    <BackendProviderWrapper provider={mockProvider}>
      <App />
    </BackendProviderWrapper>
  )
})
```

## Next Steps

- **[User Guide](USER_GUIDE.md)** - Learn how to use the visual editor
- **[Getting Started](GETTING_STARTED.md)** - Installation and setup
- **[LexFlow Docs](../../docs/README.md)** - Core LexFlow documentation
