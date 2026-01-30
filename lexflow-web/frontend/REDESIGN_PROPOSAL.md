# LexFlow Visual Editor Redesign Proposal

## Design Direction: "Precision Instrument"

The aesthetic is **utilitarian precision** — think high-end audio equipment, professional video editing software, or scientific instruments. Not cold and sterile, but **warm industrial**: purposeful, tactile, and satisfying to use.

**Core principles:**
- **Dense but not cluttered** — information-rich UI that respects expert users
- **Subtle depth** — layered panels with soft shadows and slight elevation
- **Warm neutrals** — move away from the typical cold blue-grays
- **Crisp typography** — monospace accents, clear hierarchy
- **Purposeful color** — color means something (node types, states), not decoration

---

## 1. Architecture

### Folder Structure

```
lexflow-web/frontend/src/
├── components/
│   ├── ui/                          # Base design system components
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── styles.ts            # CVA variants
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   ├── Panel/
│   │   ├── Input/
│   │   ├── Select/
│   │   ├── Badge/
│   │   ├── Tooltip/
│   │   ├── IconButton/
│   │   └── index.ts                 # Barrel export
│   │
│   ├── canvas/                      # Canvas-specific components
│   │   ├── Canvas/
│   │   ├── CanvasNode/
│   │   ├── Connection/
│   │   ├── StartNode/
│   │   ├── WorkflowGroup/
│   │   ├── Port/
│   │   ├── Minimap/
│   │   └── index.ts
│   │
│   ├── panels/                      # Panel components
│   │   ├── CodeEditor/
│   │   ├── NodeEditor/
│   │   ├── ExecutionPanel/
│   │   ├── Palette/
│   │   └── index.ts
│   │
│   ├── layout/                      # Layout components
│   │   ├── Header/
│   │   ├── MainLayout/
│   │   ├── PanelResizer/
│   │   └── index.ts
│   │
│   └── icons/                       # Icon components
│       ├── Icon.tsx                 # Wrapper component
│       ├── icons/                   # Individual icon SVGs as components
│       └── index.ts
│
├── hooks/                           # PRESERVE - existing hooks
│   ├── useCanvasInteraction.ts
│   ├── useNodeOperations.ts
│   ├── useNodePorts.ts
│   ├── useKeyboardShortcuts.ts
│   └── useExecution.ts
│
├── services/                        # PRESERVE - business logic
│   ├── workflow/
│   ├── layout/
│   ├── grammar/
│   └── parser/
│
├── store/                           # PRESERVE - Zustand stores
│   ├── workflowStore.ts
│   ├── uiStore.ts
│   ├── selectionStore.ts
│   └── executionStore.ts
│
├── styles/
│   ├── index.css                    # Tailwind imports + base styles
│   ├── fonts.css                    # Font imports
│   └── tokens.css                   # CSS custom properties for theming
│
├── lib/
│   ├── cn.ts                        # clsx + twMerge utility
│   └── theme.ts                     # Theme context and hook
│
├── types/
│   └── index.ts                     # Shared types
│
├── App.tsx
└── main.tsx
```

### Technology Stack

- **Tailwind CSS 4** — utility-first CSS with native CSS variables
- **CVA (class-variance-authority)** — type-safe component variants
- **clsx + tailwind-merge** — conditional class merging
- **Geist font family** — clean, modern typography (sans + mono)

---

## 2. Theme System

### Color Tokens (Dark Theme - Default)

