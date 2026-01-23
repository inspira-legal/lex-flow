# LexFlow Web Frontend

The React-based visual editor for LexFlow workflows.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (with hot reload)
npm run dev
```

Open http://localhost:5173 in your browser. Make sure the backend is running on port 8000.

## Building for Production

```bash
npm run build
```

This outputs to `../src/lexflow_web/static/`, which the backend serves automatically.

## Project Structure

```
src/
├── components/          # UI components
│   ├── editor/          # Code editor (YAML/JSON)
│   ├── execution/       # Run panel and output
│   ├── layout/          # Page layout
│   ├── node-editor/     # Node property panel
│   ├── palette/         # Opcode browser
│   └── visualization/   # Canvas and nodes
├── hooks/               # React hooks
├── providers/           # Backend connection
├── services/            # Parsing and visualization
├── store/               # App state (Zustand)
└── styles/              # CSS and theming
```

## Key Features

- **Visual Canvas**: Drag-and-drop workflow editing
- **Code Editor**: Edit YAML/JSON directly with syntax highlighting
- **Live Sync**: Visual and code views stay in sync
- **Real-time Output**: See workflow output as it runs
- **Keyboard Shortcuts**: Ctrl+Z (undo), Ctrl+B (toggle editor), and more

## Development Notes

- Uses Vite for fast development builds
- State management with Zustand
- Monaco Editor for code editing
- CSS Modules for styling

See the main [User Guide](../docs/USER_GUIDE.md) for how to use the editor.
