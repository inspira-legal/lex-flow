import argparse
import asyncio
import sys
from pathlib import Path

from lexflow import Parser, Engine


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="Lex Flow - Visual Programming Workflow Interpreter",
        epilog="""
Examples:
  lexflow workflow.json                             # Run workflow
  lexflow workflow.yaml                             # Run YAML workflow
  lexflow main.yaml --include helpers.yaml          # Include external workflows
  lexflow main.json --include util.json lib.yaml    # Include multiple files (JSON/YAML)
  lexflow workflow.json --verbose                   # Verbose output
  lexflow workflow.json --validate-only             # Validate without executing
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Main workflow file (required)
    parser.add_argument(
        "workflow_file",
        help="Main workflow file to execute (JSON or YAML). The 'main' workflow from this file will be executed."
    )

    # Import options
    parser.add_argument(
        "--include",
        dest="include_files",
        nargs="+",
        metavar="FILE",
        help="Include additional workflow files. All workflows (including 'main' if present) become callable external workflows.",
    )

    # Execution options
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with execution details",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate workflow without executing",
    )

    return parser


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_info(message: str):
    """Print info message"""
    print(f"→ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"✗ {message}", file=sys.stderr)


async def main():
    arg_parser = create_parser()
    args = arg_parser.parse_args()

    try:
        workflow_file = Path(args.workflow_file)

        # Check if main file exists
        if not workflow_file.exists():
            print_error(f"File not found: {workflow_file}")
            sys.exit(1)

        # Check if included files exist
        include_files = args.include_files or []
        for include_file in include_files:
            if not Path(include_file).exists():
                print_error(f"Included file not found: {include_file}")
                sys.exit(1)

        if args.verbose:
            print_info(f"Loading workflow: {workflow_file.name}")
            if include_files:
                print_info(f"Including files: {', '.join(Path(f).name for f in include_files)}")

        # Parse the workflow(s)
        parser = Parser()
        if include_files:
            program = parser.parse_files(str(workflow_file), include_files)
        else:
            program = parser.parse_file(str(workflow_file))

        if args.verbose:
            print_success("Workflow parsed successfully")
            print_info(f"Main workflow: {program.main.name}")
            if program.externals:
                print_info(f"External workflows: {', '.join(program.externals.keys())}")

        if args.validate_only:
            print_success("Workflow is valid!")
            return

        # Create and run engine
        if args.verbose:
            print_info("Starting execution...")

        engine = Engine(program)
        result = await engine.run()

        if args.verbose:
            print_success("Execution completed")
            if result is not None:
                print_info(f"Result: {result}")

    except KeyboardInterrupt:
        print_info("\nExecution interrupted by user")
        sys.exit(1)

    except Exception as e:
        print_error(f"Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def cli_main():
    """Entry point for CLI script"""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
