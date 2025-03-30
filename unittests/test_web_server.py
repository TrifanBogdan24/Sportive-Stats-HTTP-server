import unittest
from app.data_ingestor import DataIngestor
import json

class TestWebServer(unittest.TestCase):
    def test_states_mean_case_1(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/states_mean/input/in-1.json', 
                               'unittests/tests/states_mean/output/out-1.json')

    def test_states_mean_case_2(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/states_mean/input/in-2.json', 
                               'unittests/tests/states_mean/output/out-2.json')

    def _test_states_mean(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing states mean.
        It is reusable across multiple test cases with different file paths.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference = json.load(file)
        
        # Get the result from the compute_states_mean method
        result = data_ingestor.compute_response_states_mean(question)

        # Ensure all states in reference appear in the result (no missing or extra states)
        self.assertEqual(set(reference.keys()), set(result.keys()), "Result is missing states from reference or has extra states.")

        # Sort both reference and result by their values
        sorted_reference = dict(sorted(reference.items(), key=lambda item: item[1]))
        sorted_result = dict(sorted(result.items(), key=lambda item: item[1]))

        # Ensure keys are in the same order after sorting by values
        self.assertEqual(list(sorted_result.keys()), list(sorted_reference.keys()), "Keys in the result must appear in ascending order of values.")

        # Assert values with a precision of 2 decimal places
        for state in sorted_reference:
            self.assertAlmostEqual(sorted_result[state], sorted_reference[state], places=2, msg=f"Mismatch in values for {state}.")

    def test_best5_case_1(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-1.json', 
                               'unittests/tests/best5/output/out-1.json')

    def test_best5_case_2(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-2.json', 
                               'unittests/tests/best5/output/out-2.json')

    def _test_best5(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing the best 5 states.
        It is reusable across multiple test cases with different file paths.
        Assumes the result and reference are already sorted in descending order.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference = json.load(file)
        
        # Get the result from the compute_response_best5 method
        result = data_ingestor.compute_response_best5(question)

        # Ensure the result has exactly 5 states (direct check)
        self.assertEqual(len(result), 5, "The result does not contain exactly 5 states.")
        
        # Ensure the reference has exactly 5 states (direct check)
        self.assertEqual(len(reference), 5, "The reference does not contain exactly 5 states.")

        # Compare the result with the reference, directly checking each entry
        for idx, (state, value) in enumerate(reference.items()):
            if state in result:
                result_value = result[state]
                # Ensure that the result matches the expected value with precision of 2 decimals
                self.assertAlmostEqual(result_value, value, places=2,
                                    msg=f"Value for {state} at position {idx + 1} doesn't match the expected precision. Expected {value}, but got {result_value}.")
            else:
                self.fail(f"State {state} is missing in the result.")



    def test_worst5_case_1(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-1.json', 
                               'unittests/tests/best5/output/out-1.json')

    def test_worst5_case_2(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-2.json', 
                               'unittests/tests/best5/output/out-2.json')

    def _test_worst5(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing the best 5 states.
        It is reusable across multiple test cases with different file paths.
        Assumes the result and reference are already sorted in descending order.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference = json.load(file)
        
        # Get the result from the compute_response_best5 method
        result = data_ingestor.compute_response_best5(question)

        # Ensure the result has exactly 5 states (direct check)
        self.assertEqual(len(result), 5, "The result does not contain exactly 5 states.")
        
        # Ensure the reference has exactly 5 states (direct check)
        self.assertEqual(len(reference), 5, "The reference does not contain exactly 5 states.")

        # Compare the result with the reference, directly checking each entry
        for idx, (state, value) in enumerate(reference.items()):
            if state in result:
                result_value = result[state]
                # Ensure that the result matches the expected value with precision of 2 decimals
                self.assertAlmostEqual(result_value, value, places=2,
                                    msg=f"Value for {state} at position {idx + 1} doesn't match the expected precision. Expected {value}, but got {result_value}.")
            else:
                self.fail(f"State {state} is missing in the result.")

    def test_global_mean_case_1(self):
        self._test_global_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/global_mean/input/in-1.json', 
                               'unittests/tests/global_mean/output/out-1.json')

    def test_global_mean_case_2(self):
        self._test_global_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/global_mean/input/in-2.json', 
                               'unittests/tests/global_mean/output/out-2.json')

    def _test_global_mean(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing the global_mean 
        It is reusable across multiple test cases with different file paths.
        Assumes the result and reference are already sorted in descending order.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference = json.load(file)
        
        result = data_ingestor.compute_response_global_mean(question)


        self.assertIn("global_mean", result, "The key 'global_mean' is missing in the result JSON")
        expected_global_mean = reference["global_mean"]
        result_value = result.get('global_mean')


        # Use assertAlmostEqual to compare result and expected value with precision up to 2 decimal places
        self.assertAlmostEqual(result_value, expected_global_mean, places=2,
                               msg=f"Expected global_mean: {expected_global_mean}, but got: {result_value}")


if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