```css
@theme {
  /* Warm neutral palette */
  --color-surface-0: oklch(0.12 0.01 60);      /* Deepest background */
  --color-surface-1: oklch(0.15 0.01 60);      /* Panel background */
  --color-surface-2: oklch(0.18 0.01 60);      /* Elevated elements */
  --color-surface-3: oklch(0.22 0.01 60);      /* Hover states */
  --color-surface-4: oklch(0.28 0.01 60);      /* Active states */

  --color-border-subtle: oklch(0.25 0.01 60);
  --color-border-default: oklch(0.32 0.01 60);
  --color-border-strong: oklch(0.45 0.01 60);

  --color-text-muted: oklch(0.55 0.01 60);
  --color-text-secondary: oklch(0.70 0.01 60);
  --color-text-primary: oklch(0.92 0.01 60);

  /* Accent colors - purposeful, not decorative */
  --color-accent-blue: oklch(0.65 0.18 240);     /* Primary actions */
  --color-accent-green: oklch(0.72 0.16 145);    /* Success, connected */
  --color-accent-amber: oklch(0.75 0.15 75);     /* Warning, pending */
  --color-accent-red: oklch(0.65 0.20 25);       /* Error, disconnect */
  --color-accent-violet: oklch(0.55 0.18 290);   /* Special, AI ops */

  /* Node category colors - semantic meaning */
  --color-node-control: oklch(0.55 0.12 240);    /* Control flow */
  --color-node-data: oklch(0.55 0.12 145);       /* Data operations */
  --color-node-io: oklch(0.55 0.12 75);          /* Input/Output */
  --color-node-logic: oklch(0.55 0.12 290);      /* Logic/comparison */
  --color-node-math: oklch(0.55 0.12 25);        /* Math operations */
  --color-node-string: oklch(0.55 0.12 180);     /* String operations */

  /* Typography */
  --font-sans: 'Geist', system-ui, sans-serif;
  --font-mono: 'Geist Mono', 'JetBrains Mono', monospace;
}
```

### Light Theme Override

```css
@theme (.light) {
  --color-surface-0: oklch(0.98 0.005 60);
  --color-surface-1: oklch(0.96 0.005 60);
  --color-surface-2: oklch(0.94 0.008 60);
  --color-surface-3: oklch(0.90 0.010 60);
  --color-surface-4: oklch(0.85 0.012 60);

  --color-border-subtle: oklch(0.90 0.008 60);
  --color-border-default: oklch(0.82 0.010 60);
  --color-border-strong: oklch(0.70 0.012 60);

  --color-text-muted: oklch(0.55 0.01 60);
  --color-text-secondary: oklch(0.40 0.01 60);
  --color-text-primary: oklch(0.15 0.01 60);
}
```

---

## 3. Component Architecture

### File Structure Per Component

```
Button/
├── Button.tsx      # Implementation with forwardRef
├── styles.ts       # CVA variants
├── types.ts        # TypeScript interfaces
└── index.ts        # Barrel export
```

### CVA Pattern

```typescript
// styles.ts
import { cva } from 'class-variance-authority'

export const buttonVariants = cva(
  ['base', 'classes', 'here'],
  {
    variants: {
      variant: {
        solid: 'bg-accent-blue text-white',
        soft: 'bg-surface-3 text-text-primary',
        ghost: 'text-text-secondary hover:bg-surface-3',
      },
      size: {
        sm: 'h-7 px-2.5 text-xs',
        md: 'h-8 px-3 text-sm',
        lg: 'h-10 px-4 text-sm',
      },
    },
    defaultVariants: {
      variant: 'soft',
      size: 'md',
    },
  }
)
```

### Component Pattern

```typescript
// Button.tsx
import { forwardRef } from 'react'
import { cn } from '@/lib/cn'
import { buttonVariants } from './styles'
import type { ButtonProps } from './types'

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button({ variant, size, className, children, ...props }, ref) {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)

export { Button }
```

---

## 4. What to Preserve (DO NOT CHANGE)

### Zustand Stores
- `workflowStore.ts` — source, tree, execution state, undo/redo
- `uiStore.ts` — zoom, pan, panel states, dragging states, slot registry
- `selectionStore.ts` — node/reporter/connection selection
- `executionStore.ts` — web opcode state

### Services
- `WorkflowService.ts` — all YAML manipulation functions
- `LayoutService.ts` — node positioning calculations
- `GrammarService.ts` — opcode definitions and colors
- Parser service — YAML to tree conversion

### Hooks
- `useCanvasInteraction.ts` — zoom, pan, wire/orphan/variable dragging
- `useNodeOperations.ts` — node CRUD abstraction
- `useNodePorts.ts` — port interaction handling
- `useKeyboardShortcuts.ts` — all keyboard shortcuts
- `useExecution.ts` — execution management

