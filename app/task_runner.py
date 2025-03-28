from queue import Queue
from threading import Thread, Event, Lock
import os
import json

from enum import Enum
from typing import Dict

from flask import jsonify


class JobType(Enum):
    """
    Enumeration class for classifying the HTTP requests that require data processing.
    Each enum member corresponds to a specific API endpoint.
    """
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
    """
    The implementation for the Replicated Workers design pattern.
    Used for concurrently processing server's HTTP requests.

    It contains two major components:
    - A pool of tasks: represented by a Queue
    - A group of workers (threads)
    """
    
    def __init__(self):
        """
        Set up the Thread Pool:
        - Create synchronization variables
        - Create threads: the number of workers if either based
            - on an environment variable
            - if the variable was not set, on the number of CPU cores
        - Start the threads
        """
        from app import webserver

        # If the environment variable TP_NUM_OF_THREADS is not set (is None),
        # the number of created threads will equal the number of CPU cores
        self.num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count()))


        self.job_queue = Queue()
        self.shutdown_event = Event()

        self.lock_job_counter = Lock()
        self.lock_logger = Lock()

        self.lock_file_data_base = Lock()
        self.pending_job_locks = {}

        self.workers = []

        self.types_processing_jobs = []

        for _ in range(self.num_threads):
            worker = TaskRunner(self.job_queue, self.shutdown_event)
            worker.start()
            self.workers.append(worker)

        webserver.logger.log_message(f" - INFO - Server started with {self.num_threads} threads")


    def add_job(self, job_type: JobType, request_data: Dict):
        """Inserts the job in the server's Queue"""
        from app import webserver


        # Get job_id and increment JOB counter
        with self.lock_job_counter:
            job_id = webserver.job_counter
            webserver.job_counter += 1

        # Write in .log file
        message = (
            "- INFO - Received request: job_id={job_id}, ",
            f"job_type={job_type.value}, ",
            f"request_data={request_data}"
        )
        webserver.logger.log_message(message)

        # Create new JOB
        job = {"job_id": job_id, "job_type": job_type, "request_data": request_data}
        self.job_queue.put(job)

        # Add a lock on the job's file
        with self.lock_file_data_base:
            self.pending_job_locks[job_id] = Lock()

        # Write JOB's result on disk
        with self.pending_job_locks[job_id]:
            with open(os.path.join("results", f"{job_id}.json"), "w", encoding="utf-8") as file:
                json.dump({"status": "running"}, file)

        return job_id


    def get_job_result(self, job_id: int):
        """
        Returns the JSON response for 'GET /api/get_results/<job_id>' request
        by reading job's data from the disk
        """
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
            message = (
                f"- ERROR - Result file for job_id='{job_id}', ",
                f"expected to be at {file_path}, DOES NOT EXIST"
            )
            webserver.logger.log_message(message)
            return jsonify({"status": "error", "reason": "Invalid job_id"}), 500

        with webserver.tasks_runner.lock_file_data_base:
            # Equivalent to a ternary if-else
            is_job_running: bool = job_id in webserver.tasks_runner.pending_job_locks


        if is_job_running is True:
            return jsonify({"status": "running"}), 200

        # JOB's result was already compute and is thread-safe to access it
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                result = json.load(file)
            return jsonify(result), 200
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            # Internal Server Error status code
            message = f"- ERROR - Failed to read data for job_id='{job_id}'"
            webserver.logger.log_message(message)
            return jsonify({"status": "error", "reason": "Invalid job_id"}), 500

    def get_num_pending_jobs(self):
        """Returns queue's size (the number of jobs that haven't been processed yet)"""
        with self.lock_job_counter:
            return self.job_queue.qsize()

    def graceful_shutdown(self):
        """
        Waits for all workers to finish their tasks
        and stops them
        """
        from app import webserver

        message = "- INFO - Received '/api/graceful_shutdown' request"
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

        message = "- INFO - Server stopped"
        webserver.logger.log_message(message)




class TaskRunner(Thread):
    """A worker/thread"""

    def __init__(self, job_queue, shutdown_event):
        """
        A TaskRunner has 2 fields:
        - job_queue: server's Queue(), a thread-safe variable shared between all threads
        - shutdown_event: the thread stop when it receives this Event
        """
        super().__init__()
        self.job_queue = job_queue
        self.shutdown_event = shutdown_event

    def run(self):
        """
        The worker runs in an infinite loop.
        At each step, it extracts a job from the server's queue and processes it.
        The loop ends when the worker receives the 'shutdown' Event, which stops the thread.
        """
        from app import webserver

        while not self.shutdown_event.is_set():  # Check if shutdown event is set
            try:
                job = self.job_queue.get(timeout=1)  # Wait for 1 second for a job
                if job is None:  # None indicates shutdown request
                    break  # Break the loop and terminate the worker
                self._process_job(job)
                self.job_queue.task_done()
            except Exception:
                continue

    def _process_job(self, job):
        """
        Based on the job type, it will build the JSON result and store it in data base, on disk. 
        At the end of the computations, it will write in the .log file that the job was processed 
        """
        from app import webserver

        job_id: int = job["job_id"]
        job_type: JobType = job["job_type"]
        request_data: str = job["request_data"]
        response_data: Dict = {}

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
            response_data = webserver.data_ingestor.compute_response_state_diff_from_mean(
                question, state
            )
        elif job_type == JobType.MEAN_BY_CATEGORY:
            question: str = request_data.get("question", "")
            response_data = webserver.data_ingestor.compute_response_mean_by_category(question)


        with webserver.tasks_runner.lock_file_data_base:
            # Save JOB's results to disk
            with webserver.tasks_runner.pending_job_locks[job_id]:
                with open(os.path.join("results", f"{job_id}.json"), "w", encoding="utf-8") as file:
                    json.dump({"status": "done", "data": response_data}, file)

            # Delete file's lock
            webserver.tasks_runner.pending_job_locks.pop(job_id)

        # Write in .log file
        message = (
            f"- INFO - Computed response for job_id={job_id} ",
            "can be found at 'results/{job_id}.json'"
        )
        webserver.logger.log_message(message)
