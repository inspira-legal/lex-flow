"""Pygame opcodes for LexFlow - Visual workflow examples.
Installation:
    pip install lexflow[pygame]
    or:
    pip install pygame
"""

import asyncio
import os
from typing import Any
from .opcodes import opcode

# Suppress pygame welcome message
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def _check_availability():
    """Check if pygame is available and raise helpful error if not."""
    if not PYGAME_AVAILABLE:
        raise ImportError(
            "pygame is not installed. Install it with:\n"
            "  pip install lexflow[pygame]\n"
            "or:\n"
            "  pip install pygame"
        )


def register_pygame_opcodes():
    if not PYGAME_AVAILABLE:
        return

    # ============================================================================
    # Pygame Initialization & Window Management
    # ============================================================================

    @opcode()
    async def pygame_init() -> None:
        """Initialize pygame engine."""
        _check_availability()
        pygame.init()

    @opcode()
    async def pygame_create_window(
        width: int, height: int, title: str = "LexFlow + Pygame"
    ) -> Any:
        """Create a pygame window and return the display surface.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title

        Returns:
            pygame.Surface object representing the display
        """
        _check_availability()
        screen = pygame.display.set_mode((int(width), int(height)))
        pygame.display.set_caption(title)
        return screen

    @opcode()
    async def pygame_quit() -> None:
        """Quit pygame and close all windows."""
        _check_availability()
        pygame.quit()

    # ============================================================================
    # Event Handling (for workflow-controlled loops)
    # ============================================================================

    @opcode()
    async def pygame_should_quit() -> bool:
        """Check if user wants to quit (clicked X button).

        Returns:
            True if quit event detected, False otherwise.

        Note:
            Use this in control_while conditions for game loops.
        """
        _check_availability()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    @opcode()
    async def pygame_process_events() -> None:
        """Process pygame events (keeps window responsive).

        Call this in your game loop to prevent window freezing.
        """
        _check_availability()
        pygame.event.pump()

    @opcode()
    async def pygame_get_key_pressed(key_name: str) -> bool:
        """Check if a specific key is currently pressed.

        Args:
            key_name: Key name (e.g., "up", "down", "left", "right", "space", "w", "a", "s", "d")

        Returns:
            True if key is pressed, False otherwise
        """
        _check_availability()
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
    async def pygame_fill_screen(screen: Any, color: list) -> None:
        """Fill the entire screen with a color.

        Args:
            screen: The display surface
            color: RGB color as [r, g, b] where each value is 0-255
        """
        _check_availability()
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        screen.fill((r, g, b))

    @opcode()
    async def pygame_draw_text(
        screen: Any,
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
            font_size: Font size in pixels (default: 48)
            color: RGB color as [r, g, b], defaults to white [255, 255, 255]
        """
        _check_availability()
        if color is None:
            color = [255, 255, 255]

        r, g, b = int(color[0]), int(color[1]), int(color[2])
        font = pygame.font.Font(None, int(font_size))
        text_surface = font.render(text, True, (r, g, b))
        screen.blit(text_surface, (int(x), int(y)))

    @opcode()
    async def pygame_draw_rect(
        screen: Any,
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
            filled: If True, fill the rectangle; if False, draw outline only (default: True)
        """
        _check_availability()
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        rect = pygame.Rect(int(x), int(y), int(width), int(height))

        if filled:
            pygame.draw.rect(screen, (r, g, b), rect)
        else:
            pygame.draw.rect(screen, (r, g, b), rect, 2)

    @opcode()
    async def pygame_draw_circle(
        screen: Any, x: int, y: int, radius: int, color: list
    ) -> None:
        """Draw a filled circle on the screen.

        Args:
            screen: The display surface
            x: Center X position
            y: Center Y position
            radius: Circle radius
            color: RGB color as [r, g, b]
        """
        _check_availability()
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        pygame.draw.circle(screen, (r, g, b), (int(x), int(y)), int(radius))

    # ============================================================================
    # Display & Timing
    # ============================================================================

    @opcode()
    async def pygame_update_display() -> None:
        """Update the display to show all drawn elements."""
        _check_availability()
        pygame.display.flip()

    @opcode()
    async def pygame_delay(milliseconds: int) -> None:
        """Async delay in milliseconds.

        Use this to control frame rate in your game loop.
        Example: pygame_delay(16) for ~60 FPS

        Args:
            milliseconds: Delay duration in milliseconds
        """
        await asyncio.sleep(int(milliseconds) / 1000.0)

    @opcode()
    async def pygame_get_ticks() -> int:
        """Get the number of milliseconds since pygame.init() was called.

        Returns:
            Milliseconds elapsed since pygame initialization
        """
        _check_availability()
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
            Character at that position, or empty string if index out of bounds
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
    async def pygame_get_screen_width(screen: Any) -> int:
        """Get the width of the screen.

        Args:
            screen: The display surface

        Returns:
            Width in pixels
        """
        _check_availability()
        return screen.get_width()

    @opcode()
    async def pygame_get_screen_height(screen: Any) -> int:
        """Get the height of the screen.

        Args:
            screen: The display surface

        Returns:
            Height in pixels
        """
        _check_availability()
        return screen.get_height()
