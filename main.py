import json
import argparse
from core.models import Program
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

    args = parser.parse_args()

    if args.file:
        json_data = load_workflow(args.file)

    if json_data:
        program: Program = Program.model_validate(json_data)

    engine = Engine(program.workflows[0])

    condition = True
    counter = 0
    while condition:
        engine.step()
        condition = "y" == input(f"Step [{counter}], continue? ")
        if engine._state._pc is None:
            break
        print(f"Next node: {engine._state._pc}")
        counter += 1


if __name__ == "__main__":
    main()
