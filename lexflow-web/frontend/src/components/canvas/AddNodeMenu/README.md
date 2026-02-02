# AddNodeMenu Component

A searchable, categorized dropdown menu for adding new opcodes to the LexFlow workflow editor. This component displays when the user clicks the "+" button on a node.

## Features

- **Categorized Display**: Opcodes are organized by category (Control, Data, I/O, etc.) with visual icons
- **Real-time Search**: Filter opcodes by name and description as you type
- **Search Highlighting**: Matching text is highlighted in search results
- **Keyboard Support**:
  - Escape key to close menu
  - Auto-focus on search input when opened
- **Smart Positioning**: Menu automatically adjusts to stay within viewport bounds
- **Click-outside Detection**: Closes menu when clicking outside
- **Collapsible Categories**: Categories can be expanded/collapsed to browse opcodes

## Usage

```typescript
import { AddNodeMenu } from "@/components/canvas"
import { useWorkflowStore } from "@/store"

function YourComponent() {
  const { opcodes } = useWorkflowStore()
  const [menuPosition, setMenuPosition] = useState<{ x: number; y: number } | null>(null)

  const handleAddNode = (opcode: OpcodeInterface) => {
    // Handle adding the selected opcode to the workflow
    console.log("Selected opcode:", opcode.name)
  }

  return (
    <>
      <button onClick={(e) => setMenuPosition({ x: e.clientX, y: e.clientY })}>
        Add Node
      </button>

      {menuPosition && (
        <AddNodeMenu
          x={menuPosition.x}
          y={menuPosition.y}
          opcodes={opcodes}
          onSelect={handleAddNode}
          onClose={() => setMenuPosition(null)}
        />
      )}
    </>
  )
}
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| `x` | `number` | Horizontal position (pixels from left) |
| `y` | `number` | Vertical position (pixels from top) |
| `opcodes` | `OpcodeInterface[]` | Array of available opcodes to display |
| `onSelect` | `(opcode: OpcodeInterface) => void` | Callback when an opcode is selected |
| `onClose` | `() => void` | Callback to close the menu |

## File Structure

```
AddNodeMenu/
├── index.ts              # Barrel export (public API)
├── AddNodeMenu.tsx       # Main component implementation
├── types.ts              # TypeScript interfaces
├── styles.ts             # CVA style variants
└── README.md            # Documentation
```

## Styling Patterns

The component uses `class-variance-authority` (CVA) for styling variants and Tailwind CSS with CSS variables:

```typescript
// Example from styles.ts
export const menuVariants = cva(
  "w-[320px] max-h-[480px] bg-surface-1 border border-border-subtle rounded-md shadow-lg flex flex-col animate-scale-in"
)
```

CSS variables used:
- `--cat-color`: Dynamic category color for icons
- Color tokens: `surface-*`, `border-*`, `text-*`, `accent-*`

## Architecture Decisions

### 1. Colocation Pattern
All related files are co-located in the same directory, following the established project pattern.

### 2. Search Functionality
Search filters both opcode names and descriptions case-insensitively, providing a comprehensive search experience.

### 3. Category Grouping
Uses the same category grouping logic as NodePalette for consistency:
- Categories defined in grammar service
- Opcodes matched by prefix
- Unmatched opcodes go to "Other" category

### 4. Positioning Logic
Menu position is adjusted to prevent overflow:
```typescript
const adjustedX = Math.min(x, window.innerWidth - 340)
const adjustedY = Math.min(y, window.innerHeight - 500)
```

### 5. State Management
- Local state for search query and expanded category
- No global state dependencies (receives opcodes as props)
- Controlled component pattern (parent manages open/close state)

## Keyboard Interactions

- **Escape**: Close menu
- **Type**: Auto-focuses search input, filters results
- **Click Outside**: Closes menu

## Accessibility

- `role="menu"` on container
- `role="menuitem"` on selectable items
- `aria-label="Add node menu"` for screen readers
- Semantic HTML buttons for interactive elements

## Performance Considerations

- `useMemo` for expensive computations (grouping, filtering)
- Event listeners cleaned up on unmount
- Efficient search with lowercase comparison
- Categories only render when expanded

## Integration Points

### Dependencies
- `@/api/types`: OpcodeInterface type definition
- `@/services/grammar`: Category metadata (getCategories, getCategoryByOpcode)
- `@/lib/cn`: className utility for Tailwind merge
- `class-variance-authority`: Style variant management

### CSS Animation
Uses `animate-scale-in` from global CSS for smooth appearance.

## Testing Recommendations

1. **Search Functionality**
   - Test case-insensitive search
   - Test search by name and description
   - Test empty search results

2. **Category Behavior**
   - Test category expansion/collapse
   - Test empty categories (should not render)
   - Test "Other" category with uncategorized opcodes

3. **Keyboard Interactions**
   - Test Escape key closes menu
   - Test search input auto-focus

4. **Position Adjustment**
   - Test menu near right edge of viewport
   - Test menu near bottom edge of viewport

5. **Click Outside**
   - Test clicking outside closes menu
   - Test clicking on menu items doesn't close until after callback

## Future Enhancements

Potential improvements for future iterations:

1. **Keyboard Navigation**: Arrow keys to navigate through opcode list
2. **Recent Opcodes**: Show recently used opcodes at the top
3. **Favorites**: Allow users to favorite frequently used opcodes
4. **Opcode Preview**: Show parameter details on hover
5. **Custom Shortcuts**: Quick access to common opcodes via keyboard shortcuts
6. **Drag Support**: Allow dragging opcodes from menu to canvas
