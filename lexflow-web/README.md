# LexFlow Web

Visual editor and execution environment for LexFlow workflows. Can be used as a standalone web app or embedded into any website.

## Embedding the Editor

Add the LexFlow Editor to any webpage with just a few lines of code:

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-v1.3.1/lexflow-web/frontend/dist/lexflow-editor.css">
</head>
<body>
  <div id="editor" style="width: 100vw; height: 100vh;"></div>

  <script src="https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-v1.3.1/lexflow-web/frontend/dist/lexflow-editor.umd.js"></script>
  <script>
    const editor = LexFlowEditor.mount('#editor', {
      theme: 'dark',
      initialSource: `workflows:
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
        inputs:
          MESSAGE: { literal: "Hello, LexFlow!" }
`
    });
  </script>
</body>
</html>
```

### CDN URLs

Replace `web-v1.3.1` with the desired version:

```
https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-vX.Y.Z/lexflow-web/frontend/dist/lexflow-editor.css
https://cdn.jsdelivr.net/gh/inspira-legal/lex-flow@web-vX.Y.Z/lexflow-web/frontend/dist/lexflow-editor.umd.js
```

### Mount Options

```javascript
const editor = LexFlowEditor.mount('#container', {
  // Content
  initialSource: '...',           // Initial YAML workflow

  // Appearance
  theme: 'dark',                  // 'dark' | 'light' | 'system'

  // Backend (optional - for execution)
  executionUrl: '/api',           // Backend API URL
  websocketUrl: '/ws',            // WebSocket URL for streaming

  // Panel visibility
  showCodeEditor: true,           // Show YAML code editor
  showPalette: true,              // Show node palette
  showExecutionPanel: true,       // Show execution output panel
  showNodeEditor: true,           // Show node properties editor

  // Callbacks
  onSourceChange: (source) => {}, // Called when workflow changes
  onExecute: (result) => {},      // Called after execution
  onError: (error) => {},         // Called on errors
  onReady: () => {},              // Called when editor is ready
});
```

### Editor API

```javascript
// Get current workflow source
const yaml = editor.getSource();

// Set workflow source
editor.setSource(yamlString);

// Execute workflow (requires backend)
const result = await editor.execute({ input: 'value' });

// Toggle panels
editor.toggleCodeEditor();
editor.togglePalette();
editor.toggleExecutionPanel();

// Cleanup
editor.destroy();
```

## React Integration

```tsx
import { LexFlowEditor } from '@lexflow/editor';
import '@lexflow/editor/style.css';

function App() {
  return (
    <LexFlowEditor
      initialSource={workflowYaml}
      theme="dark"
      onSourceChange={(source) => console.log('Changed:', source)}
    />
  );
}
```

## Running the Backend

The editor works standalone for editing workflows. To execute workflows, run the backend:

```bash
# Install
uv tool install lexflow-web

# Run (starts both API server and serves the web UI)
lexflow-web

# Or with options
lexflow-web --host 0.0.0.0 --port 8080
```

The backend provides:
- `/api/execute` - Execute workflows
- `/api/validate` - Validate workflow syntax
- `/api/opcodes` - List available opcodes
- `/ws/execute` - WebSocket for streaming execution

## Development

```bash
cd lexflow-web/frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build library
npm run build:all
```

## Architecture

```
lexflow-web/
├── frontend/           # React + TypeScript frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── lib/        # Embeddable library exports
│   │   ├── store/      # Zustand state management
│   │   └── services/   # Workflow parsing & layout
│   └── dist/           # Built library files
└── lexflow_web/        # Python backend (FastAPI)
```
