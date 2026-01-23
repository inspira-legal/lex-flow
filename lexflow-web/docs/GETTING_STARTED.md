# Getting Started with LexFlow Web

This guide walks you through setting up and running LexFlow Web locally.

## Prerequisites

- **Python 3.10+** - For the backend server
- **Node.js 18+** - For frontend development (optional for production use)
- **uv** - Fast Python package manager ([install guide](https://docs.astral.sh/uv/))

## Installation Options

### Option 1: Quick Start (Pre-built Frontend)

If you just want to run LexFlow Web without modifying the frontend:

```bash
# Install Python dependencies
uv sync --all-extras

# Start the server
uv run lexflow-web
```

Open http://localhost:8000 in your browser. The pre-built frontend is served from `src/lexflow_web/static/`.

### Option 2: Development Setup (Hot Reload)

For frontend development with live reloading:

```bash
# Install Python dependencies
uv sync --all-extras

# Install frontend dependencies
cd lexflow-web/frontend
npm install
```

**Start both servers:**

```bash
# Terminal 1: Backend
uv run lexflow-web --reload --port 8000

# Terminal 2: Frontend dev server (from frontend directory)
cd lexflow-web/frontend
npm run dev
```

Open http://localhost:5173 in your browser. The frontend automatically connects to the backend on port 8000.

## Server Options

```bash
# Start on custom host/port
uv run lexflow-web --host 0.0.0.0 --port 3000

# Enable auto-reload for development
uv run lexflow-web --reload

# View all options
uv run lexflow-web --help
```

## Building the Frontend

To build the frontend for production:

```bash
cd lexflow-web/frontend
npm run build
```

This outputs to `src/lexflow_web/static/`, which the backend serves automatically.

## Project Structure

```
lexflow-web/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/          # UI components
│   │   │   ├── editor/          # Monaco code editor
│   │   │   ├── execution/       # Execution panel
│   │   │   ├── layout/          # Main layout
│   │   │   ├── node-editor/     # Node property editor
│   │   │   ├── palette/         # Opcode palette
│   │   │   └── visualization/   # Canvas and node rendering
│   │   ├── hooks/               # React hooks
│   │   ├── providers/           # Backend abstraction
│   │   ├── services/            # Client-side services
│   │   ├── store/               # Zustand state management
│   │   ├── App.tsx              # Main component
│   │   └── main.tsx             # Entry point
│   ├── package.json
│   └── vite.config.ts
├── src/lexflow_web/             # Python backend
│   ├── api.py                   # REST endpoints
│   ├── websocket.py             # WebSocket handler
│   ├── visualization.py         # Tree generation for API responses
│   ├── app.py                   # FastAPI app
│   └── static/                  # Built frontend files
├── docs/                        # Documentation
└── pyproject.toml
```

## Verifying Installation

After starting the server, verify everything works:

1. **Open the editor**: Navigate to http://localhost:8000 (or http://localhost:5173 for dev)

2. **Check the palette**: The left sidebar should show available opcodes organized by category

3. **Load an example**: Click an example from the examples panel to load it

4. **Run a workflow**: Click the "Run" button to execute the current workflow

5. **Edit visually**: Click nodes on the canvas to edit their properties

6. **Edit as code**: Toggle the code editor to modify YAML directly

## Troubleshooting

### Backend won't start

**Module not found errors:**
```bash
# Ensure you're in the lexflow-web directory
cd lexflow-web

# Verify lexflow is installed
uv pip list | grep lexflow
```

**Port already in use:**
```bash
# Use a different port
uv run lexflow-web --port 3000
```

### Frontend dev server issues

**npm install fails:**
```bash
# Delete the node_modules folder and try again
rm -rf node_modules
npm install
```

**Cannot connect to backend:**
- Make sure the backend is running on port 8000
- Try restarting both the frontend and backend servers

### Workflow won't load

If your workflow shows errors or won't display:
- Check your spacing - YAML uses indentation (spaces, not tabs)
- Make sure each node has a unique ID
- Every workflow needs a `start` node that points to the first action

### Live output not working

If you don't see output appearing in real-time while a workflow runs:
- Make sure the backend server is running
- Try refreshing the page
- Don't worry - the editor will still show results when the workflow finishes

## Next Steps

- **[User Guide](USER_GUIDE.md)** - Learn how to use the visual editor
- **[Customization](CUSTOMIZATION.md)** - Configure backends and providers
- **[LexFlow Docs](../../docs/README.md)** - Learn the LexFlow language
