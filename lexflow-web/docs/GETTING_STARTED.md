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
# Clone the repository
git clone https://github.com/yourusername/lex-flow.git
cd lex-flow

# Install Python dependencies
uv sync --all-extras

# Start the server
cd lexflow-web
uv run python -m lexflow_web.app
```

Open http://localhost:8000 in your browser. The pre-built frontend is served from `src/lexflow_web/static/`.

### Option 2: Development Setup (Hot Reload)

For frontend development with live reloading:

```bash
# Clone the repository
git clone https://github.com/yourusername/lex-flow.git
cd lex-flow

# Install Python dependencies
uv sync --all-extras

# Install frontend dependencies
cd lexflow-web/frontend
npm install
```

**Start both servers:**

```bash
# Terminal 1: Backend (from lexflow-web directory)
cd lexflow-web
uv run python -m lexflow_web.app --reload --port 8000

# Terminal 2: Frontend dev server (from frontend directory)
cd lexflow-web/frontend
npm run dev
```

The frontend dev server runs on http://localhost:5173 and proxies API requests to the backend on port 8000.

## Server Options

```bash
# Start on custom host/port
uv run python -m lexflow_web.app --host 0.0.0.0 --port 3000

# Enable auto-reload for development
uv run python -m lexflow_web.app --reload

# View all options
uv run python -m lexflow_web.app --help
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
│   ├── visualization.py         # Tree generation (legacy)
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
uv run python -m lexflow_web.app --port 3000
```

### Frontend dev server issues

**npm install fails:**
```bash
# Clear npm cache and retry
npm cache clean --force
rm -rf node_modules
npm install
```

**Proxy errors (cannot connect to backend):**
- Ensure the backend is running on port 8000
- Check that vite.config.ts has the correct proxy settings

### Parsing errors

If workflows fail to parse:
- Check the YAML syntax (indentation matters)
- Ensure all node IDs are unique
- Verify the `start` node exists and has a `next` reference

### WebSocket connection fails

If execution doesn't show streaming output:
- Check browser console for WebSocket errors
- Verify the backend is accessible
- Try the REST fallback: The frontend automatically falls back to REST if WebSocket fails

## Next Steps

- **[User Guide](USER_GUIDE.md)** - Learn how to use the visual editor
- **[Customization](CUSTOMIZATION.md)** - Configure backends and providers
- **[LexFlow Docs](../../docs/README.md)** - Learn the LexFlow language