### Critical Data Structures
- `WorkflowTree`, `Workflow`, `TreeNode`, `FormattedValue`
- `DraggingWire`, `DraggingOrphan`, `DraggingVariable`
- `NodeSlotPositions` — slot position registry

---

## 5. Phased Implementation Plan

### Phase 1: Foundation (Week 1)

**Goal:** Set up new architecture without breaking existing functionality

1. Install dependencies:
   ```bash
   npm install tailwindcss@next @tailwindcss/vite class-variance-authority clsx tailwind-merge
   ```

2. Configure Tailwind 4 + Vite (keep old CSS working in parallel)

3. Create base files:
   - `src/lib/cn.ts` — class merging utility
   - `src/lib/theme.ts` — theme context and hook
   - `src/styles/index.css` — Tailwind with tokens

4. Build base UI components:
   - Button, IconButton
   - Panel
   - Input, Select
   - Badge, Tooltip

5. **Testing:** Render new components alongside old ones to verify

### Phase 2: Layout Shell (Week 2)

**Goal:** Replace layout components while keeping canvas untouched

1. Build layout components:
   - Header
   - MainLayout
   - PanelResizer

2. Wrap existing canvas in new layout

3. Add theme toggle (light/dark mode working)

4. **Testing:** Full app functional with mixed old/new components

### Phase 3: Panels (Week 3)

**Goal:** Rebuild all panel internals

1. NodeEditor panel — new styling, keep logic hooks
2. Palette panel — new node browser UI
3. ExecutionPanel — new output display
4. CodeEditor wrapper — Monaco integration with new theme

5. **Testing:** All panels functional, all store interactions working

### Phase 4: Canvas (Week 4)

**Goal:** Rebuild canvas visuals — highest risk, most reward

1. Build new components:
   - CanvasNode (new styling)
   - Port (new connection points)
   - Connection (new wire styling)
   - StartNode, WorkflowGroup

2. Integrate with existing hooks (update slot registry calls)

3. **Testing:** Extensive manual testing of all interactions

### Phase 5: Polish (Week 5)

**Goal:** Refinement and cleanup

1. Remove all old CSS modules and components
2. Animation polish
3. Accessibility audit
4. Performance check

---

## 6. Testing Strategy

### Per-Phase Checklist

- [ ] All keyboard shortcuts work
- [ ] Undo/redo works
- [ ] Node selection works
- [ ] Wire connections work
- [ ] Drag operations work
- [ ] Zoom/pan works
- [ ] Theme switching works
- [ ] Panel toggles work
- [ ] Execution works
- [ ] Monaco editor works

### Critical Interactions to Test

1. **Wire dragging** — from output port to input port with snap detection
2. **Orphan conversion** — drag orphan node to input slot
3. **Variable dragging** — drag variable from palette to input slot
4. **Node positioning** — manual drag with layout mode support
5. **Slot registry** — positions update correctly on scroll/zoom

---

## 7. Visual Design Reference

```
┌────────────────────────────────────────────────────────────────────┐
│ [◆] LexFlow  │  Palette  Code  │                    │ ▶ Run │ ☀ │
├──────────────┴─────────────────┴────────────────────┴───────┴─────┤
│                                                                    │
│  ┌─────────────────────┐                                          │
│  │ main                │                                          │
│  │ ─────────────────── │                                          │
│  │ ○ inputs            │     ┌─────────────────────┐              │
│  │ ○ variables         │────▶│ print_hello         │              │
│  └─────────────────────┘     │ ─────────────────── │              │
│                              │ io_print            │              │
│                              │ ○ message: "Hello"  │──▶           │
│                              └─────────────────────┘              │
│                                                                    │
│                                                     [  100%  ][⊞] │
├────────────────────────────────────────────────────────────────────┤
│ EXECUTION                                            │ ✓ Success  │
│────────────────────────────────────────────────────────────────────│
│ Hello                                                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Key visual characteristics:**
- Warm gray backgrounds (not blue-tinted)
- Subtle rounded corners (8px nodes, 12px panels)
- Thin borders with elevation hierarchy
- Monospace accents for IDs/opcodes
- Color only for semantic meaning (node categories, states)
- Ample padding, clear visual hierarchy
