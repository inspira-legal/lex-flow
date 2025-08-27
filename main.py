import json
import argparse
from core.models import Program as OldProgram
from core.parser import Parser
from core.engine import Engine


def load_workflow(path: str) -> dict:
    try:
        with open(path) as file:
            json_data = json.load(file)
    except FileNotFoundError:
        json_data = {}
        print(f"Invalid file path: {path}")
    except json.JSONDecodeError as e:
        json_data = {}
        print(f"Failed to load json file: {e}")

    return json_data


def main():
    parser = argparse.ArgumentParser(description="Lex Flow Interpreter.")
    parser.add_argument("-f", "--file", help="Workflow file path")
    parser.add_argument("--debug", action="store_true", help="Enable step-by-step debugging")

    args = parser.parse_args()

    if args.file:
        json_data = load_workflow(args.file)

    if json_data:
        old_program = OldProgram.model_validate(json_data)
        workflow = old_program.workflows[0]
        functions_data = json_data.get("functions", {})
        
        parser = Parser(workflow, functions_data)
        program = parser.parse()

    engine = Engine(program)

    if args.debug:
        condition = True
        counter = 0
        while condition:
            engine.step()
            condition = "y" == input(f"Step [{counter}], continue? ")
            if engine._state.is_finished():
                break
            print(f"Next PC: {engine._state._pc}")
            counter += 1
    else:
        while not engine._state.is_finished():
            engine.step()


if __name__ == "__main__":
    main()
