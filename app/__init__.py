import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from app.logger import Logger

if not os.path.exists('results'):
    os.mkdir('results')
else:
    # MyTODO: begin by deleting everything from results/* directory
    os.system("rm -rf results/*")


webserver = Flask(__name__)

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1
webserver.tasks_runner = ThreadPool()

webserver.logger = Logger()

from app import routes
