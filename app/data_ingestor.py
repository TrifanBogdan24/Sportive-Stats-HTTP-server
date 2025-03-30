"""Module for calculating statistical operations on a CSV"""
import json
import csv

from typing import List, Dict


class TableEntry:
    """Class used to store in memory a row from a CSV table"""

    def __init__(self, index: int, row: list[str]):
        """Initialize a TableEntry instance by providing a row and its index"""
        self.index = index
        self.location_desc = row[4]
        self.question = row[8]
        self.data_value = float(row[11]) if row[11] else None
        self.stratification_category1 = row[30]
        self.stratification1 = row[31]

    def to_json(self) -> str:
        """Returns a JSON-formatted string of the Table_Entry instance"""
        return json.dumps(self.__dict__)

class DataIngestor:
    """
    The DataIngestor reads a CSV file, extracts relevant data
    and stores it in memory as list of TableEntry objects.
    
    It provides methods to perform statistical analyses
    for HTTP POST requests that are made to the server.
    """

    def __init__(self, csv_path: str):
        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week '
                + 'of moderate-intensity aerobic physical activity '
                + 'or 75 minutes a week of vigorous-intensity aerobic activity '
                + '(or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week '
                + 'of moderate-intensity aerobic physical activity '
                + 'or 75 minutes a week of vigorous-intensity aerobic physical activity '
                + 'and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week '
                + 'of moderate-intensity aerobic physical activity '
                + 'or 150 minutes a week of vigorous-intensity aerobic activity '
                + '(or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities '
                + 'on 2 or more days a week',
        ]


        self.table_entries: List[TableEntry] = []
        self._read_csv(csv_path)

    def _read_csv(self, csv_path):
        """Reads the CSV file and extracts only the relevant columns"""
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)      # Read header row

            for index, row in enumerate(reader):
                try:
                    entry = TableEntry(index, row)
                    self.table_entries.append(entry)
                except ValueError as err:
                    print(f"Skipping row {index} due to error: {err}")


    def compute_response_states_mean(self, question: str) -> Dict:
        """
        Returns the response for '/api/states_mean' request as a JSON dictionary
        """
        selected_rows = list(filter(lambda entry: entry.question == question
                                    and entry.data_value is not None,
                                    self.table_entries))

        state_totals = {}
        state_counts = {}

        for entry in selected_rows:
            state = entry.location_desc
            if state not in state_totals:
                state_totals[state] = 0
                state_counts[state] = 0
            state_totals[state] += entry.data_value
            state_counts[state] += 1

        state_means = {state: total / state_counts[state] for state, total in state_totals.items()}

        sorted_state_means = dict(sorted(state_means.items(), key=lambda item: item[1]))

        return sorted_state_means


    def compute_response_state_mean(self, question: str, state: str) -> Dict:
        """
        Returns the response for '/api/state_mean' request as a JSON dictionary
        """
        selected_rows = list(filter(lambda entry: entry.question == question
                                    and entry.location_desc == state
                                    and entry.data_value is not None,
                                    self.table_entries))

        if not selected_rows:
            return {state: None}

        state_mean = sum(entry.data_value for entry in selected_rows) / len(selected_rows)

        return {state: state_mean}


    def compute_response_best5(self, question: str) -> Dict:
        """
        Returns the response for '/api/best5' request as a JSON dictionary
        """
        selected_rows = list(filter(
            lambda entry: entry.question == question and entry.data_value is not None,
            self.table_entries
        ))

        if not selected_rows:
            return {"error": "No data available for the given question"}

        state_totals = {}
        state_counts = {}

        for entry in selected_rows:
            state = entry.location_desc
            if state not in state_totals:
                state_totals[state] = 0
                state_counts[state] = 0
            state_totals[state] += entry.data_value
            state_counts[state] += 1

        state_means = {state: total / state_counts[state] for state, total in state_totals.items()}

        # Determine sorting order based on question type
        if question in self.questions_best_is_min:
            # Ascending (smallest values are best)
            sorted_states = sorted(state_means.items(), key=lambda item: item[1])
        elif question in self.questions_best_is_max:
            # Descending (largest values are best)
            sorted_states = sorted(state_means.items(), key=lambda item: item[1], reverse=True)
        else:
            return {"error": "Question not found in predefined lists"}

        best5 = dict(sorted_states[:5])

        return best5


    def compute_response_worst5(self, question: str) -> Dict:
        """
        Returns the response for '/api/worst5' request as a JSON dictionary
        """
        selected_rows = list(filter(
            lambda entry: entry.question == question and entry.data_value is not None,
            self.table_entries
        ))

        if not selected_rows:
            return {"error": "No data available for the given question"}

        state_totals = {}
        state_counts = {}

        for entry in selected_rows:
            state = entry.location_desc
            if state not in state_totals:
                state_totals[state] = 0
                state_counts[state] = 0
            state_totals[state] += entry.data_value
            state_counts[state] += 1

        state_means = {state: total / state_counts[state] for state, total in state_totals.items()}

        # Determine sorting order based on question type
        if question in self.questions_best_is_min:
            # Descending (largest values are worst)
            sorted_states = sorted(state_means.items(), key=lambda item: item[1], reverse=True)
        elif question in self.questions_best_is_max:
            # Ascending (smallest values are worst)
            sorted_states = sorted(state_means.items(), key=lambda item: item[1])
        else:
            return {"error": "Question not found in predefined lists"}

        worst5 = dict(sorted_states[:5])
        return worst5

    def compute_response_global_mean(self, question: str) -> Dict:
        """
        Returns the response for '/api/global_mean' request as a JSON dictionary
        """
        selected_values = [
            entry.data_value
            for entry in self.table_entries
            if entry.question == question
            and entry.data_value is not None
        ]

        if not selected_values:
            return {"global_mean": None}

        global_mean = sum(selected_values) / len(selected_values)
        return {"global_mean": global_mean}


    def compute_response_diff_from_mean(self, question: str) -> Dict:
        """
        Returns the response for '/api/diff_from_mean' request as a JSON dictionary
        """
        selected_values = [
            entry.data_value
            for entry in self.table_entries
            if entry.question == question and entry.data_value is not None
        ]

        if not selected_values:
            return {"error": "No data available for the given question"}

        global_mean = sum(selected_values) / len(selected_values)

        state_totals = {}
        state_counts = {}

        for entry in self.table_entries:
            if entry.question == question and entry.data_value is not None:
                state = entry.location_desc
                if state not in state_totals:
                    state_totals[state] = 0
                    state_counts[state] = 0
                state_totals[state] += entry.data_value
                state_counts[state] += 1

        state_means = {
            state: total / state_counts[state] for state, total in state_totals.items()
        }

        diff_from_mean = {state: global_mean - mean for state, mean in state_means.items()}

        sorted_diff_from_mean = dict(
            sorted(
                diff_from_mean.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

        return sorted_diff_from_mean


    def compute_response_state_diff_from_mean(self, question: str, state: str) -> Dict:
        """
        Returns the response for '/api/state_diff_from_mean' request as a JSON dictionary
        """
        selected_values = [
            entry.data_value
            for entry in self.table_entries
            if entry.question == question
            and entry.data_value is not None
        ]

        if not selected_values:
            return {"error": "No data available for the given question"}

        global_mean = sum(selected_values) / len(selected_values)

        state_values = [
            entry.data_value
            for entry in self.table_entries
            if entry.question == question
            and entry.location_desc == state
            and entry.data_value is not None
        ]

        if not state_values:
            return {state: None}

        state_mean = sum(state_values) / len(state_values)

        diff_from_mean = global_mean - state_mean

        return {state: diff_from_mean}


    def compute_response_mean_by_category(self, question: str) -> Dict:
        """
        Returns the response for '/api/mean_by_category' request as a JSON dictionary
        """
        selected_rows = [
            entry for entry in self.table_entries
            if entry.question == question and entry.data_value is not None
        ]

        # Dacă nu sunt date disponibile, returnăm un JSON vid
        if not selected_rows:
            return {}

        category_totals = {}
        category_counts = {}

        for entry in selected_rows:
            # Exclude entries with empty or invalid stratification categories
            if not entry.stratification_category1 or not entry.stratification1:
                continue

            key = (entry.location_desc, entry.stratification_category1, entry.stratification1)

            if key not in category_totals:
                category_totals[key] = 0
                category_counts[key] = 0

            category_totals[key] += entry.data_value
            category_counts[key] += 1

        # Calculăm media pentru fiecare categorie
        category_means = {
            key: total / category_counts[key] for key, total in category_totals.items()
        }

        # Sorting order
        category_priority = {
            "Age (years)": 1,
            "Education": 2,
            "Gender": 3,
            "Income": 4,
            "Race/Ethnicity": 5,
            "Total": 6
        }

        age_priority = {
            "18 - 24": 1, "25 - 34": 2, "35 - 44": 3, "45 - 54": 4, "55 - 64": 5, "65 or older": 6
        }

        education_priority = {
            "Less than high school": 1, "High school graduate": 2,
            "Some college or technical school": 3, "College graduate": 4
        }

        income_priority = {
            "Less than $15,000": 1, "$15,000 - $24,999": 2, "$25,000 - $34,999": 3,
            "$35,000 - $49,999": 4, "$50,000 - $74,999": 5, "$75,000 or greater": 6,
            "Data not reported": 7
        }

        def custom_sort_key(item):
            state, category, value = item[0]
            category_rank = category_priority.get(category, 99)

            if category == "Age (years)":
                value_rank = age_priority.get(value, 99)
            elif category == "Education":
                value_rank = education_priority.get(value, 99)
            elif category == "Income":
                value_rank = income_priority.get(value, 99)
            else:
                # Default for categories without custom ranking
                value_rank = 99

            return (state, category_rank, value_rank, value)

        sorted_means = dict(sorted(category_means.items(), key=custom_sort_key))

        return {str(k): v for k, v in sorted_means.items()}



    def compute_response_state_mean_by_category(self, question: str, state: str) -> Dict:
        """
        Returns the response for '/api/state_mean_by_category' request as a JSON dictionary
        """
        # Select rows that match the question and the state, with valid data_value
        selected_rows = [
            entry for entry in self.table_entries
            if entry.question == question
                and entry.location_desc == state
                and entry.data_value is not None
        ]

        if not selected_rows:
            return {"error": "No data available for the given question and state"}

        # Dictionary to store the total values and counts
        # for each stratification category and stratification
        category_totals = {}
        category_counts = {}

        for entry in selected_rows:
            key = (entry.stratification_category1, entry.stratification1)

            if key not in category_totals:
                category_totals[key] = 0
                category_counts[key] = 0

            category_totals[key] += entry.data_value
            category_counts[key] += 1

        # Calculate the mean for each category-stratification combination
        category_means = {
            key: total / category_counts[key]
            for key, total in category_totals.items()
        }

        calculated_values = {str(k): v for k, v in category_means.items()}
        return {state: calculated_values}
