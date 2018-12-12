#!/bin/sh

# Migrate Django DB and load initial auth data with user:gerdi pw:gerdigerdi
python3 manage.py makemigrations --noinput && python3 manage.py migrate
python3 manage.py loaddata initial_superuser.json

# service nginx start & Start Gunicorn processes
nginx & gunicorn hcc_py.wsgi --bind 0.0.0.0:8000 --workers 3
