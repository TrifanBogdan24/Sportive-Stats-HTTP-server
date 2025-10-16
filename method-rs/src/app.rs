mod concurrent_hash_map;
mod data_ingestor;
mod logger;
mod request_type;
mod routes;
mod thread_pool;

use std::{fs, net::SocketAddr, str::FromStr};
use tokio::net::TcpListener;

use std::path::Path;

use std::sync::{Arc, Mutex};

use axum::{
    Router,
    extract::State,
    http,
    routing::{get, post},
    serve,
};

use crate::data_ingestor::{Table, load_csv};
use crate::routes::http_server;

use crate::thread_pool::{JobManager, ThreadPool};

use crate::logger::{LogType, print_log};

use crate::concurrent_hash_map::ConcurrentHashMap;

fn prep_results_dir() {
    if Path::new("./results").exists() {
        if Path::new("./results").is_dir() {
            fs::remove_dir_all("./results").unwrap();
        } else {
            fs::remove_file("./results").unwrap();
        }
    }
    fs::create_dir("./results").unwrap();
}

#[tokio::main]
async fn main() {
    prep_results_dir();

    let table: Table = load_csv("../nutrition_activity_obesity_usa_subset.csv");

    print_log(LogType::Info, "Loaded relevant columns from CSV in memory");

    let thread_pool = ThreadPool::new(table);
    let jobs = JobManager::new(Arc::new(thread_pool).clone());

    let server: Router = http_server(jobs);
    let addr = SocketAddr::from_str("0.0.0.0:8000").unwrap();

    print_log(
        LogType::Info,
        "Axum HTTP server is listening on 0.0.0.0:8000",
    );
    axum::serve(
        tokio::net::TcpListener::bind(addr).await.unwrap(),
        server.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .unwrap();
}
