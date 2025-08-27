#!/usr/bin/env python3

import json
import os
import sys
from io import StringIO
from contextlib import redirect_stdout

from core.models import Program as OldProgram
from core.parser import Parser
from core.engine import Engine


def run_test(test_file: str) -> dict:
    """Run a single test file and capture results."""
    test_name = os.path.basename(test_file).replace('.json', '')
    
    try:
        # Load and parse
        with open(test_file) as f:
            data = json.load(f)
        
        old_program = OldProgram.model_validate(data)
        workflow = old_program.workflows[0]
        
        parser = Parser(workflow)
        program = parser.parse()
        
        # Capture output
        output = StringIO()
        engine = Engine(program)
        
        with redirect_stdout(output):
            step_count = 0
            while engine.step() and step_count < 50:  # Safety limit
                step_count += 1
        
        result = {
            'name': test_name,
            'status': 'PASS',
            'steps': step_count,
            'output': output.getvalue(),
            'final_state': str(engine._state),
            'error': None
        }
        
    except Exception as e:
        result = {
            'name': test_name,
            'status': 'FAIL',
            'steps': 0,
            'output': '',
            'final_state': '',
            'error': str(e)
        }
    
    return result


def run_all_tests():
    """Run all tests in the tests/ directory."""
    tests_dir = 'tests'
    
    if not os.path.exists(tests_dir):
        print(f"Tests directory '{tests_dir}' not found!")
        return
    
    test_files = [f for f in os.listdir(tests_dir) if f.endswith('.json') and f not in ['expected_outputs.json', 'guessing_game.json']]
    
    if not test_files:
        print(f"No JSON test files found in '{tests_dir}'!")
        return
    
    print(f"Running {len(test_files)} tests...\n")
    
    results = []
    passed = 0
    failed = 0
    
    for test_file in sorted(test_files):
        test_path = os.path.join(tests_dir, test_file)
        result = run_test(test_path)
        results.append(result)
        
        status_icon = "✅" if result['status'] == 'PASS' else "❌"
        print(f"{status_icon} {result['name']:<20} - {result['status']} ({result['steps']} steps)")
        
        if result['status'] == 'PASS':
            passed += 1
        else:
            failed += 1
            print(f"   Error: {result['error']}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} PASSED, {failed} FAILED")
    
    # Show detailed results
    print(f"\n{'='*50}")
    print("DETAILED OUTPUT:")
    print(f"{'='*50}")
    
    for result in results:
        print(f"\n--- {result['name']} ---")
        if result['output']:
            print("Output:")
            print(result['output'])
        if result['error']:
            print(f"Error: {result['error']}")
        print(f"Final State: {result['final_state']}")
    
    return passed, failed


if __name__ == "__main__":
    run_all_tests()