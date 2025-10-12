mod data_ingestor;
mod routes;
mod request_type;
mod thread_pool;
mod logger;

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
    println!("Loaded CSV");

    let thread_pool = ThreadPool::new(table);
    let jobs = JobManager::new(Arc::new(thread_pool).clone());

    let server: Router = http_server(jobs);
    let addr = SocketAddr::from_str("0.0.0.0:8000").unwrap();
    let listener = TcpListener::bind(addr).await.unwrap();
    println!("Listening on 0.0.0.0:8000");



    axum::serve(listener, server).await.unwrap();
}
