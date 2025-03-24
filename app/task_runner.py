from queue import Queue
from threading import Thread, Event
import time
import os
import json

class ThreadPool:
    def __init__(self):
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        # Note: the TP_NUM_OF_THREADS env var will be defined by the checker


        # If the environment variable is not set (is None),
        # it will take the number of CPU cores
        self.num_threads = os.getenv("TP_NUM_OF_THREADS", os.cpu_count())

        self.job_queue = Queue()
        self.shutdown_event = Event()

        self.job_counter = 1
        self.lock_job_counter = Lock() 

        self.workers = []
        for _ in range(self.num_threads):
            worker = TaskRunner(self.job_queue, self.shutdown_event)
            worker.start()
            self.workers.append(worker)
            
    def add_job(self, job):
        self.job_queue.put(job)

    def shutdown(self):
        self.shutdown_event.set()
        for worker in self.workers:
            worker.join()


class TaskRunner(Thread):
    def __init__(self):
        # TODO: init necessary data structures
        super().__init__()
        self.job_queue = job_queue
        self.shutdown_event = shutdown_event

    def run(self):
        while True:
            # TODO
            # Get pending job
            # Execute the job and save the result to disk
            # Repeat until graceful_shutdown
            try:
                job = self.job_queue.get(timeout=1)
                if job:
                    self.process_job(job)
                    self.job_queue.task_done()
            except Exception as e:
                continue


    def process_job(self, job):
        job_id = job["job_id"]
        result = self.perform_calculation(job)
        self.save_result_to_disk(job_id, result)

    def perform_calculation(self, job):
        return {"job_id": job["job_id"], "result": "some_statistics"}

    def save_result_to_disk(self, job_id, result):
        file_path = os.path.join("results", f"{job_id}.json")
        with open(file_path, "w") as f:
            json.dump(result, f)