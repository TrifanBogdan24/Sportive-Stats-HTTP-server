import unittest
import json
from deepdiff import DeepDiff

from app.data_ingestor import DataIngestor


CSV_FILE_FOR_QUERIES_ON_QEUSTION = 'unittests/sample_data_multiple_states.csv'
DATA_FILE_QUERIES_ON_QEUSTION_AND_STATE = 'unittests/sample_data_multiple_states.csv'

class TestWebServer(unittest.TestCase):
    def test_states_mean_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_states_mean, 
            'unittests/tests/states_mean/input/in-1.json', 
            'unittests/tests/states_mean/output/out-1.json')

    def test_states_mean_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_states_mean, 
            'unittests/tests/states_mean/input/in-2.json', 
            'unittests/tests/states_mean/output/out-2.json')


    def test_best5_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_best5, 
            'unittests/tests/best5/input/in-1.json', 
            'unittests/tests/best5/output/out-1.json')

    def test_best5_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_best5, 
            'unittests/tests/best5/input/in-2.json', 
            'unittests/tests/best5/output/out-2.json')

    def test_worst5_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_worst5, 
            'unittests/tests/best5/input/in-1.json', 
            'unittests/tests/best5/output/out-1.json')

    def test_worst5_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_worst5, 
            'unittests/tests/best5/input/in-2.json', 
            'unittests/tests/best5/output/out-2.json')

    def test_global_mean_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_global_mean, 
            'unittests/tests/global_mean/input/in-1.json', 
            'unittests/tests/global_mean/output/out-1.json')

    def test_global_mean_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_global_mean, 
            'unittests/tests/global_mean/input/in-2.json', 
            'unittests/tests/global_mean/output/out-2.json')


    def test_diff_from_mean_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)

        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_diff_from_mean, 
            'unittests/tests/diff_from_mean/input/in-1.json', 
            'unittests/tests/diff_from_mean/output/out-1.json')

    def test_diff_from_mean_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_diff_from_mean, 
            'unittests/tests/diff_from_mean/input/in-2.json', 
            'unittests/tests/diff_from_mean/output/out-2.json')


    def test_mean_by_category_case_1(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_mean_by_category,
            'unittests/tests/mean_by_category/input/in-1.json', 
            'unittests/tests/mean_by_category/output/out-1.json')

    def test_mean_by_category_case_2(self):
        data_ingestor = DataIngestor(CSV_FILE_FOR_QUERIES_ON_QEUSTION)
        self._test_function_that_queries_just_question(
            data_ingestor.compute_response_mean_by_category,
            'unittests/tests/mean_by_category/input/in-2.json', 
            'unittests/tests/mean_by_category/output/out-2.json')

    
    def _test_function_that_queries_just_question(self, function, input_file, output_file):
        """
        Helper method to perform the test logic for computing the mean_by_category
        It is reusable across multiple test cases with different file paths.
        """

        # Load input JSON data
        with open(input_file) as file:
            request_data = json.load(file)
        question = request_data["question"]
        
        # Load expected output JSON data
        with open(output_file) as file:
            reference_result = json.load(file)
        
        result = function(question)

        d = DeepDiff(result, reference_result, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

if __name__ == '__main__':
    print("Starting tests...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWebServer)
    unittest.TextTestRunner(verbosity=2).run(suite)
