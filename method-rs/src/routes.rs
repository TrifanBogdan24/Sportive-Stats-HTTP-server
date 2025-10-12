use std::sync::{Arc, Mutex};

use axum::{
    Json, Router,
    extract::State,
    http::StatusCode,
    response::{self, IntoResponse},
    routing::{get, post},
};

use serde::{Deserialize, Serialize};


use crate::thread_pool;

use crate::thread_pool::{ThreadPool, JobManager};

use crate::request_type::RequestType;


#[derive(Serialize, Deserialize)]
pub struct QuestionRequest {
    pub question: String,
}

#[derive(Serialize, Deserialize)]
pub struct QuestionStateRequest {
    pub question: String,
    pub state: String,
}


#[derive(Serialize)]
struct JobResponse {
    job_id: u32,
}

struct AppState {
    jobs: JobManager
}

pub fn http_server(jobs: JobManager) -> Router {
    let app_state = AppState {
        jobs
    };

    let state: Arc<AppState> = Arc::new(app_state);

    Router::new()
        .route("/api/states_mean", post(request_states_mean))
        .route("/api/state_mean", post(request_state_mean))
        .route("/api/best5", post(request_best5))
        .route("/api/worst5", post(request_worst5))
        .route("/api/global_mean", post(request_global_mean))
        .route("/api/diff_from_mean", post(request_diff_from_mean))
        .route("/api/state_mean_by_category", post(request_state_mean_by_category))
        .with_state(state)
}

async fn request_states_mean(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::STATES_MEAN,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_state_mean(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::STATE_MEAN,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_best5(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::BEST_5,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_worst5(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::WORST_5,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_global_mean(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::GLOBAL_MEAN,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_diff_from_mean(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::DIFF_FROM_MEAN,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_state_mean_by_category(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    let job_id: u32 = state.jobs.add_job(
        RequestType::MEAN_BY_CATEGORY,
        &serde_json::to_string(&payload).unwrap()
    );
    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}
