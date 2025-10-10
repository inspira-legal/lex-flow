"""Pygame opcodes for LexFlow - Visual workflow examples.

These opcodes are designed to be composed in workflows, with the game loop
controlled by LexFlow's control_while instead of being hidden in opcodes.
"""

import asyncio
from lexflow import opcode

try:
    import pygame
except ImportError:
    print("pygame not installed. Install with: pip install pygame")
    raise


# ============================================================================
# Pygame Initialization & Window Management
# ============================================================================

@opcode()
async def pygame_init() -> None:
    """Initialize pygame engine."""
    pygame.init()


@opcode()
async def pygame_create_window(
    width: int, height: int, title: str = "LexFlow + Pygame"
) -> pygame.Surface:
    """Create a pygame window and return the display surface."""
    screen = pygame.display.set_mode((int(width), int(height)))
    pygame.display.set_caption(title)
    return screen


@opcode()
async def pygame_quit() -> None:
    """Quit pygame and close all windows."""
    pygame.quit()


# ============================================================================
# Event Handling (for workflow-controlled loops)
# ============================================================================

@opcode()
async def pygame_should_quit() -> bool:
    """Check if user wants to quit (clicked X button).

    Returns True if quit event detected, False otherwise.
    Use this in control_while conditions for game loops.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False


@opcode()
async def pygame_process_events() -> None:
    """Process pygame events (keeps window responsive).

    Call this in your game loop to prevent window freezing.
    """
    pygame.event.pump()


@opcode()
async def pygame_get_key_pressed(key_name: str) -> bool:
    """Check if a specific key is currently pressed.

    Args:
        key_name: Key name (e.g., "up", "down", "left", "right", "space", "w", "a", "s", "d")

    Returns:
        True if key is pressed, False otherwise
    """
    keys = pygame.key.get_pressed()

    # Map common key names to pygame constants
    key_map = {
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "space": pygame.K_SPACE,
        "w": pygame.K_w,
        "a": pygame.K_a,
        "s": pygame.K_s,
        "d": pygame.K_d,
        "escape": pygame.K_ESCAPE,
        "return": pygame.K_RETURN,
    }

    key_name_lower = key_name.lower()
    if key_name_lower in key_map:
        return bool(keys[key_map[key_name_lower]])

    return False


# ============================================================================
# Drawing Operations
# ============================================================================

@opcode()
async def pygame_fill_screen(screen: pygame.Surface, color: list) -> None:
    """Fill the entire screen with a color.

    Args:
        screen: The display surface
        color: RGB color as [r, g, b] where each value is 0-255
    """
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    screen.fill((r, g, b))


@opcode()
async def pygame_draw_text(
    screen: pygame.Surface,
    text: str,
    x: int,
    y: int,
    font_size: int = 48,
    color: list = None,
) -> None:
    """Draw text on the screen.

    Args:
        screen: The display surface
        text: Text to render
        x: X position (left edge)
        y: Y position (top edge)
        font_size: Font size in pixels
        color: RGB color as [r, g, b], defaults to white
    """
    if color is None:
        color = [255, 255, 255]

    r, g, b = int(color[0]), int(color[1]), int(color[2])
    font = pygame.font.Font(None, int(font_size))
    text_surface = font.render(text, True, (r, g, b))
    screen.blit(text_surface, (int(x), int(y)))


@opcode()
async def pygame_draw_rect(
    screen: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    color: list,
    filled: bool = True,
) -> None:
    """Draw a rectangle on the screen.

    Args:
        screen: The display surface
        x: X position (left edge)
        y: Y position (top edge)
        width: Rectangle width
        height: Rectangle height
        color: RGB color as [r, g, b]
        filled: If True, fill the rectangle; if False, draw outline only
    """
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    rect = pygame.Rect(int(x), int(y), int(width), int(height))

    if filled:
        pygame.draw.rect(screen, (r, g, b), rect)
    else:
        pygame.draw.rect(screen, (r, g, b), rect, 2)


@opcode()
async def pygame_draw_circle(
    screen: pygame.Surface, x: int, y: int, radius: int, color: list
) -> None:
    """Draw a filled circle on the screen.

    Args:
        screen: The display surface
        x: Center X position
        y: Center Y position
        radius: Circle radius
        color: RGB color as [r, g, b]
    """
    r, g, b = int(color[0]), int(color[1]), int(color[2])
    pygame.draw.circle(screen, (r, g, b), (int(x), int(y)), int(radius))


# ============================================================================
# Display & Timing
# ============================================================================

@opcode()
async def pygame_update_display() -> None:
    """Update the display to show all drawn elements."""
    pygame.display.flip()


@opcode()
async def pygame_delay(milliseconds: int) -> None:
    """Async delay in milliseconds.

    Use this to control frame rate in your game loop.
    Example: pygame_delay(16) for ~60 FPS
    """
    await asyncio.sleep(int(milliseconds) / 1000.0)


@opcode()
async def pygame_get_ticks() -> int:
    """Get the number of milliseconds since pygame.init() was called.

    Returns:
        Milliseconds elapsed since pygame initialization
    """
    return pygame.time.get_ticks()


# ============================================================================
# Math Helpers (for animations)
# ============================================================================

@opcode()
async def math_sin(angle: float) -> float:
    """Calculate sine of an angle (in radians).

    Args:
        angle: Angle in radians

    Returns:
        Sine value between -1 and 1
    """
    import math
    return math.sin(float(angle))


@opcode()
async def math_cos(angle: float) -> float:
    """Calculate cosine of an angle (in radians).

    Args:
        angle: Angle in radians

    Returns:
        Cosine value between -1 and 1
    """
    import math
    return math.cos(float(angle))


@opcode()
async def math_multiply(left: float, right: float) -> float:
    """Multiply two numbers.

    Args:
        left: First number
        right: Second number

    Returns:
        Product of left * right
    """
    return float(left) * float(right)


@opcode()
async def math_add(left: float, right: float) -> float:
    """Add two numbers (preserving floating point).

    Args:
        left: First number
        right: Second number

    Returns:
        Sum of left + right
    """
    return float(left) + float(right)


@opcode()
async def string_length(text: str) -> int:
    """Get the length of a string.

    Args:
        text: The string

    Returns:
        Length of the string
    """
    return len(str(text))


@opcode()
async def string_char_at(text: str, index: int) -> str:
    """Get character at specific index in string.

    Args:
        text: The string
        index: Index position (0-based)

    Returns:
        Character at that position
    """
    text_str = str(text)
    idx = int(index)
    if 0 <= idx < len(text_str):
        return text_str[idx]
    return ""


# ============================================================================
# Color & Math Helpers
# ============================================================================

@opcode()
async def pygame_create_color(r: int, g: int, b: int) -> list:
    """Create an RGB color list.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        List [r, g, b]
    """
    return [int(r), int(g), int(b)]


@opcode()
async def pygame_get_screen_width(screen: pygame.Surface) -> int:
    """Get the width of the screen."""
    return screen.get_width()


@opcode()
async def pygame_get_screen_height(screen: pygame.Surface) -> int:
    """Get the height of the screen."""
    return screen.get_height()


# ============================================================================
# Helper opcodes for game logic (list operations)
# ============================================================================

@opcode()
async def list_create_pair(x: int, y: int) -> list:
    """Create a list with two elements [x, y].

    Args:
        x: First element
        y: Second element

    Returns:
        List [x, y]
    """
    return [int(x), int(y)]


@opcode()
async def list_prepend(items: list, value) -> list:
    """Add value to the beginning of a list.

    Args:
        items: The list
        value: Value to prepend

    Returns:
        New list with value at the beginning
    """
    return [value] + list(items)


@opcode()
async def list_remove_last(items: list) -> list:
    """Remove the last element from a list.

    Args:
        items: The list

    Returns:
        New list without the last element
    """
    if len(items) == 0:
        return []
    return list(items)[:-1]


if __name__ == "__main__":
    print("✅ Pygame opcodes loaded!")
    print("\nAvailable opcodes:")
    print("\n  Initialization:")
    print("    • pygame_init()")
    print("    • pygame_create_window(width, height, title)")
    print("    • pygame_quit()")
    print("\n  Event Handling (for workflow loops):")
    print("    • pygame_should_quit() -> bool")
    print("    • pygame_process_events()")
    print("\n  Drawing:")
    print("    • pygame_fill_screen(screen, color)")
    print("    • pygame_draw_text(screen, text, x, y, font_size, color)")
    print("    • pygame_draw_rect(screen, x, y, width, height, color, filled)")
    print("    • pygame_draw_circle(screen, x, y, radius, color)")
    print("\n  Display & Timing:")
    print("    • pygame_update_display()")
    print("    • pygame_delay(milliseconds)")
    print("\n  Helpers:")
    print("    • pygame_create_color(r, g, b) -> list")
    print("    • pygame_get_screen_width(screen) -> int")
    print("    • pygame_get_screen_height(screen) -> int")
    print("\n💡 Game loops are controlled by LexFlow's control_while!")
