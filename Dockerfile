FROM python:alpine
WORKDIR /app
EXPOSE 8000
RUN pip install -U pip -U setuptools gunicorn psycopg2-binary
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . .
RUN chmod +x ./dockerentrypoint.sh
ENTRYPOINT ["./dockerentrypoint.sh"]