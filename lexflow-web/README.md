# LexFlow Web

A visual workflow editor and execution environment for LexFlow. Build workflows by dragging and connecting nodes, or write YAML/JSON directly in the integrated code editor.

![LexFlow Web Editor](example.png)

## Features

- **Visual Node Editor**: Drag-and-drop workflow creation with Scratch-inspired blocks
- **Live Code Sync**: Changes in the visual editor sync with YAML/JSON code and vice-versa
- **Real-time Execution**: Run workflows with streaming output via WebSocket
- **Client-side Parsing**: Workflow visualization happens entirely in the browser
- **Customizable Backend**: Swap the execution backend or run fully offline

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend development)
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lex-flow.git
cd lex-flow

# Install dependencies (from monorepo root)
uv sync --all-extras

# Start the server
cd lexflow-web
uv run python -m lexflow_web.app
```

Open http://localhost:8000 in your browser.

### Running in Development Mode

For frontend development with hot reload:

```bash
# Terminal 1: Start backend
cd lexflow-web
uv run python -m lexflow_web.app --reload

# Terminal 2: Start frontend dev server
cd lexflow-web/frontend
npm install
npm run dev
```

The frontend dev server runs on http://localhost:5173 and proxies API requests to the backend.

## Documentation

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and setup guide
- **[User Guide](docs/USER_GUIDE.md)** - How to use the visual editor
- **[Customization](docs/CUSTOMIZATION.md)** - Custom backends and providers

## Architecture

```
lexflow-web/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # UI components (Canvas, Editor, Palette, etc.)
│   │   ├── hooks/         # React hooks (parsing, WebSocket, shortcuts)
│   │   ├── providers/     # Backend abstraction layer
│   │   ├── services/      # Client-side visualization & parsing
│   │   └── store/         # Zustand state management
│   └── ...
└── src/lexflow_web/       # Python FastAPI backend
    ├── api.py             # REST API endpoints
    ├── websocket.py       # WebSocket execution handler
    └── app.py             # Application entry point
```

### Key Design Decisions

1. **Client-side Parsing**: Workflow visualization (tree generation) happens in the browser via TypeScript, not the backend. This makes the frontend portable and reduces latency.

2. **Backend Provider Pattern**: The frontend uses a `BackendProvider` interface for all backend communication. You can swap backends by implementing this interface.

3. **Dual Editing Modes**: Edit workflows visually (drag-and-drop) or as code (YAML/JSON). Both stay in sync.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/opcodes` | GET | List available opcodes |
| `/api/examples` | GET | List example workflows |
| `/api/examples/{path}` | GET | Get example content |
| `/api/execute` | POST | Execute workflow (REST) |
| `/api/validate` | POST | Validate workflow syntax |
| `/ws/execute` | WebSocket | Execute with streaming output |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |
| `VITE_WS_URL` | (auto) | WebSocket URL (derived from API URL if not set) |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `npm test` (frontend), `pytest` (backend)
5. Submit a pull request

## License

MIT
