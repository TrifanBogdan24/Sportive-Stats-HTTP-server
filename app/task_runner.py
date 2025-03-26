from queue import Queue
from threading import Thread, Event, Lock
import time
import os
import json

from enum import Enum
from typing import Dict



class JobType(Enum):
    GET_RESULTS = "/api/get_results"
    STATES_MEAN = "/api/states_mean"
    STATE_MEAN = "/api/state_mean"
    BEST_5 = "/api/best5"
    WORST_5 = "/api/worst5"
    GLOBAL_MEAN = "/api/global_mean"
    DIFF_FROM_MEAN = "/api/diff_from_mean"
    STATE_DIFF_FROM_MEAN = "api/state_diff_from_mean"
    STATE_MEAN_BY_CATEGORY = "api/state_mean_by_category"





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
        self.num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count()))
        
        self.job_queue = Queue()
        self.shutdown_event = Event()
        
        self.lock_job_counter = Lock()
        
        self.workers = []

        for _ in range(self.num_threads):
            worker = TaskRunner(self.job_queue, self.shutdown_event)
            worker.start()
            self.workers.append(worker)

    def add_job(self, job_type: JobType, request_data: Dict):
        from app import webserver

        with self.lock_job_counter:
            job_id = webserver.job_counter
            webserver.job_counter += 1

        # Creeare unui JOB nou
        job = {"job_id": job_id, "job_type": job_type, "request_data": request_data}
        self.job_queue.put(job)

        # Scrierea JOB-ului pe disc
        with open(os.path.join("results", f"{job_id}.json"), "w") as f:
            json.dump({"status": "running"}, f)

        return job_id

    def shutdown(self):
        self.shutdown_event.set()
        for worker in self.workers:
            worker.join()


class TaskRunner(Thread):
    def __init__(self, job_queue, shutdown_event):
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
                    self._process_job(job)
                    self.job_queue.task_done()
            except Exception as e:
                continue


    def _process_job(self, job):
        from app import webserver
        

        job_id: int = job["job_id"]
        job_type: JobType = job["job_type"]
        request_data: str = job["request_data"]
        response_data: str = ""


        if job_type == JobType.STATES_MEAN:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_states_mean(question)
        elif job_type == JobType.STATE_MEAN:
            question: str = request_data.get("question", "")
            state: str = request_data.get("state", "")
            response_data = webserver.data_ingestor.compute_response_state_mean(question, state)
        elif job_type == JobType.BEST_5:
            question: str = request_data.get("question", "")
            # TODO: compute response
        elif job_type == JobType.GLOBAL_MEAN:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_global_mean(question)
        elif job_type == JobType.DIFF_FROM_MEAN:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_diff_from_mean(question)
        elif job_type == JobType.STATE_DIFF_FROM_MEAN:
            question: str = request_data.get("question", "")
            state: str = request_data.get("state", "")
            response_data = webserver.data_ingestor.compute_response_state_diff_from_mean(question, state)       





        # Save results to disk
        with open(os.path.join("results", f"{job_id}.json"), "w") as f:
            json.dump({"status": "done", "data": response_data}, f)





if __name__ == '__main__':
    """For test purposes only"""
    tasks_runner = ThreadPool()