use std::net::SocketAddr;
use std::os::linux::raw::stat;
use std::sync::{Arc, Mutex};

use axum::extract::Path;
use axum::{
    Json, Router,
    extract::{ConnectInfo, Request, State},
    http::StatusCode,
    response::{self, IntoResponse},
    routing::{get, post},
};

use serde::{Deserialize, Serialize};

use crate::logger::{LogType, print_log};
use crate::thread_pool;

use crate::thread_pool::{JobManager, JobStatus, ThreadPool};

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


struct AppState {
    jobs: JobManager,
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
        .route(
            "/api/state_mean_by_category",
            post(request_state_mean_by_category),
        )
        .route("/api/graceful_shutdown", get(graceful_shutdown))
        .route("/api/jobs", get(get_jobs_status))
        .route("/api/num_jobs", get(get_num_pending_jobs))
        .route("/api/get_results/{job_id}", get(get_job_result))
        .with_state(state)
}


fn responde_with_server_shutdown_error() -> (StatusCode, Json<serde_json::Value>) {
    let response = serde_json::json!({
        "status": "error",
        "reason": "server is already shut down"
    });
    (StatusCode::METHOD_NOT_ALLOWED, Json(response))
}

pub fn log_received_request(request_name: &str, addr: &SocketAddr) {
    print_log(
        LogType::Info,
        &format!(
            "Received {:?} request from {}",
            request_name,
            addr.ip()
        ),
    );
}

pub fn log_added_job_in_thread_pool(
    request_type: RequestType,
    addr: &SocketAddr,
    job_id: u32,
    json_request: &str,
) {
    print_log(
        LogType::Info,
        &format!(
            "Added job in Thread Pool for {:?} request coming from from {}\n\
        \t- Created job_id={}\n\
        \t- Requested_data: {:}",
            request_type.as_str(),
            addr.ip(),
            job_id,
            json_request
        ),
    );
}

async fn request_states_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::STATES_MEAN.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(RequestType::STATES_MEAN, &json_request);

    log_added_job_in_thread_pool(RequestType::STATES_MEAN, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}

async fn request_state_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::STATE_MEAN.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(RequestType::STATE_MEAN, &json_request);

    log_added_job_in_thread_pool(RequestType::STATE_MEAN, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}

async fn request_best5(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::BEST_5.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(RequestType::BEST_5, &json_request);

    log_added_job_in_thread_pool(RequestType::BEST_5, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}

async fn request_worst5(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(RequestType::WORST_5.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(RequestType::WORST_5, &json_request);

    log_added_job_in_thread_pool(RequestType::WORST_5, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}

async fn request_global_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(&RequestType::GLOBAL_MEAN.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state.jobs.add_job(RequestType::GLOBAL_MEAN, &json_request);

    log_added_job_in_thread_pool(RequestType::GLOBAL_MEAN, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}



async fn request_diff_from_mean(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionRequest>,
) -> impl IntoResponse {
    log_received_request(&RequestType::DIFF_FROM_MEAN.as_str(), &addr);
    
    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }
    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state
        .jobs
        .add_job(RequestType::DIFF_FROM_MEAN, &json_request);

    log_added_job_in_thread_pool(RequestType::DIFF_FROM_MEAN, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}

async fn request_state_mean_by_category(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
    Json(payload): Json<QuestionStateRequest>,
) -> impl IntoResponse {
    log_received_request(&RequestType::MEAN_BY_CATEGORY.as_str(), &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    let json_request = serde_json::to_string(&payload).unwrap();

    let job_id: u32 = state
        .jobs
        .add_job(RequestType::MEAN_BY_CATEGORY, &json_request);

    log_added_job_in_thread_pool(RequestType::MEAN_BY_CATEGORY, &addr, job_id, &json_request);

    let response = serde_json::json!({
        "job_id": job_id
    });
    (StatusCode::OK, Json(response))
}



async fn graceful_shutdown(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
) -> impl IntoResponse {
    // TODO
    log_received_request("GET /api/graceful_shutdown", &addr);

    if state.jobs.is_thread_pool_shut_down() {
        return responde_with_server_shutdown_error();
    }

    state.jobs.shutdown_thread_pool();

    // Verifica daca mai sunt joburi active
    let pending = state.jobs.count_pending();

    let response = if pending > 0 {
        serde_json::json!({
            "status": "running"
        })
    } else {
        serde_json::json!({
            "status": "done"
        })
    };

    (StatusCode::OK, Json(response))
}


async fn get_jobs_status(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
) -> impl IntoResponse {
    // TODO
    log_received_request("GET /api/jobs", &addr);

    let statuses = state.jobs.get_jobs_status_snapshot();
    let mut data = Vec::new();
    for (id, status) in statuses.iter() {
        let status_str = match status {
            JobStatus::Running => "running",
            JobStatus::Done => "done",
        };
        data.push(serde_json::json!({ id.to_string(): status_str }));
    }

    let response = serde_json::json!({
        "status": "done",
        "data": data
    });

    (StatusCode::OK, Json(response))
}

#[derive(Serialize)]
struct NumJobsResponse {
    pending: usize,
}

async fn get_num_pending_jobs(
    State(state): State<Arc<AppState>>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
) -> impl IntoResponse {
    // TODO
    log_received_request("GET /api/num_jobs", &addr);

    let pending = state.jobs.count_pending();
    let response = NumJobsResponse { pending };
    (StatusCode::OK, Json(response))
}



async fn get_job_result(
    State(state): State<Arc<AppState>>,
    Path(job_id): Path<u32>,
    ConnectInfo(addr): ConnectInfo<SocketAddr>,
) -> impl IntoResponse {
    // TODO
    log_received_request(&format!("GET /api/get_results/{}", job_id), &addr);

    let statuses = state.jobs.get_jobs_status_snapshot();

    match statuses.get(&job_id) {
        None => {
            let response = serde_json::json!({
                "status": "error",
                "reason": "Invalid job_id"
            });
            (StatusCode::OK, Json(response))
        }
        Some(JobStatus::Running) => {
            let response = serde_json::json!({
                "status": "running"
            });
            (StatusCode::OK, Json(response))
        }
        Some(JobStatus::Done) => {
            let path = format!("./results/{}.json", job_id);
            match std::fs::read_to_string(&path) {
                Ok(content) => {
                    let json_value: serde_json::Value =
                        serde_json::from_str(&content).unwrap_or(serde_json::json!({ "raw": content }));
                    let response = serde_json::json!({
                        "status": "done",
                        "data": json_value
                    });
                    (StatusCode::OK, Json(response))
                }
                Err(_) => {
                    let response = serde_json::json!({
                        "status": "error",
                        "reason": "Result file is missing"
                    });
                    (StatusCode::OK, Json(response))
                }
            }
        }
    }
}
