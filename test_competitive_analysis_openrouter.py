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
    
    inputs = {
        "company_name": "Anthropic",
        "competitor_name": "OpenAI",
        "api_key": os.environ.get("OPENROUTER_API_KEY", "your-openrouter-key")
    }

    # Handle placeholder API key
    if inputs["api_key"] == "your-openrouter-key":
        print("\n⚠️  Note: Using placeholder API key. Skipping execution to avoid expected error.")
        print("To run this test properly, replace the placeholder in this file or set an environment variable.")
        return {"final_report": "[Mocked] Proper API key required for actual run."}

    result = await engine.run(inputs=inputs)

    print("\n✅ Workflow completed!")
    
    # Assertions
    assert result is not None, "Workflow should return a result"
    assert "final_report" in result, "Result should contain 'final_report'"
    assert len(result["final_report"]) > 0, "'final_report' should not be empty"
    
    print("✓ All assertions passed!")
    return result


if __name__ == "__main__":
    asyncio.run(main())
