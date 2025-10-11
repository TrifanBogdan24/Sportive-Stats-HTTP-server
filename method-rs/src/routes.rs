use std::sync::{Arc, Mutex};

use axum::{
    http::StatusCode, extract::State, response::{self, IntoResponse}, routing::{delete, get, post}, Json, Router
};

use crate::data_ingestor::{
    json_response_best5, json_response_diff_from_mean, json_response_global_mean, json_response_state_mean, json_response_state_mean_by_category, json_response_states_mean, json_response_worst5, load_csv, Table
};

use serde::Deserialize;


#[derive(Deserialize)]
struct QuestionRequest{
    question: String
}


#[derive(Deserialize)]
struct QuestionStateRequest {
    question: String,
    state: String
}

pub fn app() -> Router {
    let table: Table = load_csv("../nutrition_activity_obesity_usa_subset.csv");
    println!("CSV loaded");

    let data = Arc::new(Mutex::new(table));

    Router::new()
        .route("/api/states_mean", post(request_states_mean))
        .route("/api/state_mean", post(request_state_mean))
        .route("/api/best5", post(request_best5))
        .route("/api/worst5", post(request_worst5))
        .route("/api/global_mean", post(request_global_mean))
        .route("/api/diff_from_mean", post(request_diff_from_mean))
        .route("/api/state_mean_by_category", post(request_state_mean_by_category))
        .with_state(data)
}

async fn request_states_mean(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_states_mean(&*table, &payload.question);
    (StatusCode::OK, json)
}


async fn request_state_mean(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionStateRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_state_mean(&*table, &payload.question, &payload.state);
    (StatusCode::OK, json)
}


async fn request_best5(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_best5(&*table, &payload.question);
    (StatusCode::OK, json)
}


async fn request_worst5(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_worst5(&*table, &payload.question);
    (StatusCode::OK, json)
}



async fn request_global_mean(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_global_mean(&*table, &payload.question);
    (StatusCode::OK, json)
}


async fn request_diff_from_mean(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_diff_from_mean(&*table, &payload.question);
    (StatusCode::OK, json)
}

async fn request_state_mean_by_category(
    State(state): State<Arc<Mutex<Table>>>,
    Json(payload): Json<QuestionStateRequest>
) -> impl IntoResponse {
    let table = state.lock().unwrap();
    let json: String = json_response_state_mean_by_category(&*table, &payload.question, &payload.state);
    (StatusCode::OK, json)
}