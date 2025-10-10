mod data_ingestor;

use crate::data_ingestor::{load_csv, Table};

fn main() {
    let table: Table = load_csv("../nutrition_activity_obesity_usa_subset.csv");
    println!("CSV loaded");

}
