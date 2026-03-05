#!/usr/bin/env python3
"""
LexFlow Competitive Intelligence Monitor

Real-time competitive monitoring with Perplexity (search) + OpenRouter (formatting).

Usage:
    python3 run_competitive_monitor.py --company "Jusbrasil" --competitor "Inspira"
    python3 run_competitive_monitor.py -c "Tesla" -x "BYD" --verbose

Features:
    ✅ Real-time web search (last 30 days)
    ✅ Social media mentions (Twitter, LinkedIn)
    ✅ Recent hires and job postings
    ✅ News and press releases
    ✅ Funding announcements
    ✅ Product launches

Examples:
    # Basic usage with default API keys
    python3 run_competitive_monitor.py --company "Nubank" --competitor "Inter"

    # With custom API keys
    python3 run_competitive_monitor.py -c "Tesla" -x "BYD" \
        --perplexity-key "pplx-..." \
        --openrouter-key "sk-or-v1-..."

    # Verbose mode
    python3 run_competitive_monitor.py -c "Anthropic" -x "OpenAI" -v
"""

import sys
import argparse
import asyncio
import os
from pathlib import Path
from typing import Optional, Any

# Add lexflow to path
sys.path.insert(0, str(Path(__file__).parent / "lexflow-core" / "src"))

from lexflow import Parser, Engine


# Default API keys (to be provided via command line or environment)
DEFAULT_PERPLEXITY_KEY = os.environ.get("PERPLEXITY_API_KEY")
DEFAULT_OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Real-time competitive intelligence monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument(
        "-c", "--company",
        required=True,
        type=str,
        help="Your company name"
    )

    parser.add_argument(
        "-x", "--competitor",
        required=True,
        type=str,
        help="Competitor to monitor"
    )

    # Optional API keys
    parser.add_argument(
        "--perplexity-key",
        type=str,
        default=DEFAULT_PERPLEXITY_KEY,
        help="Perplexity API key (for real-time search)"
    )

    parser.add_argument(
        "--openrouter-key",
        type=str,
        default=DEFAULT_OPENROUTER_KEY,
        help="OpenRouter API key (for formatting)"
    )

    # Optional settings
    parser.add_argument(
        "--perplexity-model",
        type=str,
        default="sonar",
        choices=["sonar", "sonar-pro"],
        help="Perplexity model to use"
    )

    parser.add_argument(
        "--openrouter-model",
        type=str,
        default="google/gemini-2.5-flash-lite",
        help="OpenRouter model for formatting"
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

    # Only validate if not using command-line/environment overrides
    if args.perplexity_key and not args.perplexity_key.startswith("pplx-"):
        raise ValueError("Invalid Perplexity API key format (should start with 'pplx-')")

    if args.openrouter_key and not args.openrouter_key.startswith("sk-or-"):
        raise ValueError("Invalid OpenRouter API key format (should start with 'sk-or-')")

    if not args.perplexity_key:
        print("⚠️  Warning: Perplexity API key not provided. Search steps may fail.")

    if not args.openrouter_key:
        print("⚠️  Warning: OpenRouter API key not provided. Formatting steps may fail.")


async def run_monitoring(
    company_name: str,
    competitor_name: str,
    perplexity_key: Optional[str],
    openrouter_key: Optional[str],
    perplexity_model: str = "sonar",
    openrouter_model: str = "google/gemini-2.5-flash-lite",
    verbose: bool = False
) -> Any:
    """
    Execute real-time competitive monitoring.

    Args:
        company_name: Your company name
        competitor_name: Competitor to monitor
        perplexity_key: Perplexity API key (for real-time search)
        openrouter_key: OpenRouter API key (for formatting)
        perplexity_model: Perplexity model to use
        openrouter_model: OpenRouter model for formatting
        verbose: Enable verbose output
    """
    workflow_path = Path(__file__).parent / "examples" / "integrations" / "competitive_analysis_hybrid.yaml"

    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    if verbose:
        print("="*60)
        print("🔍 Real-Time Competitive Intelligence Monitor")
        print("="*60)
        print(f"📁 Workflow: {workflow_path}")
        print(f"📊 Company: {company_name}")
        print(f"🎯 Competitor: {competitor_name}")
        print(f"🔍 Search Engine: Perplexity ({perplexity_model})")
        print(f"✨ Formatter: OpenRouter ({openrouter_model})")
        print("="*60 + "\n")

    # Parse workflow
    parser = Parser()
    program = parser.parse_file(str(workflow_path))

    if verbose:
        print("✓ Workflow loaded successfully\n")

    # Build inputs
    inputs = {
        "company_name": company_name,
        "competitor_name": competitor_name,
        "perplexity_api_key": perplexity_key,
        "openrouter_api_key": openrouter_key,
    }

    # Add model overrides if different from defaults
    if perplexity_model != "sonar":
        inputs["perplexity_model"] = perplexity_model

    if openrouter_model != "google/gemini-2.5-flash-lite":
        inputs["openrouter_model"] = openrouter_model

    # Execute workflow
    engine = Engine(program)
    result = await engine.run(inputs=inputs)

    if verbose:
        print("\n" + "="*60)
        print("✅ Monitoring complete")
        print("="*60)

    return result


async def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Validate inputs
        validate_inputs(args)

        # Run monitoring
        await run_monitoring(
            company_name=args.company,
            competitor_name=args.competitor,
            perplexity_key=args.perplexity_key,
            openrouter_key=args.openrouter_key,
            perplexity_model=args.perplexity_model,
            openrouter_model=args.openrouter_model,
            verbose=args.verbose
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if locals().get('args') and getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
