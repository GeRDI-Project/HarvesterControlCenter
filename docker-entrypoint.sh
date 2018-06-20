#!/bin/sh

# service nginx start

# Start Gunicorn processes

nginx & gunicorn hcc_py.wsgi --bind 0.0.0.0:8000 --workers 3
