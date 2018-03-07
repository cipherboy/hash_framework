#!/bin/bash

py_gunicorn=$(which gunicorn)

if [ "$py_gunicorn" == "" ]; then
    echo "No gunicorn found" 1>&2
    exit 1
fi

$py_gunicorn hash_framework.manager.__main__:app --workers 1 --backlog 81920 --bind '0.0.0.0:8000' $@
