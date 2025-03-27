import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool, JobType
from app.logger import Logger
from threading import Lock



if not os.path.exists('results'):
    os.mkdir('results')
else:
    os.system("rm -rf results/*")


webserver = Flask(__name__)

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
webserver.logger = Logger()


webserver.job_counter = 1
webserver.tasks_runner = ThreadPool()


webserver.is_shutting_down = False
webserver.lock_is_shutting_down = Lock()


from app import routes
