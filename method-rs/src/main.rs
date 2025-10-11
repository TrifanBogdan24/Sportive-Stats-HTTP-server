mod data_ingestor;
mod routes;

use crate::data_ingestor::{load_csv, Table};
use std::{net::SocketAddr, str::FromStr};
use tokio::net::TcpListener;

use crate::routes::{
    app
};


use axum::{
    extract::State,
    routing::{get, post},
    Router,
    serve
};


#[tokio::main]
async fn main() {


    let app: Router = app();

    let addr = SocketAddr::from_str("0.0.0.0:8000").unwrap();
    let listener = TcpListener::bind(addr).await.unwrap();

    println!("Listening on 0.0.0.0:8000");
    axum::serve(listener, app).await.unwrap();
}
