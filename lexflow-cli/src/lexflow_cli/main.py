import argparse
import asyncio
import json
import sys
import yaml
from pathlib import Path

from lexflow import Parser, Engine
from lexflow.visualizer import WorkflowVisualizer


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
  lexflow workflow.json --visualize                 # Show workflow visualization
  lexflow workflow.json --visualize --validate-only # Visualize without executing
  lexflow workflow.json --output-file output.txt    # Redirect output to file
  lexflow workflow.json --metrics                   # Show performance metrics
  lexflow workflow.json --metrics --metrics-json    # Export metrics as JSON
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Main workflow file (required)
    parser.add_argument(
        "workflow_file",
        help="Main workflow file to execute (JSON or YAML). The 'main' workflow from this file will be executed.",
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
    parser.add_argument(
        "--visualize",
        "--show-flow",
        action="store_true",
        help="Visualize workflow structure as ASCII art (can combine with --validate-only)",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        dest="output_file",
        metavar="FILE",
        help="Redirect workflow output to file instead of stdout",
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="inputs",
        action="append",
        metavar="KEY=VALUE",
        help="Input parameters for main workflow (can be used multiple times). Values are parsed as JSON when possible (e.g., --input age=30 --input enabled=true)",
    )

    # Metrics options
    parser.add_argument(
        "--metrics",
        "-m",
        action="store_true",
        help="Collect and display performance metrics after execution",
    )
    parser.add_argument(
        "--metrics-json",
        action="store_true",
        help="Export metrics as JSON (implicitly enables metrics). Output to stdout or --metrics-output file",
    )
    parser.add_argument(
        "--metrics-output",
        metavar="FILE",
        help="Output file for metrics (JSON or text report based on --metrics-json)",
    )
    parser.add_argument(
        "--metrics-top",
        type=int,
        default=10,
        metavar="N",
        help="Number of top operations to show in metrics report (default: 10)",
    )

    return parser


def _load_workflow_data(file_path: str) -> dict:
    """Load raw workflow data from YAML/JSON file.

    Args:
        file_path: Path to workflow file

    Returns:
        Raw workflow dictionary
    """
    path = Path(file_path)

    with open(file_path, "r") as f:
        # Detect file format by extension
        if path.suffix.lower() in [".yaml", ".yml"]:
            return yaml.safe_load(f)
        elif path.suffix.lower() == ".json":
            return json.load(f)
        else:
            # Try JSON first, fallback to YAML
            content = f.read()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return yaml.safe_load(content)


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
                print_info(
                    f"Including files: {', '.join(Path(f).name for f in include_files)}"
                )

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

        # Visualize workflow if requested
        if args.visualize:
            if args.verbose:
                print_info("Generating workflow visualization...")

            # Load raw workflow data for visualization
            workflow_data = _load_workflow_data(str(workflow_file))

            # If there are included files, merge their workflows
            if include_files:
                all_workflows = workflow_data.get("workflows", [])
                for include_file in include_files:
                    include_data = _load_workflow_data(include_file)
                    all_workflows.extend(include_data.get("workflows", []))
                workflow_data["workflows"] = all_workflows

            visualizer = WorkflowVisualizer()

            # Visualize all workflows in the program
            visualization = visualizer.visualize_program(workflow_data)
            print("\n" + visualization + "\n")

        if args.validate_only:
            print_success("Workflow is valid!")
            return

        # Parse input parameters
        inputs_dict = {}
        if args.inputs:
            for input_str in args.inputs:
                if "=" not in input_str:
                    print_error(
                        f"Invalid input format: {input_str}. Expected KEY=VALUE"
                    )
                    sys.exit(1)

                key, value = input_str.split("=", 1)

                # Try to parse value as JSON for automatic type conversion
                # This allows: age=30 -> int, enabled=true -> bool, tags='["a","b"]' -> list
                try:
                    inputs_dict[key] = json.loads(value)
                except json.JSONDecodeError:
                    # If JSON parsing fails, keep as string
                    inputs_dict[key] = value

            if args.verbose:
                print_info(f"Input parameters: {inputs_dict}")

        # Create and run engine
        if args.verbose:
            print_info("Starting execution...")

        # Handle output redirection
        output_file = None
        if args.output_file:
            if args.verbose:
                print_info(f"Redirecting output to: {args.output_file}")
            output_file = open(args.output_file, "w")

        try:
            # Create engine with optional metrics (enabled if --metrics or --metrics-json)
            enable_metrics = args.metrics or args.metrics_json
            engine = Engine(program, output=output_file, metrics=enable_metrics)
            result = await engine.run(inputs=inputs_dict if inputs_dict else None)

            if args.verbose:
                print_success("Execution completed")
                if result is not None:
                    print_info(f"Result: {result}")

            # Handle metrics output
            if enable_metrics:
                if args.metrics_json:
                    # Export as JSON
                    metrics_json = engine.metrics.to_json(indent=2)

                    if args.metrics_output:
                        with open(args.metrics_output, "w") as f:
                            f.write(metrics_json)
                        if args.verbose:
                            print_success(
                                f"Metrics JSON written to: {args.metrics_output}"
                            )
                    else:
                        # Print to stdout (stderr if output file is stdout)
                        target = sys.stderr if not args.output_file else sys.stdout
                        print("\n=== METRICS (JSON) ===", file=target)
                        print(metrics_json, file=target)
                else:
                    # Show formatted report
                    metrics_report = engine.get_metrics_report(top_n=args.metrics_top)

                    if args.metrics_output:
                        with open(args.metrics_output, "w") as f:
                            f.write(metrics_report)
                        if args.verbose:
                            print_success(
                                f"Metrics report written to: {args.metrics_output}"
                            )
                    else:
                        # Print to stdout (stderr if output file is stdout)
                        target = sys.stderr if not args.output_file else sys.stdout
                        print(file=target)
                        print(metrics_report, file=target)
                        print(file=target)
                        print(f"Summary: {engine.get_metrics_summary()}", file=target)

        finally:
            if output_file:
                output_file.close()
                if args.verbose:
                    print_success(f"Output written to: {args.output_file}")

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
