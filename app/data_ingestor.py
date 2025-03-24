import os
import json
import csv


class Table_Entry:
    def __init__(self, index: int, year_start: int, year_end: int, location_abbr: str, location_desc: str, datasource: str, classification: str, topic: str, question: str, data_value: float, stratification_category1: str, stratification1: str):
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
        return (
            "{\n"
            f"\tIndex: {self.index},\n"
            f"\tYearStart: {self.year_start},\n"
            f"\tYearEnd: {self.year_end},\n"
            f"\tLocationAbbr: \"{self.location_abbr}\",\n"
            f"\tLocationDesc: \"{self.location_desc}\",\n"
            f"\tDatasource: \"{self.datasource}\",\n"
            f"\tClassification: \"{self.classification}\",\n"
            f"\tData_Value: {self.data_value},\n"
            f"\tStratificationCategory1: {self.stratification_category1},\n"
            f"\tStratification1: {self.stratification1}\n"
            "}"
        )

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

        
        self.table_entries = []
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



if __name__ == '__main__':
    """For testing purposes"""
    data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
    for entry in data_ingestor.table_entries:
        print(entry.to_json())
    print("The CSV table has been successfully read")
