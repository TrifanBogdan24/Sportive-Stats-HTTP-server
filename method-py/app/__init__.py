"""Set up the HTTP web server"""

import os
from threading import Lock
from flask import Flask

from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.logger import Logger
from app.routes import register_routes


def create_app():
    """Flask application factory."""

    app = Flask(__name__)

    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    else:
        os.system(f"rm -rf {results_dir}/*")

    app.logger = Logger()
    app.data_ingestor = DataIngestor("../nutrition_activity_obesity_usa_subset.csv")
    app.job_counter = 1
    app.tasks_runner = ThreadPool(app)
    app.is_shutting_down = False
    app.lock_is_shutting_down = Lock()

    register_routes(app)

    return app
