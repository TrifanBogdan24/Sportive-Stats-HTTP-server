use csv::ReaderBuilder;
use serde::{Deserialize, Serialize};
use serde_json::{self, json};
use std::{
    collections::{self, HashMap, btree_map::Range},
    fs::File,
    os::linux::raw::stat,
};

/// This is best-effort (cannot store String as const)

const QUESTIONS_BEST_IS_MIN: &[&str] = &[
    "Percent of adults aged 18 years and older who have an overweight classification",
    "Percent of adults aged 18 years and older who have obesity",
    "Percent of adults who engage in no leisure-time physical activity",
    "Percent of adults who report consuming fruit less than one time daily",
    "Percent of adults who report consuming vegetables less than one time daily",
];

const QUESTIONS_BEST_IS_MAX: &[&str] = &[
    "Percent of adults who achieve at least 150 minutes a week \
        of moderate-intensity aerobic physical activity \
        or 75 minutes a week of vigorous-intensity aerobic activity \
        (or an equivalent combination)",
    "Percent of adults who achieve at least 150 minutes a week \
        of moderate-intensity aerobic physical activity \
        or 75 minutes a week of vigorous-intensity aerobic physical activity \
        and engage in muscle-strengthening activities on 2 or more days a week",
    "Percent of adults who achieve at least 300 minutes a week \
        of moderate-intensity aerobic physical activity \
        or 150 minutes a week of vigorous-intensity aerobic activity \
        (or an equivalent combination)",
    "Percent of adults who engage in muscle-strengthening activities \
        on 2 or more days a week",
];

#[derive(PartialEq)]
enum RankingType {
    Best5,
    Worst5,
}

// Relevant columns from CSV file
#[derive(Debug, Serialize)]
struct TableEntry {
    index: u32,
    location_desc: String,
    question: String,
    data_value: f32,
    stratification_category1: String,
    stratification1: String,
}

#[derive(Debug, Serialize)]
pub struct Table {
    pub entries: Vec<TableEntry>,
}

pub fn load_csv(filename: &str) -> Table {
    let file = File::open(filename).expect("Cannot open file");

    let mut rdr = csv::Reader::from_reader(file);
    let headers = rdr
        .headers()
        .expect("CSV file doesn't have header line")
        .clone();

    let mut entries: Vec<TableEntry> = vec![];
    let mut line_index = 0;

    for result in rdr.records() {
        line_index = line_index + 1;
        match result {
            Ok(entry) => {
                let row: HashMap<_, _> = headers.iter().zip(entry.iter()).collect();

                // Get cell value by column name:

                let location_desc: &str = row
                    .get("LocationDesc")
                    .expect("Missing \"LocationDesc\" column");

                let question: &str = row.get("Question").expect("Missing \"Question\" column");

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

                entries.push(TableEntry {
                    index: line_index,
                    location_desc: location_desc.to_string(),
                    question: question.to_string(),
                    data_value: data_value,
                    stratification_category1: stratification_category1.to_string(),
                    stratification1: stratification1.to_string(),
                })
            }
            Err(err) => eprintln!("[ERR] Skipping row due to: {}", err),
        }
    }

    Table { entries: entries }
}

fn compute_states_mean<'a>(table: &'a Table, question: &'a str) -> HashMap<&'a str, f32> {
    let selected_entries: Vec<&TableEntry> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question)
        .collect();

    let mut state_totals: HashMap<&str, f32> = HashMap::new();
    let mut state_counts: HashMap<&str, u32> = HashMap::new();

    for entry in selected_entries {
        let state: &str = &entry.location_desc;

        if let Some(value) = state_totals.get(state) {
            // HashMap contains key
            state_totals.insert(&state, value + entry.data_value);
        } else {
            // HashMap does NOT contain key
            state_totals.insert(&state, 0.0);
        }

        if let Some(value) = state_counts.get(state) {
            // HashMap contains key
            state_counts.insert(&state, value + 1);
        } else {
            // HashMap does NOT contain key
            state_counts.insert(&state, 0);
        }
    }

    let mut states_mean: HashMap<&str, f32> = HashMap::new();

    for (state, total) in state_totals.iter() {
        states_mean.insert(
            &state,
            total / state_counts.get(state).unwrap().clone() as f32,
        );
    }

    states_mean
}

pub fn json_response_states_mean(table: &Table, question: &str) -> String {
    // TODO:
    let states_mean: HashMap<&str, f32> = compute_states_mean(table, question);
    serde_json::to_string(&states_mean).unwrap()
}

pub fn json_response_state_mean(table: &Table, question: &str, state: &str) -> String {
    // TODO:
    let selected_entries: Vec<&TableEntry> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question && entry.location_desc == state)
        .collect();

    if selected_entries.is_empty() {
        // TODO: treat this case
        return String::new();
    }

    let state_total: f32 = selected_entries.iter().map(|entry| entry.data_value).sum();

    let mut state_mean: HashMap<&str, f32> = HashMap::new();

    state_mean.insert(&state, state_total / selected_entries.len() as f32);

    serde_json::to_string(&state_mean).unwrap()
}

