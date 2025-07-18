# gunicorn.conf.py

import multiprocessing
import os
from pathlib import Path
import pwd
import grp

BASE_DIR = Path(__file__).resolve().parent

bind = f'unix:{os.getenv("GUNICORN_SOCKET", str(BASE_DIR / "flask-postgres.sock"))}'

workers = multiprocessing.cpu_count() * 2 + 1
timeout = 120

accesslog = os.getenv("GUNICORN_ACCESS_LOG", str(BASE_DIR / "log" / "flask-postgres" / "access.log"))
errorlog  = os.getenv("GUNICORN_ERROR_LOG",  str(BASE_DIR / "log" / "flask-postgres" / "error.log"))
loglevel  = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Получаем имя текущего пользователя
current_uid = os.getuid()
current_gid = os.getgid()
user  = os.getenv("GUNICORN_USER", pwd.getpwuid(current_uid).pw_name)
group = os.getenv("GUNICORN_GROUP", grp.getgrgid(current_gid).gr_name)
