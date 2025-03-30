#!/usr/bin/bash

rm -f $HOME/Downloads/ASC-Tema-1.zip

git log > git-log

zip -r $HOME/Downloads/ASC-Tema-1.zip \
    api_server.py        \
    app/                 \
    app/routes.py        \
    app/task_runner.py   \
    app/data_ingestor.py \
    app/__init__.py      \
    README.md            \
    unittests/           \
    unittests/mytests.py \
    git-log

rm -f git-log