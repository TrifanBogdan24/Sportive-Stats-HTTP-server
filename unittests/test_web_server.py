import unittest
import json
import os
from deepdiff import DeepDiff
from app.data_ingestor import DataIngestor

# Constants For queries only on the 'question'
test_categories_1 = [
    "states_mean", "best5", "worst5", "global_mean", "diff_from_mean", "mean_by_category"
]

# Constants For queries only on both the 'question' and 'state'
test_categories_2 = [
    "state_mean", "state_diff_from_mean", "state_mean_by_category"
]

all_test_categories = test_categories_1 + test_categories_2


def discover_test_cases():
    """Dynamically discovers input/output test cases for each category"""
    test_cases = []
    for category in all_test_categories :
        input_dir = f'unittests/tests/{category}/input'
        output_dir = f'unittests/tests/{category}/output'
        
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            for input_file in sorted(os.listdir(input_dir)):
                if input_file.endswith('.json'):
                    input_path = os.path.join(input_dir, input_file)
                    output_path = os.path.join(output_dir, input_file.replace('in-', 'out-'))
                    if os.path.exists(output_path):
                        test_cases.append((category, input_path, output_path))
    return test_cases

def add_dynamic_tests(test_class):
    """Dynamically adds test methods for each discovered test case"""
    for idx, (category, input_file, output_file) in enumerate(discover_test_cases()):
        def test_func(self, cat=category, in_f=input_file, out_f=output_file):
            self._run_test_case(cat, in_f, out_f)
        setattr(test_class, f'test_{category}_{idx+1}', test_func)

class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.data_ingestor_1 = DataIngestor('unittests/data_for_queries_on_question.csv')
        self.data_ingestor_2 = DataIngestor('unittests/data_for_queries_on_question_and_state.csv')
        self.function_map = {
            "states_mean": self.data_ingestor_1.compute_response_states_mean,
            "best5": self.data_ingestor_1.compute_response_best5,
            "worst5": self.data_ingestor_1.compute_response_worst5,
            "global_mean": self.data_ingestor_1.compute_response_global_mean,
            "diff_from_mean": self.data_ingestor_1.compute_response_diff_from_mean,
            "mean_by_category": self.data_ingestor_1.compute_response_mean_by_category,
            "state_mean": self.data_ingestor_2.compute_response_state_mean,
            "state_diff_from_mean": self.data_ingestor_2.compute_response_state_diff_from_mean,
            "state_mean_by_category": self.data_ingestor_2.compute_response_state_mean_by_category
        }

    def _run_test_case(self, category, input_file, output_file):
        """Helper function to run a single test case"""
        print(f"Running test: {category} with {input_file}")
        with open(input_file) as f:
            request_data = json.load(f)
        question = request_data.get("question")

        with open(output_file) as f:
            expected_output = json.load(f)

        function = self.function_map[category] 

        if category in test_categories_2:
            state = request_data.get("state")
            result = function(question, state)
        else:
            result = function(question)

        diff = DeepDiff(result, expected_output, math_epsilon=0.01)
        self.assertTrue(diff == {}, str(diff))
        test_case_id = str.split(input_file, '/')[-1].removeprefix('in-').removesuffix('.json')
        print(f"[PASSED] {category} case {test_case_id}")

if __name__ == '__main__':
    print("Starting tests...")
    add_dynamic_tests(TestWebServer)
    unittest.main()
