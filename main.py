import argparse
import asyncio
import sys
from pathlib import Path
from typing import List

from core.loader import WorkflowLoader
from core.parser import Parser
from core.engine import Engine
from core.errors import (
    LexFlowError,
    ErrorReporter,
)


def create_parser() -> argparse.ArgumentParser:
    """Create enhanced argument parser"""
    parser = argparse.ArgumentParser(
        description="Lex Flow - Visual Programming Workflow Interpreter",
        epilog="""
Examples:
  python main.py workflow.json                           # Run single workflow
  python main.py main.json -I utils.json helpers.json   # Import additional workflows
  python main.py main.json --workflow greeting -I utils.json  # Run specific workflow
  python main.py workflow.json --import-dir modules/     # Import from directory
  python main.py --debug workflow.json                   # Step-by-step debugging
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Main workflow file (required)
    parser.add_argument("main_file", help="Main workflow file to execute")

    # Import options
    parser.add_argument(
        "-I",
        "--import",
        dest="import_files",
        nargs="*",
        default=[],
        help="Additional workflow files to import",
    )
    parser.add_argument(
        "--import-dir", type=str, help="Directory containing workflow files to import"
    )

    # Execution options
    parser.add_argument(
        "--workflow",
        type=str,
        help="Name of specific workflow to execute (default: 'main' or single workflow)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable step-by-step debugging"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with execution details",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate workflows without executing",
    )

    return parser


def print_success(message: str):
    """Print success message"""
    print(f"[SUCCESS] {message}")


def print_info(message: str):
    """Print info message"""
    print(f"[INFO] {message}")


def print_error(error: Exception, suggestions: List[str] = None):
    """Print formatted error with suggestions"""
    print(ErrorReporter.format_error_report(error, suggestions))


async def run_workflow(engine: Engine, debug: bool = False, verbose: bool = False):
    """Execute workflow with optional debugging"""
    if debug:
        step_count = 0
        print_info("Debug mode enabled. Press Enter to step, 'q' to quit.")

        while not engine._state.is_finished():
            if verbose:
                print(f"Step {step_count}: {engine._state}")

            await engine.step()

            user_input = (
                input(f"Step [{step_count}] completed. Continue? (Enter/q): ")
                .strip()
                .lower()
            )
            if user_input == "q":
                print_info("Execution terminated by user")
                break

            step_count += 1

        if engine._state.is_finished():
            print_success(f"Workflow completed in {step_count} steps")

    else:
        step_count = 0
        while not engine._state.is_finished():
            await engine.step()
            step_count += 1

        if verbose:
            print_success(f"Workflow completed in {step_count} steps")


async def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        loader = WorkflowLoader()

        import_files = list(args.import_files) if args.import_files else []

        if args.import_dir:
            print_info(f"Loading import workflows from directory: {args.import_dir}")
            import_dir = Path(args.import_dir)
            if import_dir.exists() and import_dir.is_dir():
                json_files = list(import_dir.glob("*.json"))
                import_files.extend([str(f) for f in json_files])

        if import_files:
            print_info(f"Loading main file: {Path(args.main_file).name}")
            print_info(f"Loading {len(import_files)} import file(s)")
        else:
            print_info(f"Loading workflow file: {Path(args.main_file).name}")

        all_workflows = loader.load_files_with_main(args.main_file, import_files)

        if args.verbose:
            main_workflows = []
            import_workflows_list = []

            for name, workflow in all_workflows.items():
                source_file = Path(loader.file_sources[name]).name
                interface = workflow.interface
                inputs = (
                    f"({', '.join(interface.inputs)})" if interface.inputs else "()"
                )
                outputs = (
                    f" -> ({', '.join(interface.outputs)})" if interface.outputs else ""
                )

                workflow_info = f"  {name}{inputs}{outputs} from {source_file}"
                if source_file == Path(args.main_file).name:
                    main_workflows.append(workflow_info)
                else:
                    import_workflows_list.append(workflow_info)

            if main_workflows:
                print_info("Main file workflows:")
                for info in main_workflows:
                    print(info)

            if import_workflows_list:
                print_info("Imported workflows:")
                for info in import_workflows_list:
                    print(info)

        print_success(f"Loaded {len(all_workflows)} workflow(s)")

        main_workflow_name = loader.get_main_workflow_from_file(
            args.main_file, args.workflow
        )
        main_workflow = all_workflows[main_workflow_name]

        print_info(f"Executing workflow: {main_workflow_name}")

        if args.validate_only:
            print_success("All workflows are valid!")
            return

        parser_obj = Parser(main_workflow, list(all_workflows.values()))
        program = parser_obj.parse()

        engine = Engine(program)
        print_info("Starting execution...")

        await run_workflow(engine, args.debug, args.verbose)

    except KeyboardInterrupt:
        print_info("\nExecution interrupted by user")
        sys.exit(1)

    except LexFlowError as e:
        print_error(e)
        sys.exit(1)

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
