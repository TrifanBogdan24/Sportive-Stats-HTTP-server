import os
import json
import csv

from typing import List


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
        # TODO: Read csv from csv_path



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


    def compute_response_states_mean(self, question: str) -> str:
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
        
        return json.dumps(sorted_state_means)


    def compute_response_state_mean(self, question: str, state: str) -> str:
        # Primește o întrebare (din setul de întrebări de mai sus) și un stat, și calculează media valorilor înregistrate (Data_Value)
        selected_rows = list(filter(lambda entry: entry.question == question
                                    and entry.location_desc == state
                                    and entry.data_value is not None, 
                                    self.table_entries))
        if not selected_rows:
            return json.dumps({state: None})

        state_mean = sum(entry.data_value for entry in selected_rows) / len(selected_rows)

        return json.dumps({state: state_mean})


    def compute_response_best5(self, question: str):
        selected_rows = list(filter(lambda entry: entry.question == question and entry.data_value is not None, self.table_entries))

        if not selected_rows:
            return json.dumps({"error": "No data available for the given question"})

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
            return json.dumps({"error": "Question not found in predefined lists"})

        best5 = dict(sorted_states[:5])

        return json.dumps(best5)


    def compute_response_worst5(self, question: str):
        selected_rows = list(filter(lambda entry: entry.question == question and entry.data_value is not None, self.table_entries))

        if not selected_rows:
            return json.dumps({"error": "No data available for the given question"})

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
            return json.dumps({"error": "Question not found in predefined lists"})

        worst5 = dict(sorted_states[:5])

        return json.dumps(worst5)

    def compute_response_global_mean(self, question: str):
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]

        if not selected_values:
            return json.dumps({"global_mean": None})

        global_mean = sum(selected_values) / len(selected_values)
        return json.dumps({"global_mean": global_mean})


    def compute_response_diff_from_mean(self, question: str):
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]
        
        if not selected_values:
            return json.dumps({"error": "No data available for the given question"})

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

        return json.dumps(sorted_diff_from_mean)


    def compute_response_state_diff_from_mean(self, question: str, state: str):
        selected_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.data_value is not None]
        
        if not selected_values:
            return json.dumps({"error": "No data available for the given question"})

        global_mean = sum(selected_values) / len(selected_values)

        state_values = [entry.data_value for entry in self.table_entries if entry.question == question and entry.location_desc == state and entry.data_value is not None]

        if not state_values:
            return json.dumps({state: None})

        state_mean = sum(state_values) / len(state_values)

        diff_from_mean = global_mean - state_mean

        return json.dumps({state: diff_from_mean})


if __name__ == '__main__':
    """For testing purposes"""
    data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
    for entry in data_ingestor.table_entries:
        print(entry.to_json())
    print("The CSV table has been successfully read")
