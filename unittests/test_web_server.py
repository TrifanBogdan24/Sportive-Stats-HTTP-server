import unittest
import json
from deepdiff import DeepDiff

from app.data_ingestor import DataIngestor


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
            reference_result = json.load(file)
        
        # Get the result from the compute_states_mean method
        result = data_ingestor.compute_response_states_mean(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

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
            reference_result = json.load(file)
        
        # Get the result from the compute_response_best5 method
        result = data_ingestor.compute_response_best5(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))



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
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference_result = json.load(file)
        
        # Get the result from the compute_response_best5 method
        result = data_ingestor.compute_response_best5(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

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
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference_result = json.load(file)
        
        result = data_ingestor.compute_response_global_mean(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_diff_from_mean_case_1(self):
        self._test_diff_from_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/diff_from_mean/input/in-1.json', 
                               'unittests/tests/diff_from_mean/output/out-1.json')

    def test_diff_from_mean_case_2(self):
        self._test_diff_from_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/diff_from_mean/input/in-2.json', 
                               'unittests/tests/diff_from_mean/output/out-2.json')



    def _test_diff_from_mean(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing the diff_from_mean 
        It is reusable across multiple test cases with different file paths.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference_result = json.load(file)
        
        result = data_ingestor.compute_response_diff_from_mean(question)


        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))



    def test_diff_from_mean_case_1(self):
        self._test_diff_from_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/diff_from_mean/input/in-1.json', 
                               'unittests/tests/diff_from_mean/output/out-1.json')

    def test_diff_from_mean_case_2(self):
        self._test_diff_from_mean('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/diff_from_mean/input/in-2.json', 
                               'unittests/tests/diff_from_mean/output/out-2.json')


    def test_mean_by_category_case_1(self):
        self._test_mean_by_category('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/mean_by_category/input/in-1.json', 
                               'unittests/tests/mean_by_category/output/out-1.json')

    def test_mean_by_category_case_2(self):
        self._test_mean_by_category('unittests/sample_data_multiple_states.csv', 
                               'unittests/tests/mean_by_category/input/in-2.json', 
                               'unittests/tests/mean_by_category/output/out-2.json')



    def _test_mean_by_category(self, data_file, input_file, output_file):
        """
        Helper method to perform the test logic for computing the mean_by_category
        It is reusable across multiple test cases with different file paths.
        """
        data_ingestor = DataIngestor(data_file)

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference_result = json.load(file)
        
        result = data_ingestor.compute_response_mean_by_category(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))


if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
