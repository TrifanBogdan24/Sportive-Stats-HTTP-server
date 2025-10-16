use std::collections::VecDeque;
use std::env;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use serde::Serialize;
use std::collections::HashMap;

use crate::request_type::RequestType;

use crate::data_ingestor::{
    Table, json_response_best5, json_response_diff_from_mean, json_response_global_mean,
    json_response_mean_by_catagory, json_response_state_mean, json_response_state_mean_by_category,
    json_response_states_mean, json_response_worst5,
};
use crate::routes::{QuestionRequest, QuestionStateRequest};

use crate::concurrent_hash_map::ConcurrentHashMap;

use crate::logger::{LogType, print_log};

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    table: Mutex<Table>,
    workers: Vec<TaskRunner>,
    queue: Arc<(Mutex<VecDeque<Job>>, Condvar)>,
    shutdown: Arc<Mutex<bool>>,
    file_locks: ConcurrentHashMap<u32, Arc<Mutex<File>>>,
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

        // Create a lock on ./results/<job_id>.json file for each new job
        // and delete it after the result is computed
        let file_locks: ConcurrentHashMap<u32, Arc<Mutex<File>>> = ConcurrentHashMap::new();

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

        print_log(
            LogType::Info,
            &format!("Starting thread pool with {} runners", num_threads),
        );

        ThreadPool {
            table: Mutex::new(table),
            workers,
            queue,
            shutdown,
            file_locks,
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
    fn new(
        id: usize,
        queue: Arc<(Mutex<VecDeque<Job>>, Condvar)>,
        shutdown: Arc<Mutex<bool>>,
    ) -> Self {
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
                    // Worker <id> executing job
                    job();
                }
            }

            // Worker <id> is shutting down
        });

        TaskRunner {
            id,
            thread: Some(thread),
        }
    }
}

#[derive(Clone, Copy, Serialize)]
pub enum JobStatus {
    Running,
    Done,
}

pub struct JobManager {
    next_id: Arc<AtomicU32>,
    thread_pool: Arc<ThreadPool>,
    statuses: Arc<Mutex<HashMap<u32, JobStatus>>>,
}





impl JobManager {
    pub fn new(thread_pool: Arc<ThreadPool>) -> Self {
        Self {
            next_id: Arc::new(AtomicU32::new(1)),
            thread_pool,
            statuses: Arc::new(Mutex::new(HashMap::new()))
        }
    }

    pub fn shutdown_thred_pool(&self) {
        self.thread_pool.shutdown();
    }

    pub fn get_jobs_status_snapshot(&self) -> HashMap<u32, JobStatus> {
        self.statuses.lock().unwrap().clone()
    }

    pub fn count_pending(&self) -> usize {
        self.statuses.lock().unwrap()
            .values()
            .filter(|&&s| matches!(s, JobStatus::Running))
            .count()
    }

    pub fn add_job(&self, request_type: RequestType, json_request: &str) -> u32 {
        let job_id = self.next_id.fetch_add(1, Ordering::SeqCst);
       
       // Clone data (to be used in closure)
        let req_data = json_request.to_string();
        let thread_pool = Arc::clone(&self.thread_pool);
        let statuses = Arc::clone(&self.statuses);

        self.thread_pool.execute(move || {
            JobManager::run_job(thread_pool, job_id, request_type, req_data);
            statuses.lock().unwrap().insert(job_id, JobStatus::Done);
        });

        job_id
    }

    fn run_job(thread_pool: Arc<ThreadPool>, job_id: u32, request_type: RequestType, req_data: String) {
        // Create and lock the file
        let path = format!("./results/{}.json", job_id);
        if let Some(parent) = std::path::Path::new(&path).parent() {
            if let Err(e) = std::fs::create_dir_all(parent) {
                print_log(LogType::Error, &format!("Failed to create results dir: {}", e));
                return;
            }
        }

        let file = match File::create(&path) {
            Ok(f) => f,
            Err(e) => {
                print_log(LogType::Error, &format!("Failed to create file {}: {}", path, e));
                return;
            }
        };

        let file_lock = Arc::new(Mutex::new(file));
        thread_pool.file_locks.insert(job_id, Arc::clone(&file_lock));

        // Run the job logic
        JobManager::handle_request_type(&thread_pool, job_id, request_type, &req_data, &file_lock);

        // Remove file lock entry (file stays on disk)
        thread_pool.file_locks.delete(&job_id);
        print_log(LogType::Info, &format!("File lock for job_id={} removed", job_id));
    }

    fn handle_request_type(
        thread_pool: &Arc<ThreadPool>,
        job_id: u32,
        request_type: RequestType,
        req_data: &str,
        file_lock: &Arc<Mutex<File>>,
    ) {
        let json_response = match request_type {
            RequestType::STATES_MEAN => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_states_mean(&table, &query.question)
            }
            RequestType::STATE_MEAN => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionStateRequest = serde_json::from_str(req_data).unwrap();
                json_response_state_mean(&table, &query.question, &query.state)
            }
            RequestType::BEST_5 => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_best5(&table, &query.question)
            }
            RequestType::WORST_5 => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_worst5(&table, &query.question)
            }
            RequestType::GLOBAL_MEAN => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_global_mean(&table, &query.question)
            }
            RequestType::DIFF_FROM_MEAN => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_diff_from_mean(&table, &query.question)
            }
            RequestType::MEAN_BY_CATEGORY => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionRequest = serde_json::from_str(req_data).unwrap();
                json_response_mean_by_catagory(&table, &query.question)
            }
            RequestType::STATE_MEAN_BY_CATEGORY => {
                let table = thread_pool.table.lock().unwrap();
                let query: QuestionStateRequest = serde_json::from_str(req_data).unwrap();
                json_response_state_mean_by_category(&table, &query.question, &query.state)
            }
            _ => {
                print_log(LogType::Error, &format!("Unhandled request type for job_id={}", job_id));
                return;
            }
        };

        // Write response in .json file under the lock
        JobManager::write_result_to_file(file_lock, job_id, &json_response);

        print_log(
            LogType::Info,
            &format!(
                "Response for job_id={} was computed and saved to ./results/{}.json",
                job_id, job_id
            ),
        );
    }

    fn write_result_to_file(file_lock: &Arc<Mutex<File>>, job_id: u32, data: &str) {
        match file_lock.lock() {
            Ok(mut file_guard) => {
                if let Err(e) = writeln!(file_guard, "{}", data) {
                    print_log(LogType::Error, &format!("Failed to write job {}: {}", job_id, e));
                }
            }
            Err(_) => {
                print_log(LogType::Error, &format!("Poisoned file lock for job {}", job_id));
            }
        }
    }
}
