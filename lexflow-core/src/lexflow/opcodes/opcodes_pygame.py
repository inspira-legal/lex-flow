"""Pygame opcodes for LexFlow - Visual workflow examples.

Installation:
    pip install lexflow[pygame]
"""

import asyncio
import os
from typing import Any

from .opcodes import opcode, register_category

# Suppress pygame welcome message
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


def register_pygame_opcodes():
    """Register pygame opcodes to the default registry."""
    if not PYGAME_AVAILABLE:
        return

    register_category(
        id="pygame",
        label="Pygame Operations",
        prefix="pygame_",
        color="#00D86A",
        icon="🎮",
        requires="pygame",
        order=220,
    )

    # =========================================================================
    # Pygame Initialization & Window Management
    # =========================================================================

    @opcode(category="pygame")
    async def pygame_init() -> None:
        """Initialize pygame engine."""
        pygame.init()

    @opcode(category="pygame")
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
        screen = pygame.display.set_mode((int(width), int(height)))
        pygame.display.set_caption(title)
        return screen

    @opcode(category="pygame")
    async def pygame_quit() -> None:
        """Quit pygame and close all windows."""
        pygame.quit()

    # =========================================================================
    # Event Handling
    # =========================================================================

    @opcode(category="pygame")
    async def pygame_should_quit() -> bool:
        """Check if user wants to quit (clicked X button).

        Returns:
            True if quit event detected, False otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    @opcode(category="pygame")
    async def pygame_process_events() -> None:
        """Process pygame events (keeps window responsive)."""
        pygame.event.pump()

    @opcode(category="pygame")
    async def pygame_get_key_pressed(key_name: str) -> bool:
        """Check if a specific key is currently pressed.

        Args:
            key_name: Key name (e.g., "up", "down", "left", "right", "space")

        Returns:
            True if key is pressed, False otherwise
        """
        keys = pygame.key.get_pressed()
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

    # =========================================================================
    # Drawing Operations
    # =========================================================================

    @opcode(category="pygame")
    async def pygame_fill_screen(screen: Any, color: list) -> None:
        """Fill the entire screen with a color.

        Args:
            screen: The display surface
            color: RGB color as [r, g, b] where each value is 0-255
        """
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        screen.fill((r, g, b))

    @opcode(category="pygame")
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
            color: RGB color as [r, g, b], defaults to white
        """
        if color is None:
            color = [255, 255, 255]
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        font = pygame.font.Font(None, int(font_size))
        text_surface = font.render(text, True, (r, g, b))
        screen.blit(text_surface, (int(x), int(y)))

    @opcode(category="pygame")
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
            filled: If True, fill; if False, draw outline only
        """
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        rect = pygame.Rect(int(x), int(y), int(width), int(height))
        if filled:
            pygame.draw.rect(screen, (r, g, b), rect)
        else:
            pygame.draw.rect(screen, (r, g, b), rect, 2)

    @opcode(category="pygame")
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
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        pygame.draw.circle(screen, (r, g, b), (int(x), int(y)), int(radius))

    # =========================================================================
    # Display & Timing
    # =========================================================================

    @opcode(category="pygame")
    async def pygame_update_display() -> None:
        """Update the display to show all drawn elements."""
        pygame.display.flip()

    @opcode(category="pygame")
    async def pygame_delay(milliseconds: int) -> None:
        """Async delay in milliseconds.

        Args:
            milliseconds: Delay duration in milliseconds
        """
        await asyncio.sleep(int(milliseconds) / 1000.0)

    @opcode(category="pygame")
    async def pygame_get_ticks() -> int:
        """Get milliseconds since pygame.init() was called.

        Returns:
            Milliseconds elapsed since pygame initialization
        """
        return pygame.time.get_ticks()

    # =========================================================================
    # Color & Screen Helpers
    # =========================================================================

    @opcode(category="pygame")
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

    @opcode(category="pygame")
    async def pygame_get_screen_width(screen: Any) -> int:
        """Get the width of the screen.

        Args:
            screen: The display surface

        Returns:
            Width in pixels
        """
        return screen.get_width()

    @opcode(category="pygame")
    async def pygame_get_screen_height(screen: Any) -> int:
        """Get the height of the screen.

        Args:
            screen: The display surface

        Returns:
            Height in pixels
        """
        return screen.get_height()
