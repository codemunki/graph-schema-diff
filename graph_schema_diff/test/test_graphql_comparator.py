import pytest
import json
import os
from graph_schema_diff.graphql_comparator import GraphQLComparator

# Helper function to load schema from a file
def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

@pytest.fixture
def comparator():
    model_file = os.getenv("MODEL_FILE", "models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf")
    expected_json_path = os.getenv("EXPECTED_JSON_PATH", "data/expected.json")

    # Configure for 10 GPU layers and a context length of 2048
    n_gpu_layers = 10
    n_ctx = 2048

    return GraphQLComparator(model_file=model_file, expected_json_path=expected_json_path, n_gpu_layers=n_gpu_layers, n_ctx=n_ctx)

def run_compare_test(comparator, test_case_dir):
    """
    Helper function to run a compare test for a given test case directory.
    """
    schema1 = load_file(f"{test_case_dir}/schema1.graphql")
    schema2 = load_file(f"{test_case_dir}/schema2.graphql")

    # Load the expected result
    expected_result_file = f"{test_case_dir}/expected_result.json"
    expected_result = json.loads(load_file(expected_result_file))

    # Run the comparison
    result = comparator.compare(schema1, schema2)

    # Validate the status
    assert result["status"] == "success", f"Test failed for {test_case_dir}: Comparison did not succeed"

    # Extract actual and expected breaking changes
    actual_breaking_changes = [change for change in result["result"].get("changes", []) if change["breaking"]]
    expected_breaking_changes = [change for change in expected_result.get("changes", []) if change["breaking"]]

    unmatched_expected = []
    unexpected_actual = []

    # Check that all expected breaking changes are found in the actual result
    for expected_change in expected_breaking_changes:
        found_match = any(
            expected_change["type"] == actual_change["type"] and
            expected_change["field"] == actual_change["field"] and
            expected_change["breaking"] == actual_change["breaking"]
            for actual_change in actual_breaking_changes
        )
        if not found_match:
            unmatched_expected.append(expected_change)

    # Check for unexpected breaking changes in the actual result
    for actual_change in actual_breaking_changes:
        found_match = any(
            actual_change["type"] == expected_change["type"] and
            actual_change["field"] == expected_change["field"] and
            actual_change["breaking"] == expected_change["breaking"]
            for expected_change in expected_breaking_changes
        )
        if not found_match:
            unexpected_actual.append(actual_change)

    # If there are unmatched expected or unexpected actual breaking changes, report them
    if unmatched_expected or unexpected_actual:
        print(f"Test failed for {test_case_dir}:")

        if unmatched_expected:
            print("\nExpected breaking changes not found in actual result:")
            print(json.dumps(unmatched_expected, indent=4))

        if unexpected_actual:
            print("\nUnexpected breaking changes found in actual result:")
            print(json.dumps(unexpected_actual, indent=4))

        print("\nActual result:")
        print(json.dumps(result, indent=4))

        print("\nExpected result:")
        print(json.dumps(expected_result, indent=4))

        assert False, f"Test failed for {test_case_dir} due to unmatched or unexpected breaking changes."

    print(f"Comparison for {test_case_dir} passed.\n")

# Test for test1 case
def test_compare_test1(comparator):
    run_compare_test(comparator, "data/test1")

# Test for test2 case
def test_compare_test2(comparator):
    run_compare_test(comparator, "data/test2")

# Test for test3 case
def test_compare_test3(comparator):
    run_compare_test(comparator, "data/test3")

# Test for test4 case
def test_compare_test4(comparator):
    run_compare_test(comparator, "data/test4")
