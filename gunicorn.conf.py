import multiprocessing
from loguru import logger
import logging
from logger import init_logging

wsgi_app = "main:app"
bind = '0.0.0.0:8000'
preload_app = True
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 2

print(f'Workers: {workers}')

worker_class = 'uvicorn.workers.UvicornWorker'
# logconfig = './log.conf'

# class PropagateHandler(logging.Handler):
#     def emit(self, record):
#         logging.getLogger("gunicorn.error").handle(record)

# logger.remove()
# logger.add(PropagateHandler())
