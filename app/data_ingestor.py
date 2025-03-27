import os
import json
import csv

from typing import List, Dict


class Table_Entry:
    def __init__(self,
                index: int, year_start: int, year_end: int, location_abbr: str, location_desc: str,
                datasource: str, classification: str, topic: str, question: str,
                data_value: float, stratification_category1: str, stratification1: str):
        """Initialize a CSV_Entry instance with the provided arguments"""
        self.index = index
        self.year_start = year_start
        self.year_end = year_end
        self.location_abbr = location_abbr
        self.location_desc = location_desc
        self.datasource = datasource
        self.classification = classification
        self.topic = topic
        self.question = question
        self.data_value = data_value
        self.stratification_category1 = stratification_category1
        self.stratification1 = stratification1

    def to_json(self) -> str:
        """Returns a JSON-formatted string of the Table_Entry instance."""
        return json.dumps(self.__dict__)

class DataIngestor:
    def __init__(self, csv_path: str):
        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

        
        self.table_entries: List[Table_Entry] = []
        self._read_csv(csv_path)

    def _read_csv(self, csv_path):
        """Reads the CSV file and extracts relevant columns."""
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)      # Read header row

            for i, row in enumerate(reader):
                try:
                    entry = Table_Entry(
                        index=i,
                        year_start=int(row[1]),
                        year_end=int(row[2]),
                        location_abbr=row[3],
                        location_desc=row[4],
                        datasource=row[5],
                        classification=row[6],
                        topic=row[7],
                        question=row[8],
                        data_value=float(row[11]) if row[11] else None,
                        stratification_category1=row[30],
                        stratification1=row[31]

                    )
                    self.table_entries.append(entry)
                except ValueError as e:
                    print(f"Skipping row {i} due to error: {e}")


    def compute_response_states_mean(self, question: str) -> Dict:
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
        
        state_means = {state: state_totals[state] / state_counts[state] for state in state_totals}
        
        sorted_state_means = dict(sorted(state_means.items(), key=lambda item: item[1]))
        
        return sorted_state_means


    def compute_response_state_mean(self, question: str, state: str) -> Dict:
        # Primește o întrebare (din setul de întrebări de mai sus) și un stat, și calculează media valorilor înregistrate (Data_Value)
        selected_rows = list(filter(lambda entry: entry.question == question
                                    and entry.location_desc == state
                                    and entry.data_value is not None, 
                                    self.table_entries))
        if not selected_rows:
            return {state: None}

        state_mean = sum(entry.data_value for entry in selected_rows) / len(selected_rows)

        return {state: state_mean}


    def compute_response_best5(self, question: str) -> Dict:
        selected_rows = list(filter(lambda entry: entry.question == question and entry.data_value is not None, self.table_entries))

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

        state_means = {state: state_totals[state] / state_counts[state] for state in state_totals}

        # Determine sorting order based on question type
        if question in self.questions_best_is_min:
            sorted_states = sorted(state_means.items(), key=lambda item: item[1])  # Ascending (smallest values are best)
        elif question in self.questions_best_is_max:
            sorted_states = sorted(state_means.items(), key=lambda item: item[1], reverse=True)  # Descending (largest values are best)
        else:
            return {"error": "Question not found in predefined lists"}

        best5 = dict(sorted_states[:5])

        return best5


    def compute_response_worst5(self, question: str) -> Dict:
        selected_rows = list(filter(lambda entry: entry.question == question and entry.data_value is not None, self.table_entries))

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

        state_means = {state: state_totals[state] / state_counts[state] for state in state_totals}

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
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]

        if not selected_values:
            return {"global_mean": None}

        global_mean = sum(selected_values) / len(selected_values)
        return {"global_mean": global_mean}


    def compute_response_diff_from_mean(self, question: str) -> Dict:
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]
        
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

        state_means = {state: state_totals[state] / state_counts[state] for state in state_totals}

        diff_from_mean = {state: global_mean - state_means[state] for state in state_means}

        sorted_diff_from_mean = dict(sorted(diff_from_mean.items(), key=lambda item: item[1], reverse=True))

        return sorted_diff_from_mean


    def compute_response_state_diff_from_mean(self, question: str, state: str) -> Dict:
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]
        
        if not selected_values:
            return {"error": "No data available for the given question"}

        global_mean = sum(selected_values) / len(selected_values)

        state_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.location_desc == state and entry.data_value is not None]

        if not state_values:
            return {state: None}

        state_mean = sum(state_values) / len(state_values)

        diff_from_mean = global_mean - state_mean

        return {state: diff_from_mean}
    
    def compute_response_mean_by_category(self, question: str) -> Dict:
        selected_rows = [
            entry for entry in self.table_entries
            if entry.question == question and entry.data_value is not None
        ]

        if not selected_rows:
            return {"error": "No data available for the given question"}

        category_totals = {}
        category_counts = {}

        for entry in selected_rows:
            key = (entry.location_desc, entry.stratification_category1, entry.stratification1)

            if key not in category_totals:
                category_totals[key] = 0
                category_counts[key] = 0

            category_totals[key] += entry.data_value
            category_counts[key] += 1

        category_means = {key: category_totals[key] / category_counts[key] for key in category_totals}

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
                value_rank = 99  # Default for categories without custom ranking

            return (state, category_rank, value_rank, value)

        sorted_means = dict(sorted(category_means.items(), key=custom_sort_key))

        return {str(k): v for k, v in sorted_means.items()}



if __name__ == '__main__':
    """For testing purposes"""
    data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
    for entry in data_ingestor.table_entries:
        print(entry.to_json())
    print("The CSV table has been successfully read")