fn get_best5_or_worst5(
    states_mean: &HashMap<&str, f32>,
    question: &str,
    ranking_type: RankingType,
) -> String {
    let is_question_in_best_mins: bool = QUESTIONS_BEST_IS_MIN.contains(&question);
    let is_question_in_best_maxs: bool = QUESTIONS_BEST_IS_MAX.contains(&question);

    if (is_question_in_best_mins == true && ranking_type == RankingType::Best5)
        || (is_question_in_best_maxs == true && ranking_type == RankingType::Worst5)
    {
        // Sort in ASCENDING order (smaller values are best)
        let mut sorted: Vec<(&&str, &f32)> = states_mean.iter().collect();
        sorted.sort_by(|a, b| a.1.partial_cmp(b.1).unwrap());

        // Take first 5 (handles cases with <5 elements)
        let top5_vec = &sorted[..5.min(sorted.len())];

        // Convert to HashMap
        let top5_map: HashMap<_, _> = top5_vec.iter().map(|(k, v)| (k, **v)).collect();

        serde_json::to_string(&top5_map).unwrap()
    } else if (is_question_in_best_maxs == true && ranking_type == RankingType::Best5)
        || (is_question_in_best_mins == true && ranking_type == RankingType::Worst5)
    {
        // Sort in DESCENDING order (bigger values are best)
        let mut sorted: Vec<(&&str, &f32)> = states_mean.iter().collect();
        sorted.sort_by(|a, b| b.1.partial_cmp(a.1).unwrap());

        // Take first 5 (handles cases with <5 elements)
        let top5_vec = &sorted[..5.min(sorted.len())];

        // Convert to HashMap
        let top5_map: HashMap<_, _> = top5_vec.iter().map(|(k, v)| (k, **v)).collect();

        serde_json::to_string(&top5_map).unwrap()
    } else {
        let mut response: HashMap<&str, &str> = HashMap::new();
        response.insert("error", "Question not found in predefined lists");

        serde_json::to_string(&response).unwrap()
    }
}

pub fn json_response_best5(table: &Table, question: &str) -> String {
    // TODO
    let states_mean: HashMap<&str, f32> = compute_states_mean(table, question);

    if states_mean.is_empty() {
        let mut response: HashMap<&str, &str> = HashMap::new();
        response.insert(&"error", &"No data available for the given question");

        serde_json::to_string(&response).unwrap()
    } else {
        get_best5_or_worst5(&states_mean, question, RankingType::Best5)
    }
}

pub fn json_response_worst5(table: &Table, question: &str) -> String {
    // TODO
    let states_mean: HashMap<&str, f32> = compute_states_mean(table, question);

    if states_mean.is_empty() {
        let mut response: HashMap<String, String> = HashMap::new();
        response.insert(
            "error".to_string(),
            "No data available for the given question".to_string(),
        );

        serde_json::to_string(&response).unwrap()
    } else {
        get_best5_or_worst5(&states_mean, question, RankingType::Worst5)
    }
}

pub fn json_response_global_mean(table: &Table, question: &str) -> String {
    let selected_values: Vec<f32> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question)
        .map(|entry| entry.data_value)
        .collect();

    if selected_values.is_empty() {
        let mut response: HashMap<&str, Option<()>> = HashMap::new();
        response.insert(&"global_mean", None);

        serde_json::to_string(&response).unwrap()
    } else {
        let sum: f32 = selected_values.iter().sum();
        let global_mean: f32 = sum / selected_values.len() as f32;
        let mut response: HashMap<&str, f32> = HashMap::new();
        response.insert(&"global_mean", global_mean);

        serde_json::to_string(&response).unwrap()
    }
}

pub fn json_response_diff_from_mean(table: &Table, question: &str) -> String {
    let selected_values: Vec<f32> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question)
        .map(|entry| entry.data_value)
        .collect();

    if selected_values.is_empty() {
        let sum: f32 = selected_values.iter().sum();
        let global_mean: f32 = sum / selected_values.len() as f32;
        let mut response: HashMap<&str, f32> = HashMap::new();
        response.insert(&"global_mean", global_mean);

        return serde_json::to_string(&response).unwrap();
    }

    // Using ::<f32> turbofish
    let global_mean: f32 = selected_values.iter().sum::<f32>() / selected_values.len() as f32;

    let states_mean: HashMap<&str, f32> = compute_states_mean(table, question);

    let mut diff_from_mean: HashMap<&str, f32> = HashMap::new();

    for (state, mean) in states_mean.iter() {
        diff_from_mean.insert(&state, global_mean - mean);
    }

    // Operations: HashMap -> Vec -> sort DESC -> HashMap

    // Sort in DESCENDING order
    let mut sorted: Vec<(&str, f32)> = diff_from_mean.into_iter().collect();

    sorted.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

    let diff_from_mean: HashMap<&str, f32> = sorted.into_iter().map(|(k, v)| (k, v)).collect();

    serde_json::to_string(&diff_from_mean).unwrap()
}

