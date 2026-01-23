# LexFlow Web Frontend Rewrite - Progress

## Overview

Rewrote the monolithic vanilla JS frontend to React + Vite + TypeScript with Scratch/n8n-inspired UX.

## Tech Stack

- **React 18** + **Vite** + **TypeScript**
- **Zustand** for state management (with persist middleware)
- **Monaco Editor** for YAML editing
- **CSS Modules** with Inspira Dark theme

## Project Structure

```
lexflow-web/frontend/
├── src/
│   ├── api/                 # API client + TypeScript types
│   │   ├── types.ts         # All type definitions
│   │   ├── client.ts        # REST API client
│   │   └── index.ts
│   ├── store/               # Zustand stores
│   │   ├── workflowStore.ts # Source, tree, history, execution
│   │   ├── uiStore.ts       # Panels, zoom, node status
│   │   └── index.ts
│   ├── hooks/               # Custom React hooks
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useWebSocket.ts  # WebSocket execution
│   │   └── index.ts
│   ├── components/
│   │   ├── layout/          # Header, MainLayout
│   │   ├── editor/          # Monaco CodeEditor
│   │   ├── visualization/   # Canvas, WorkflowNode, Connection
│   │   ├── execution/       # ExecutionPanel
│   │   ├── node-editor/     # NodeEditorPanel (slide-in)
│   │   └── palette/         # NodePalette (drawer)
│   ├── styles/
│   │   └── variables.css    # CSS variables (Inspira Dark)
│   ├── App.tsx
│   └── main.tsx
├── vite.config.ts           # Build to ../src/lexflow_web/static/
├── package.json
├── ISSUES.md                # Known bugs & future enhancements
└── PROGRESS.md              # This file
```

## Completed Features

### Phase 1: Project Setup ✅
- Vite + React + TypeScript initialized
- Build outputs to `../src/lexflow_web/static/`
- Zustand stores set up
- CSS variables extracted from original theme

### Phase 2: Editor Integration ✅
- Monaco Editor with YAML syntax
- Debounced parsing (500ms)
- Parse status indicator
- Custom "lexflow-dark" theme
- "Find in Source" - jumps to node line

### Phase 3: Canvas Visualization ✅
- SVG-based canvas with pan/zoom
- n8n-style node cards with color-coded categories:
  - Control (orange), Data (green), I/O (cyan)
  - Operator (purple), Workflow (magenta)
- Bezier curve connections with animated flow dots
- Branch labels (THEN/ELSE/BODY/etc.)

### Phase 4: Execution Panel ✅
- WebSocket streaming output (real-time)
- Blinking cursor animation
- Stop/Cancel button
- Workflow inputs form
- Result display

### Phase 5: Node Editor ✅
- Slide-in panel (click node to open)
- Shows opcode, inputs, branches, config
- Opcode descriptions from catalog
- Parameter info (type, required)
- Copy node ID to clipboard
- "Find in Source" button

### Phase 6: Node Palette ✅
- Drawer overlay (Ctrl+P or + button)
- Categorized opcodes with icons
- Search/filter functionality
- Expandable opcode details

### Additional Features ✅
- **LocalStorage persistence** - workflow saves between sessions
- **Keyboard shortcuts**:
  - `Escape` - close panels, deselect node
  - `Ctrl+B` - toggle editor
  - `Ctrl+D` - duplicate selected node
  - `Ctrl+E` - toggle execution panel
  - `Ctrl+P` - toggle palette
  - `Ctrl+F` - search nodes on canvas
  - `Ctrl+Z` - undo (outside editor)
  - `Ctrl+Y` / `Ctrl+Shift+Z` - redo
  - `Ctrl+0` - reset zoom
  - `Delete` / `Backspace` - delete selected node
- **File operations** (header buttons):
  - New workflow
  - Import (upload .yaml/.yml/.json)
  - Export (download workflow.yaml)
- **Undo/Redo** - 50-step history stack
- **Examples dropdown** - grouped by category
- **Mini-map** - small canvas preview in bottom-left corner for navigation
- **Node search** - Ctrl+F to search nodes by ID, opcode, or type with highlight
- **Delete node** - Del/Backspace to delete selected node with confirmation
- **Multi-workflow support** - Files with multiple workflows display each in a dotted border with name label
- **Draggable workflows** - Drag workflow groups by their header to reposition them on the canvas
- **Drag-drop from palette** - Drag opcodes from palette to canvas to add new nodes
- **Inline node editing** - Click on literal or variable inputs to edit values directly
- **Duplicate node** - Copy selected nodes with Ctrl+D or Duplicate button

## Known Issues

See `ISSUES.md` for full list.

### Bugs (Fixed)
- [x] ~~**Node hover flickering** - fixed by removing CSS transform on hover~~
- [x] ~~**Workflow group dragging broken** - fixed stale closure in `onDrag` callback using `useUiStore.getState()`~~

## Remaining Roadmap

1. ~~**Drag-drop from palette**~~ - DONE: drag opcodes to canvas to add nodes
2. ~~**Delete node**~~ - DONE: remove node from YAML
3. ~~**Inline node editing**~~ - DONE: edit values in side panel
4. ~~**Duplicate node**~~ - DONE: copy selected node

**Future Enhancements:**
- Connection editing - create/remove node connections visually
- Node reordering - drag nodes to change execution order
- Workflow templates - quick-start with common patterns

## Build & Run

```bash
# Development (with hot reload)
cd frontend
npm run dev
# Then run backend: lexflow-web --reload

# Production build
cd frontend
npm run build
# Start server: lexflow-web
# Open http://localhost:8000
```

## Key Files to Know

- `src/store/workflowStore.ts` - main state (source, history, execution)
- `src/components/visualization/Canvas.tsx` - SVG canvas + layout algorithm
- `src/components/visualization/WorkflowNode.tsx` - node card component
- `src/hooks/useWebSocket.ts` - WebSocket execution streaming
- `src/hooks/useKeyboardShortcuts.ts` - all keyboard shortcuts

## Style Guide

- **Node colors**: Scratch-inspired category colors
- **Theme**: Inspira Dark (slate/cyan palette)
- **Fonts**: Inter, Plus Jakarta Sans, JetBrains Mono (code)
- **Interactions**: n8n-style (click node → slide-in panel)
