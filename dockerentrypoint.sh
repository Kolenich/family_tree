#!/bin/sh

mkdir -p logs
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn family_tree.wsgi -b 0.0.0.0 --access-logfile logs/gunicorn-access.log --log-file logs/gunicorn.log
