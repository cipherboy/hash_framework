#!/bin/bash

py_gunicorn=$(which gunicorn)

if [ "$py_gunicorn" == "" ]; then
    echo "No gunicorn found" 1>&2
    exit 1
fi

mkdir -p ~/logs
bash stop_manager.sh

echo "Creating databases..."
python3 -m hash_framework.manager db

python3 -m hash_framework.scheduler 2> ~/logs/scheduler-err.log > ~/logs/scheduler.log &
spid="$!"
echo "$spid" > ~/logs/scheduler.pid
echo "scheduler pid: $spid"

$py_gunicorn hash_framework.manager.__main__:app --workers 8 --backlog 81920 --bind '0.0.0.0:8000' $@ 2> ~/logs/manager-err.log > ~/logs/manager.log &
mpid="$!"
echo "$mpid" > ~/logs/manager.pid
echo "manager pid: $mpid"


wait
