use std::sync::{Arc, Mutex, Condvar};
use std::sync::atomic::{AtomicU32, Ordering};
use std::thread;
use std::collections::VecDeque;
use std::env;

use crate::request_type::RequestType;


use crate::data_ingestor::{
    json_response_best5, json_response_diff_from_mean, json_response_global_mean, json_response_mean_by_catagory, json_response_state_mean, json_response_state_mean_by_category, json_response_states_mean, json_response_worst5, load_csv, Table
};
use crate::routes::{QuestionRequest, QuestionStateRequest};

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    table: Mutex<Table>,
    workers: Vec<TaskRunner>,
    queue: Arc<(Mutex<VecDeque<Job>>, Condvar)>,
    shutdown: Arc<Mutex<bool>>,
}

impl ThreadPool {
    /// Create a new ThreadPool
    pub fn new(table: Table) -> Self {
        

        let num_threads: usize = match env::var("TP_NUM_OF_THREADS") {
            Ok(value) => match value.parse::<usize>() {
                Ok(num_threads) => num_threads,
                _ => num_cpus::get(),
            },
            _ => num_cpus::get(),
        };
        
        let queue = Arc::new((Mutex::new(VecDeque::new()), Condvar::new()));
        let shutdown = Arc::new(Mutex::new(false));
        let mut workers = Vec::with_capacity(num_threads);

        for id in 0..num_threads {
            workers.push(TaskRunner::new(
                id,
                Arc::clone(&queue),
                Arc::clone(&shutdown),
            ));
        }


        println!("Starting thread pool with {} runners", num_threads);
        ThreadPool {
            table: Mutex::new(table),
            workers,
            queue,
            shutdown
        }
    }

    /// Submit a new task to the pool
    pub fn execute<F>(&self, func: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let (lock, cond_var) = &*self.queue;
        let mut queue = lock.lock().unwrap();
        queue.push_back(Box::new(func));
        // Wake up an worker:
        cond_var.notify_one();
    }

    /// Send shutdown signal: Thread Pool will run all remaining jobs (after which Thread Pool stops)
    pub fn shutdown(&self) {
        let mut flag = self.shutdown.lock().unwrap();
        *flag = true;
        // Wake up all workers:
        self.queue.1.notify_all();
    }

}


pub struct TaskRunner {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl TaskRunner {
    fn new(id: usize, queue: Arc<(Mutex<VecDeque<Job>>, Condvar)>, shutdown: Arc<Mutex<bool>>) -> Self {
        let thread = thread::spawn(move || {
            loop {
                let job_opt = {
                    let (lock, cond_var) = &*queue;
                    let mut q = lock.lock().unwrap();

                    // Wait for a job if queue is empty
                    while q.is_empty() && !*shutdown.lock().unwrap() {
                        q = cond_var.wait(q).unwrap();
                    }

                    // If queue is empty and received shutdown -> stop the worker
                    if q.is_empty() && *shutdown.lock().unwrap() {
                        break;
                    }

                    q.pop_front()
                };

                if let Some(job) = job_opt {
                    println!("Worker {} executing job...", id);
                    job();
                }
            }

            println!("Worker {} shutting down.", id);
        });

        TaskRunner { id, thread: Some(thread) }
    }
}



pub struct JobManager {
    next_id: Arc<AtomicU32>,
    thread_pool: Arc<ThreadPool>,
}


impl JobManager {
    pub fn new(thread_pool: Arc<ThreadPool>) -> Self {
        Self {
            next_id: Arc::new(AtomicU32::new(1)),
            thread_pool,
        }
    }

    pub fn add_job(&self, request_type: RequestType, json_request: &str) -> u32 {
        // Generate unique job ID
        let job_id = self.next_id.fetch_add(1, Ordering::SeqCst);

        // Clone anything needed for the async closure
        let req_type = request_type.clone();
        let req_data = json_request.to_string();


        let thread_pool = Arc::clone(&self.thread_pool);

        self.thread_pool.execute(move || {
            println!("[Job #{job_id}] Starting : {:}", request_type.as_str());
            
            match request_type {
                RequestType::STATES_MEAN => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_states_mean(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::STATE_MEAN => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionStateRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_state_mean(&table, &query.question, &query.state);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::BEST_5 => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_best5(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::WORST_5 => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_worst5(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::GLOBAL_MEAN => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_global_mean(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::DIFF_FROM_MEAN => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_diff_from_mean(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::MEAN_BY_CATEGORY => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_mean_by_catagory(&table, &query.question);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },
                RequestType::STATE_MEAN_BY_CATEGORY => {
                    let table = thread_pool.table.lock().unwrap();
                    let query: QuestionStateRequest = serde_json::from_str(&req_data).unwrap();
                    let json_response = json_response_state_mean_by_category(&table, &query.question, &query.state);

                    // TODO: write in results/<job_id>.json and log time
                    println!("{:}", json_response);
                },

                _ => ()
            }

            println!("[Job #{job_id}] Finished");
        });

        job_id
    }
}