fn get_category_priorities<'a>() -> HashMap<&'a str, u32> {
    let mut category_priorities: HashMap<&str, u32> = HashMap::new();
    category_priorities.insert("Age (years)", 1);
    category_priorities.insert("Education", 2);
    category_priorities.insert("Gender", 3);
    category_priorities.insert("Income", 4);
    category_priorities.insert("Race/Ethnicity", 5);
    category_priorities.insert("Total", 6);

    category_priorities
}

fn get_age_priorities<'a>() -> HashMap<&'a str, u32> {
    let mut age_priorities: HashMap<&str, u32> = HashMap::new();
    age_priorities.insert("18 - 24", 1);
    age_priorities.insert("25 - 34", 2);
    age_priorities.insert("35 - 44", 3);
    age_priorities.insert("45 - 54", 4);
    age_priorities.insert("55 - 64", 5);
    age_priorities.insert("65 or older", 6);

    age_priorities
}

fn get_education_priorities<'a>() -> HashMap<&'a str, u32> {
    let mut education_priorities: HashMap<&str, u32> = HashMap::new();
    education_priorities.insert("Less than high school", 1);
    education_priorities.insert("High school graduate", 2);
    education_priorities.insert("Some college or technical school", 3);
    education_priorities.insert("College graduate", 4);

    education_priorities
}

fn get_income_priorities<'a>() -> HashMap<&'a str, u32> {
    let mut income_priorities: HashMap<&str, u32> = HashMap::new();
    income_priorities.insert("Less than $15,000", 1);
    income_priorities.insert("$15,000 - $24,999", 2);
    income_priorities.insert("$25,000 - $34,999", 3);
    income_priorities.insert("$35,000 - $49,999", 4);
    income_priorities.insert("$50,000 - $74,999", 5);
    income_priorities.insert("$75,000 or greater", 6);
    income_priorities.insert("Data not reported", 7);

    income_priorities
}

pub fn json_response_mean_by_catagory(table: &Table, question: &str) -> String {
    let selected_entries: Vec<&TableEntry> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question)
        .collect();

    if selected_entries.is_empty() {
        return serde_json::to_string("").unwrap();
    }

    let mut category_totals: HashMap<(&str, &str, &str), f32> = HashMap::new();
    let mut category_counts: HashMap<(&str, &str, &str), u32> = HashMap::new();

    for entry in selected_entries.iter() {
        if entry.stratification1 == "" || entry.stratification_category1 == "" {
            continue;
        }

        let key: (&str, &str, &str) = (
            &entry.location_desc,
            &entry.stratification_category1,
            &entry.stratification1,
        );

        if let Some(value) = category_totals.get(&key) {
            // HashMap contains key
            category_totals.insert(key.clone(), value + entry.data_value);
        } else {
            // HashMap does NOT contain key
            category_totals.insert(key.clone(), entry.data_value);
        }

        if let Some(value) = category_counts.get(&key) {
            // HashMap contains key
            category_counts.insert(key.clone(), value + 1);
        } else {
            // HashMap does NOT contain key
            category_counts.insert(key.clone(), 1);
        }
    }

    let mut category_means: HashMap<(&str, &str, &str), f32> = HashMap::new();

    for (key, total) in category_totals.iter() {
        category_means.insert(*key, total / *category_counts.get(key).unwrap() as f32);
    }

    let category_priorities: HashMap<&str, u32> = get_category_priorities();
    let age_priorities: HashMap<&str, u32> = get_age_priorities();
    let education_priorities: HashMap<&str, u32> = get_education_priorities();
    let income_priorities: HashMap<&str, u32> = get_income_priorities();

    let mut sorted: Vec<((&str, &str, &str), f32)> = category_means.into_iter().collect();

    // TODO: continue it

    String::new()
}

pub fn json_response_state_mean_by_category(table: &Table, question: &str, state: &str) -> String {
    let selected_entries: Vec<&TableEntry> = table
        .entries
        .iter()
        .filter(|entry| entry.question == question && entry.location_desc == state)
        .collect();

    if selected_entries.is_empty() {
        let mut response: HashMap<&str, &str> = HashMap::new();
        response.insert(
            "error",
            "No data avialable for the given question and state",
        );

        return serde_json::to_string(&response).unwrap();
    }

    let mut category_totals: HashMap<(&str, &str), f32> = HashMap::new();
    let mut category_counts: HashMap<(&str, &str), u32> = HashMap::new();

    for entry in selected_entries {
        let key: (&str, &str) = (&entry.stratification_category1, &entry.stratification1);

        if let Some(value) = category_totals.get(&key) {
            // HashMap contains key
            category_totals.insert(key.clone(), value + entry.data_value);
        } else {
            // HashMap does NOT contain key
            category_totals.insert(key.clone(), entry.data_value);
        }

        if let Some(value) = category_counts.get(&key) {
            // HashMap contains key
            category_counts.insert(key.clone(), value + 1);
        } else {
            // HashMap does NOT contain key
            category_counts.insert(key.clone(), 1);
        }
    }

    let mut category_means: HashMap<(&str, &str), f32> = HashMap::new();
    for (key, total) in category_totals.iter() {
        category_means.insert(*key, total / *category_counts.get(key).unwrap() as f32);
    }

    // TODO: continue

    serde_json::to_string(&category_means).unwrap()
}
