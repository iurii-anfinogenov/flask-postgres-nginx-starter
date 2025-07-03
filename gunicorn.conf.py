# gunicorn.conf.py

import multiprocessing
import os

# bind to a unix socket
bind = 'unix:' + os.getenv('GUNICORN_SOCKET', '/run/flask-postgres.sock')

# workers = 2 * CPU cores + 1
workers = multiprocessing.cpu_count() * 2 + 1

# timeout for workers (in seconds)
timeout = 120

# logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '/var/log/flask-postgres/access.log')
errorlog  = os.getenv('GUNICORN_ERROR_LOG',  '/var/log/flask-postgres/error.log')
loglevel  = os.getenv('GUNICORN_LOG_LEVEL',  'info')

# optionally run as specific user/group
user  = os.getenv('GUNICORN_USER',  'www-data')
group = os.getenv('GUNICORN_GROUP', 'www-data')
