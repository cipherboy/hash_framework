#!/bin/bash

py_gunicorn=$(which gunicorn)

$py_gunicorn hash_framework.manager.__main__:app --workers=1 $@
