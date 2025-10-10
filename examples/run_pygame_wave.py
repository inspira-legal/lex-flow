#!/usr/bin/env python3
"""Run the pygame wave animation workflow example."""

import asyncio
import sys
from pathlib import Path

# Add lexflow to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lexflow-core" / "src"))

# Import pygame opcodes (this registers them globally)
import example_pygame_opcodes  # noqa: F401

from lexflow import Parser, Engine


async def main():
    """Run the pygame wave animation workflow."""
    workflow_path = Path(__file__).parent / "example_pygame_wave.yaml"

    print("=" * 60)
    print("LexFlow + Pygame - Wave Animation Demo")
    print("=" * 60)
    print(f"\nLoading workflow: {workflow_path}")

    # Parse workflow
    parser = Parser()
    program = parser.parse_file(str(workflow_path))

    print("✓ Workflow parsed successfully")
    print("\nStarting wave animation...")
    print("(Close the window to exit)\n")

    # Run workflow
    engine = Engine(program)
    result = await engine.run()

    print("\n✅ Animation completed!")
    return result


if __name__ == "__main__":
    asyncio.run(main())
