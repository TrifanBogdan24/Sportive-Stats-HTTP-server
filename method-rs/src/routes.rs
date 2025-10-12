use std::sync::{Arc, Mutex};
use std::net::SocketAddr;

use axum::{
    extract::{Request, State, ConnectInfo}, http::StatusCode,  response::{self, IntoResponse}, routing::{get, post}, Json, Router
};

use serde::{Deserialize, Serialize};


use crate::logger::{print_log, LogType};
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
    let app_state = AppState { jobs };
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


pub fn log_received_request(request_type: RequestType, addr: &SocketAddr) {
    print_log(
        LogType::Info,
        &format!("Received {:?} request from {}", request_type.as_str(), addr.ip())
    );
}


pub fn log_added_job_in_thread_pool(request_type: RequestType, addr: &SocketAddr, job_id: u32, json_request: &str) {
    print_log(
        LogType::Info,
        &format!("Added job in Thread Pool for {:?} request coming from from {}\n\
        \t- Created job_id={}\n\
        \t- Requested_data: {:}",
        request_type.as_str(),
        addr.ip(),
        job_id,
        json_request
    ));
}


async fn request_states_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::STATES_MEAN, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::STATES_MEAN,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::STATES_MEAN,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}


async fn request_state_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::STATE_MEAN, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();
    
    let job_id: u32 = state.jobs.add_job(
        RequestType::STATE_MEAN,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::STATE_MEAN,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_best5(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::BEST_5, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::BEST_5,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::BEST_5,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_worst5(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::WORST_5, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::WORST_5,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::WORST_5,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_global_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::GLOBAL_MEAN, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::GLOBAL_MEAN,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::GLOBAL_MEAN,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_diff_from_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::DIFF_FROM_MEAN, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::DIFF_FROM_MEAN,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::DIFF_FROM_MEAN,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}

async fn request_state_mean_by_category(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::MEAN_BY_CATEGORY, &addr);
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(
        RequestType::MEAN_BY_CATEGORY,
        &json_request
    );

    log_added_job_in_thread_pool(
        RequestType::MEAN_BY_CATEGORY,
        &addr,
        job_id,
        &json_request
    );

    let response = JobResponse { job_id };
    (StatusCode::OK, Json(response))
}
