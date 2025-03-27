from queue import Queue
from threading import Thread, Event, Lock
from flask import jsonify
import time
import os
from sys import exit
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
    MEAN_BY_CATEGORY = "api/mean_by_category"
    STATE_MEAN_BY_CATEGORY = "api/state_mean_by_category"

class ThreadPool:
    def __init__(self):
        from app import webserver

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
        self.lock_logger = Lock()

        self.workers = []

        self.types_processing_jobs = []

        for _ in range(self.num_threads):
            worker = TaskRunner(self.job_queue, self.shutdown_event)
            worker.start()
            self.workers.append(worker)

        webserver.logger.log_message(f" - INFO - Server started with {self.num_threads} threads")
        

    def add_job(self, job_type: JobType, request_data: Dict):
        from app import webserver


        # Get job_id and increment JOB counter
        with self.lock_job_counter:
            job_id = webserver.job_counter
            webserver.job_counter += 1

        # Write in .log file
        message = f"- INFO - Received request: job_id={job_id}, job_type={job_type.value}, request_data={request_data}"
        webserver.logger.log_message(message)

        # Create new JOB
        job = {"job_id": job_id, "job_type": job_type, "request_data": request_data}
        self.job_queue.put(job)

        # Write JOB's result on disk
        with open(os.path.join("results", f"{job_id}.json"), "w") as file:
            json.dump({"status": "running"}, file)

        return job_id


    def get_job_result(self, job_id: int):
        from app import webserver

        num_jobs = 0
        with self.lock_job_counter:
            num_jobs = webserver.job_counter - 1

        if job_id < 1 or job_id > num_jobs:
            # Bad Request status code
            message = f"- ERROR - Invalid job_id \'{job_id}\'! It is outside of range."
            webserver.logger.log_message(message)
            return jsonify({"status": "error", "reason": "Invalid job_id"}), 400
        

        file_path = f"results/{job_id}.json"
        
        if not os.path.exists(file_path):
            # Not Found status code
            message = f"- ERROR - Result file for job_id='{job_id}', expected to be at {file_path}, DOES NOT EXIST"
            webserver.logger.log_message(message)
            return jsonify({"status": "error", "reason": "Invalid job_id"}), 500
        
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            # Successful response with 200 OK status
            return jsonify(data), 200
        except Exception as e:
            # Internal Server Error status code
            message = f"- ERROR - Failed to read data for job_id='{job_id}'"
            webserver.logger.log_message(message)
            return jsonify({"status": "error", "reason": "Invalid job_id"}), 500
        
    def graceful_shutdown(self):
        from app import webserver

        message = f"- INFO - Received '/api/graceful_shutdown' request"
        webserver.logger.log_message(message)

        with webserver.lock_is_shutting_down:
            if webserver.is_shutting_down:
                return
            webserver.is_shutting_down = True

        message = f"- INFO - Number of workers thread to join = {len(self.workers)}"
        webserver.logger.log_message(message)

        self.shutdown_event.set()  # Signal all workers to stop

        # Add None to the queue for each worker (to unblock them)
        for _ in range(len(self.workers)):
            self.job_queue.put(None)


        # Wait for all workers to exit
        for tid, worker in enumerate(self.workers):
            message = f"- INFO - Joining thread TID={tid}"
            webserver.logger.log_message(message)
            worker.join()  # Make sure every thread finishes

        message = f"- INFO - Server stopped"
        webserver.logger.log_message(message)



class TaskRunner(Thread):
    def __init__(self, job_queue, shutdown_event):
        super().__init__()
        self.job_queue = job_queue
        self.shutdown_event = shutdown_event

    def run(self):
        while not self.shutdown_event.is_set():  # Check if shutdown event is set
            try:
                job = self.job_queue.get(timeout=1)  # Wait for 1 second for a job
                if job is None:  # None indicates shutdown request
                    break  # Break the loop and terminate the worker
                self._process_job(job)
                self.job_queue.task_done()
            except Exception as e:
                # Handle any exceptions and retry getting jobs
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
            response_data = webserver.data_ingestor.compute_response_best5(question)
        elif job_type == JobType.WORST_5:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_worst5(question)
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
        elif job_type == JobType.MEAN_BY_CATEGORY:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_mean_by_category(question)

        # Save JOB's results to disk
        with open(os.path.join("results", f"{job_id}.json"), "w") as f:
            json.dump({"status": "done", "data": response_data}, f)

        # Write in .log file
        message = f"- INFO - Computed response for job_id={job_id} can be found at 'results/{job_id}.json'"
        webserver.logger.log_message(message)

if __name__ == '__main__':
    """For test purposes only"""
    tasks_runner = ThreadPool()
