FROM python:3.10-slim

RUN useradd -u 1000 -m -d /app -s /bin/bash app

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

USER app
COPY gunicorn.conf.py server.py ./
COPY data ./data

ENV BIND=0.0.0.0:8000
ENV DATA_DIR=./data
ENV DEFAULT_CONTENT_TYPE=application/json

CMD gunicorn -c gunicorn.conf.py server:app

EXPOSE 8000
VOLUME ["/app/data"]
