#!/usr/bin/env python3
"""Simple test script for JSON parser robustness."""

from resync.core.utils.json_parser import parse_llm_json_response

# Test cases
test_cases = [
    ('{"is_incorrect": false, "confidence": 0.95, "reason": "Response is accurate"}', None),
    ('```json\n{"is_incorrect": true, "confidence": 0.85, "reason": "Bad advice"}\n```', None),
    ('Here is the analysis:\n{"is_incorrect": false, "confidence": 0.80, "reason": "Good response"}', None),
]

print('Testing JSON parser robustness...')
for i, (response, required_keys) in enumerate(test_cases):
    try:
        result = parse_llm_json_response(response, required_keys)
        print(f'Test {i+1}: SUCCESS - {result}')
    except Exception as e:
        print(f'Test {i+1}: FAILED - {e}')

# Test malformed
try:
    parse_llm_json_response('This is not JSON at all')
    print('Malformed test: FAILED - Should have raised exception')
except Exception as e:
    print('Malformed test: SUCCESS - Correctly raised exception')

print('JSON parser testing completed.')
