mod data_ingestor;
mod routes;
mod request_type;
mod thread_pool;
mod logger;

use std::{net::SocketAddr, str::FromStr};
use tokio::net::TcpListener;

use std::sync::Arc;

use axum::{
    extract::State, http, routing::{get, post}, serve, Router
};

use crate::routes::http_server;
use crate::data_ingestor::{load_csv, Table};

use crate::thread_pool::ThreadPool;


#[tokio::main]
async fn main() {
    let server: Router = http_server();
    let addr = SocketAddr::from_str("0.0.0.0:8000").unwrap();
    let listener = TcpListener::bind(addr).await.unwrap();
    println!("Listening on 0.0.0.0:8000");

    axum::serve(listener, server).await.unwrap();
}
