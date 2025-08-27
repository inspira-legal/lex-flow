#!/usr/bin/env python3

import json
from run_tests import run_test
import os


def validate_all_tests():
    """Validate that test outputs match expected outputs."""
    
    # Load expected outputs
    with open('tests/expected_outputs.json') as f:
        expected = json.load(f)
    
    tests_dir = 'tests'
    test_files = [f for f in os.listdir(tests_dir) if f.endswith('.json') and f != 'expected_outputs.json']
    
    print(f"Validating {len(test_files)} tests against expected outputs...\n")
    
    all_passed = True
    
    for test_file in sorted(test_files):
        test_name = test_file.replace('.json', '')
        test_path = os.path.join(tests_dir, test_file)
        
        if test_name not in expected:
            print(f"⚠️  {test_name:<20} - No expected output defined")
            continue
            
        result = run_test(test_path)
        expected_output = expected[test_name]
        actual_output = result['output']
        
        if result['status'] != 'PASS':
            print(f"❌ {test_name:<20} - Test failed: {result['error']}")
            all_passed = False
        elif actual_output == expected_output:
            print(f"✅ {test_name:<20} - Output matches expected")
        else:
            print(f"❌ {test_name:<20} - Output mismatch")
            print(f"   Expected: {repr(expected_output)}")
            print(f"   Actual:   {repr(actual_output)}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All tests PASSED! Core functionality validated.")
    else:
        print("❌ Some tests FAILED. Check output above.")
    
    return all_passed


if __name__ == "__main__":
    validate_all_tests()