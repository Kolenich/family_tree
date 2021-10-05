FROM python:3-slim

WORKDIR /app

EXPOSE 8000

RUN pip install -U pip -U setuptools gunicorn psycopg2-binary

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT python manage.py migrate \
        && python manage.py collectstatic --noinput \
        && gunicorn family_tree.wsgi -b 0.0.0.0 --access-logfile logs/gunicorn-access.log --log-file logs/gunicorn.log
