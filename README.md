# Flask-Postgres-Nginx-Starter (расширенная версия)

Минимальный, но гибкий шаблон для развёртывания трёхуровневого веб-стека:

* **PostgreSQL** – уровень хранения данных
* **Flask (Gunicorn)** – прикладной уровень (WSGI-сервер)
* **Nginx** – обратный прокси и балансировщик нагрузки

---

## 📦 Структура проекта

```sh
flask-postgres-nginx-starter/
├── app.py
├── config
│   ├── flask-postgres.service
│   ├── nginx.socket.conf       # Nginx через Unix-сокет (рекомендуется)
│   └── nginx.tcp.conf          # Nginx через TCP-порт (для отладки)
├── gunicorn.conf.py
├── README.md
├── requirements.txt
└── templates
    └── index.html
```

* **app.py** — минимальное Flask-приложение с чтением и записью данных в PostgreSQL.
* **requirements.txt** — зависимости Python.
* **config/flask-postgres.service** — unit-файл systemd для запуска Gunicorn.
* **config/nginx.socket.conf** — конфигурация Nginx для подключения по Unix-сокету.
* **config/nginx.tcp.conf** — конфигурация Nginx для подключения по TCP.

---

## 🔧 Установка и настройка

### 1. Зависимости

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip postgresql nginx
```

### 2. Настройка PostgreSQL

```bash
sudo -u postgres psql <<EOF
CREATE DATABASE myapp;
CREATE USER appuser WITH PASSWORD 'secret';
GRANT ALL PRIVILEGES ON DATABASE myapp TO appuser;
\q
EOF
```

### 3. Клонирование проекта

```bash
git clone https://github.com/your-org/flask-postgres-nginx-starter.git
cd flask-postgres-nginx-starter
cp .env.example .env
```

### 4. Установка Python-зависимостей

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Тестовый запуск

```bash
python3 app.py
```

Откройте в браузере: [http://localhost:5000](http://localhost:5000)

---

## 🚀 Развёртывание в продакшене

### Вариант A: Gunicorn + сокет + NGINX (рекомендуется)

#### 1. Конфигурация Gunicorn (`gunicorn.conf.py`)

```python
import multiprocessing
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
USE_TCP = os.getenv("GUNICORN_USE_TCP", "false").lower() == "true"

bind = os.getenv("GUNICORN_BIND", "127.0.0.1:8000") if USE_TCP else \
       f'unix:{BASE_DIR / "flask-postgres.sock"}'

workers = multiprocessing.cpu_count() * 2 + 1
accesslog = os.getenv("GUNICORN_ACCESS_LOG", str(BASE_DIR / "log/access.log"))
errorlog = os.getenv("GUNICORN_ERROR_LOG", str(BASE_DIR / "log/error.log"))
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
user = os.getenv("GUNICORN_USER", os.getenv("USER"))
group = os.getenv("GUNICORN_GROUP", user)
```

> 📌 Благодаря `os.getenv("USER")` запуск возможен без хардкода имени пользователя, работает на любой машине.

#### 2. Права на сокет и директории логов

Убедитесь, что:

* директория `log/` существует и доступна для записи
* сокет создаётся с правами, позволяющими Nginx читать его (например, `chmod 770` и группа `www-data`)

> 🔐 Лучше использовать `/opt/` и `www-data`:
>
> ```bash
> sudo chown -R www-data:www-data /opt/flask-postgres-nginx-starter
> ```

#### 3. systemd unit-файл `/etc/systemd/system/myapp.service`

```ini
[Unit]
Description=Gunicorn instance to serve flask-postgres-nginx-starter
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/flask-postgres-nginx-starter
EnvironmentFile=/opt/flask-postgres-nginx-starter/.env
ExecStart=/opt/flask-postgres-nginx-starter/venv/bin/gunicorn \
  --config /opt/flask-postgres-nginx-starter/gunicorn.conf.py \
  app:app
Restart=always
RestartSec=5
Type=simple

[Install]
WantedBy=multi-user.target
```

#### 4. Nginx (используйте `config/nginx.socket.conf`)

```nginx
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/flask-postgres-nginx-starter/flask-postgres.sock;
    }

    access_log /var/log/nginx/flask-postgres.access.log;
    error_log  /var/log/nginx/flask-postgres.error.log;
}
```

> ⚠️ Убедитесь, что путь к `.sock` совпадает с `bind` в `gunicorn.conf.py`

### Вариант B: Gunicorn через TCP-порт (отладка)

#### systemd:

```ini
ExecStart=/opt/flask-postgres-nginx-starter/venv/bin/gunicorn \
  --bind 127.0.0.1:8000 \
  --config /opt/flask-postgres-nginx-starter/gunicorn.conf.py \
  app:app
```

#### Nginx (используйте `config/nginx.tcp.conf`):

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        include proxy_params;
    }
}
```

---

## ✅ Что выбрать?

| Сценарий          | Рекомендуемый способ      |
| ----------------- | ------------------------- |
| Продакшен         | Unix-сокет + Nginx        |
| Локальная отладка | TCP-порт (127.0.0.1:8000) |

Сокет даёт выше производительность и безопасность, но требует настройки прав. TCP — проще для первого запуска и дебага.

---

## 📊 Мониторинг и отладка

```bash
sudo systemctl status myapp
sudo journalctl -u myapp -f
sudo tail -f /var/log/nginx/*.log
sudo tail -f log/*.log
```

---

## 🔍 Возможные расширения

* Подключение HTTPS через Let's Encrypt (certbot --nginx)
* Контейнеризация с помощью Docker или Podman
* Поддержка .env переменных через python-dotenv или decouple
* Добавление CI/CD пайплайнов (GitHub Actions, GitLab CI)
* Фронтенд-интеграция: React, Vue, HTMX, Bootstrap
* Метрики: Prometheus exporter, логирование в JSON и системные лог-сервисы

---

**Авторский комментарий:** этот шаблон — основа продакшен-развёртывания для начинающего разработчика. Практикуйтесь с разными типами запуска, изучайте systemd и работу сокетов — это основа надёжного бэкенда.
