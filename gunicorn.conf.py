import os


bind = os.getenv('BIND', '0.0.0.0:8000')
workers = int(os.getenv('WORKERS', "1"))
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "debug"
