use std::sync::{Arc, Mutex, Condvar};
use std::thread;
use std::collections::VecDeque;
use std::env;

type Job = Box<dyn FnOnce() + Send + 'static>;

pub struct ThreadPool {
    workers: Vec<TaskRunner>,
    queue: Arc<(Mutex<VecDeque<Job>>, Condvar)>,
    shutdown: Arc<Mutex<bool>>,
}

impl ThreadPool {
    pub fn new() -> Self {
        let num_threads: usize = match env::var("TP_NUM_OF_THREADS") {
            Ok(value) => match value.parse::<usize>() {
                Ok(num_threads) => num_threads,
                _ => num_cpus::get(), // fallback dacă parse e invalid
            },
            _ => num_cpus::get(), // fallback dacă variabila de mediu nu există
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
        ThreadPool { workers, queue, shutdown }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let (lock, cvar) = &*self.queue;
        let mut q = lock.lock().unwrap();
        q.push_back(Box::new(f));
        cvar.notify_one(); // trezește un worker
    }

    /// Trimite semnalul de închidere; pool-ul va rula toate job-urile existente înainte de a se închide
    pub fn shutdown(&self) {
        let mut flag = self.shutdown.lock().unwrap();
        *flag = true;
        self.queue.1.notify_all(); // trezește toți workerii
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
                    let (lock, cvar) = &*queue;
                    let mut q = lock.lock().unwrap();

                    // Așteaptă job dacă coada e goală
                    while q.is_empty() && !*shutdown.lock().unwrap() {
                        q = cvar.wait(q).unwrap();
                    }

                    // Dacă coada e goală și shutdown este true, ieșim
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
