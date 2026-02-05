#!/usr/bin/env python3
"""
LexFlow Competitive Analysis Runner

Execute competitive intelligence workflows via command line with custom inputs.

Usage:
    python3 run_competitive_analysis.py --company "Tesla" --competitor "BYD"
    python3 run_competitive_analysis.py -c "Nubank" -x "Banco Inter" --api-key "your-key"

Examples:
    # Using default API key from workflow
    python3 run_competitive_analysis.py --company "Anthropic" --competitor "OpenAI"

    # Using custom API key
    python3 run_competitive_analysis.py -c "SpaceX" -x "Blue Origin" -k "sk-or-v1-..."

    # Using custom models
    python3 run_competitive_analysis.py -c "Tesla" -x "BYD" --research-model "deepseek/deepseek-v3.2-20251201"
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional

# Add lexflow to path
sys.path.insert(0, str(Path(__file__).parent / "lexflow-core" / "src"))

from lexflow import Parser, Engine


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Execute competitive analysis using LexFlow and OpenRouter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument(
        "-c", "--company",
        required=True,
        type=str,
        help="Your company name (the company you're analyzing for)"
    )

    parser.add_argument(
        "-x", "--competitor",
        required=True,
        type=str,
        help="Competitor name (the company to research)"
    )

    # Optional arguments
    parser.add_argument(
        "-k", "--api-key",
        type=str,
        default=None,
        help="OpenRouter API key (if not using default from workflow)"
    )

    parser.add_argument(
        "--research-model",
        type=str,
        default=None,
        help="Custom research model (e.g., 'google/gemini-2.5-flash')"
    )

    parser.add_argument(
        "--formatter-model",
        type=str,
        default=None,
        help="Custom formatter model (e.g., 'google/gemini-2.5-flash-lite')"
    )

    parser.add_argument(
        "-w", "--workflow",
        type=str,
        default="examples/integrations/competitive_analysis_openrouter.yaml",
        help="Path to workflow file (default: competitive_analysis_openrouter.yaml)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> None:
    """Validate input arguments."""
    if not args.company.strip():
        raise ValueError("Company name cannot be empty")

    if not args.competitor.strip():
        raise ValueError("Competitor name cannot be empty")

    if args.company.lower() == args.competitor.lower():
        print("⚠️  Warning: Company and competitor have the same name")


async def run_analysis(
    workflow_path: Path,
    company_name: str,
    competitor_name: str,
    api_key: Optional[str] = None,
    research_model: Optional[str] = None,
    formatter_model: Optional[str] = None,
    verbose: bool = False
) -> dict:
    """
    Execute competitive analysis workflow.

    Args:
        workflow_path: Path to the LexFlow workflow YAML file
        company_name: Name of the company being analyzed for
        competitor_name: Name of the competitor to research
        api_key: Optional OpenRouter API key override
        research_model: Optional research model override
        formatter_model: Optional formatter model override
        verbose: Enable verbose output
    """
    # Validate workflow file exists
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    if verbose:
        print(f"📁 Loading workflow: {workflow_path}")

    # Parse workflow
    parser = Parser()
    program = parser.parse_file(str(workflow_path))

    if verbose:
        print("✓ Workflow parsed successfully")
        print(f"📊 Company: {company_name}")
        print(f"🎯 Competitor: {competitor_name}")
        print()

    # Build inputs dictionary
    inputs = {
        "company_name": company_name,
        "competitor_name": competitor_name
    }

    # Add optional overrides
    if api_key:
        inputs["api_key"] = api_key
        if verbose:
            print("🔑 Using custom API key")

    if research_model:
        inputs["research_model"] = research_model
        if verbose:
            print(f"🤖 Research model: {research_model}")

    if formatter_model:
        inputs["formatter_model"] = formatter_model
        if verbose:
            print(f"✨ Formatter model: {formatter_model}")

    if verbose:
        print("\n" + "="*60)
        print("Starting Analysis...")
        print("="*60 + "\n")

    # Execute workflow
    engine = Engine(program)
    result = await engine.run(inputs=inputs)

    if verbose:
        print("\n" + "="*60)
        print("Analysis Complete!")
        print("="*60)

    return result


async def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Validate inputs
        validate_inputs(args)

        # Resolve workflow path
        workflow_path = Path(__file__).parent / args.workflow

        # Run analysis
        await run_analysis(
            workflow_path=workflow_path,
            company_name=args.company,
            competitor_name=args.competitor,
            api_key=args.api_key,
            research_model=args.research_model,
            formatter_model=args.formatter_model,
            verbose=args.verbose
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if locals().get('args') and getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
