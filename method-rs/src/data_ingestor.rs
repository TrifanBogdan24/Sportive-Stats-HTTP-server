use serde::Deserialize;
use std::{collections::HashMap, fs::File};
use csv::ReaderBuilder;


// Relevant columns from CSV file
#[derive(Debug)]
struct TableEntry {
    index: u32,
    location_desc: String,
    question: String,
    data_value: f32,
    stratification_category1: String,
    stratification1: String
}


#[derive(Debug)]
pub struct Table {
    pub entries: Vec<TableEntry>
}


pub fn load_csv(filename: &str) -> Table {
    let file = File::open(filename)
        .expect("Cannot open file");

    let mut rdr = csv::Reader::from_reader(file);
    let headers = rdr
        .headers()
        .expect("CSV file doesn't have header line")
        .clone();

    let mut entries: Vec<TableEntry> = vec![];
    let mut line_index = 0;

    for result in rdr.records() {
        line_index = line_index + 1;
        match result  {
            Ok(entry) => {
                let row: HashMap<_, _> = headers.iter().zip(entry.iter()).collect();

                // Get cell value by column name: 

                let location_desc: &str = row
                    .get("LocationDesc")
                    .expect("Missing \"LocationDesc\" column");

                let question: &str = row
                    .get("Question")
                    .expect("Missing \"Question\" column");
                
                let data_value: f32 = row
                    .get("Data_Value")
                    .expect("Missing \"Data_Value\" column")
                    .parse::<f32>()
                    .expect("Cannot parse \"Data_Value\" as f32");
    

                let stratification_category1: &str = row
                    .get("StratificationCategory1")
                    .expect("Missing \"StratificationCategory1\" column");

                let stratification1: &str = row
                    .get("Stratification1")
                    .expect("Missing \"Stratification1\" column");

                entries.push(
                    TableEntry {
                        index: line_index,
                        location_desc: location_desc.to_string(),
                        question: question.to_string(),
                        data_value: data_value,
                        stratification_category1: stratification_category1.to_string(),
                        stratification1: stratification1.to_string()
                    }
                )
            }
            Err(err) => eprintln!("[ERR] Skipping row due to: {}", err)
        }
    }


    Table {
        entries: entries
    }
}


pub fn compute_response_states_mean(table: &Table, question: &str) {
    // TODO:
}



