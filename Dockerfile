FROM python:3.13.5-slim

RUN useradd -u 1000 -m -d /app -s /bin/bash app

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

USER app
COPY showmock ./showmock
COPY data ./data

ENV BIND=0.0.0.0:8000
ENV DATA_DIR=./data
ENV DEFAULT_CONTENT_TYPE=application/json

ENTRYPOINT ["python", "-m", "showmock"]
CMD []

EXPOSE 8000
VOLUME ["/app/data"]
