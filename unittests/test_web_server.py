import unittest
from app.data_ingestor import DataIngestor
import json

class TestWebServer(unittest.TestCase):
    def test_states_mean_case_1(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-1.json', 
                               'unittests/tests/best5/output/out-1.json')

    def test_states_mean_case_2(self):
        self._test_states_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/best5/input/in-2.json', 
                               'unittests/tests/best5/output/out-2.json')

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

        # Compare the result with the reference
        for state, value in reference.items():
            result_value = result.get(state)
            self.assertIsNotNone(result_value, f"State {state} is missing in result.")
            # Ensure that the result matches the expected value with precision of 2 decimals
            self.assertAlmostEqual(result_value, value, places=2, msg=f"Value for {state} doesn't match the expected precision.")


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

if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
