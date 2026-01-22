# Known Issues & Roadmap

## Bugs

- [x] ~~**Node hover flickering** - Nodes flicker when hovering. Fixed by removing CSS transform on hover.~~
- [x] ~~**Workflow group dragging broken** - Dragging workflow groups didn't work properly (only quick flicks moved them). Fixed by using `useUiStore.getState()` in the `onDrag` callback to read current position instead of stale closure value.~~

## Completed Features

- [x] Canvas-based node visualization with pan/zoom
- [x] n8n-style node cards with Scratch-inspired colors
- [x] Bezier curve connections with animated flow dots
- [x] Monaco editor with YAML syntax highlighting
- [x] Slide-in node editor panel
- [x] Node palette drawer with search
- [x] LocalStorage persistence for workflow source
- [x] Keyboard shortcuts (Escape, Ctrl+B/E/P/Z/Y/0)
- [x] WebSocket streaming execution with cancel button
- [x] "Find in Source" button in node editor
- [x] Copy node ID to clipboard
- [x] Opcode descriptions and parameter info
- [x] File operations: New, Import, Export
- [x] Undo/Redo with 50-step history
- [x] Mini-map for large workflow navigation
- [x] Node search/filter with Ctrl+F
- [x] Delete node action with confirmation (Del/Backspace key)
- [x] Multi-workflow visualization with dotted borders and labels
- [x] Draggable workflow groups (drag header to reposition)

## Roadmap (Priority Order)

1. **Drag-drop from palette** - Drag opcodes from palette to canvas to add nodes
2. **Inline node editing** - Edit node values directly in side panel, save to YAML
3. **Duplicate node** - Copy selected node with new ID

## Future Ideas

- Multiple workflow tabs
- Workflow validation warnings
- Node execution status during run (highlight running node)
- Zoom to fit all nodes
- Auto-layout button
- Dark/light theme toggle
- Export as image/SVG
