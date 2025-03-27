from app import webserver
from flask import request, jsonify, after_this_request

import os
import signal
from sys import exit
import json
from app.task_runner import JobType

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_job_result(job_id: str):

    job_id_integer: int = 0
    
    try:
        job_id_integer = int(job_id)
    except ValueError:
        message = f"- ERROR - Invalid job_id \'{job_id}\'! It must be a positive integer, greater than 0!"
        webserver.logger.log_message(message)
        return jsonify({"status": "error", "reason": "Invalid job_id"}), 400

    if job_id_integer <= 0:
        message = f"- ERROR - Invalid job_id \'{job_id}\'! It must be a positive integer, greater than 0!"
        webserver.logger.log_message(message)
        return jsonify({"status": "error", "reason": "Invalid job_id"}), 400
           
    return webserver.tasks_runner.get_job_result(job_id_integer)

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    return handle_processing_request(request, JobType.STATES_MEAN)


@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    return handle_processing_request(request, JobType.STATE_MEAN)



@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    return handle_processing_request(request, JobType.BEST_5)



@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    return handle_processing_request(request, JobType.WORST_5)


@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    return handle_processing_request(request, JobType.GLOBAL_MEAN)


@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    return handle_processing_request(request, JobType.DIFF_FROM_MEAN)


@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    return handle_processing_request(request, JobType.STATE_DIFF_FROM_MEAN)

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    return handle_processing_request(request, JobType.MEAN_BY_CATEGORY)


@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    return handle_processing_request(request, JobType.STATE_MEAN_BY_CATEGORY)


def handle_processing_request(request, job_type: JobType):
    # Throw an error if '/api/graceful_shutdown' request was already made
    with webserver.lock_is_shutting_down:
        if webserver.is_shutting_down is True:
            webserver.logger.log_message(f" - ERROR - Bad request: cannot accept '{job_type.value}' request after GRACEFUL SHUTDOWN!")
            # Exit code 400 - Bad Request
            return jsonify({"status": "error", "reason": "shutting down"}), 400 
        
    # Get request data
    data = request.json
    # Register job. Don't wait for task to finish
    job_id = webserver.tasks_runner.add_job(JobType.STATE_MEAN_BY_CATEGORY, data)
    # Return associated job_id
    return jsonify({"job_id": job_id})



@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    webserver.tasks_runner.graceful_shutdown()
    return jsonify({'status': 'done'})

@webserver.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    # TODO: implement it
    return jsonify({'status': 'Not Implemented Yet'})    

@webserver.route('/api/num_jobs', methods=['GET'])
def get_num_jobs():
    num_jobs = webserver.tasks_runner.get_num_pending_jobs()
    return jsonify({'num_pending_job': f'{num_jobs}'})




# You can check localhost in your browser to see what this displays
@webserver.route('/')
@webserver.route('/index')
def index():
    routes = get_defined_routes()
    msg = f"Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ""
    for route in routes:
        paragraphs += f"<p>{route}</p>"

    msg += paragraphs
    return msg

def get_defined_routes():
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
