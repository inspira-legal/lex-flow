#!/usr/bin/env python3
"""Test the competitive analysis workflow with OpenRouter."""

import asyncio
import sys
from pathlib import Path

# Add lexflow to path
sys.path.insert(0, str(Path(__file__).parent / "lexflow-core" / "src"))

from lexflow import Parser, Engine


async def main():
    """Run the competitive analysis workflow."""
    workflow_path = Path(__file__).parent / "examples" / "integrations" / "competitive_analysis_openrouter.yaml"

    print("=" * 60)
    print("Testing Competitive Analysis with OpenRouter")
    print("=" * 60)
    print(f"\nLoading workflow: {workflow_path}")

    # Parse workflow
    parser = Parser()
    program = parser.parse_file(str(workflow_path))

    print("✓ Workflow parsed successfully")
    print("\nRunning workflow...\n")

    # Run workflow with inputs
    engine = Engine(program)
    result = await engine.run(
        inputs={
            "company_name": "Anthropic",
            "competitor_name": "OpenAI",
            "api_key": "your-openrouter-key"
        }
    )

    print("\n✅ Workflow completed!")
    return result


if __name__ == "__main__":
    asyncio.run(main())
