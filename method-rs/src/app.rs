mod data_ingestor;
mod routes;
mod request_type;
mod thread_pool;
mod logger;
mod concurrent_hash_map;


use std::{net::SocketAddr, str::FromStr, fs};
use tokio::net::TcpListener;

use std::path::Path;

use std::sync::Arc;

use axum::{
    extract::State, http, routing::{get, post}, serve, Router
};

use crate::routes::http_server;
use crate::data_ingestor::{load_csv, Table};

use crate::thread_pool::{ThreadPool, JobManager};

use crate::logger::{LogType, print_log};


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

    print_log(LogType::Info, "Axum HTTP server is listening on 0.0.0.0:8000");
    axum::serve(
        tokio::net::TcpListener::bind(addr).await.unwrap(),
        server.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .unwrap();

}
