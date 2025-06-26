# Flask-Postgres-Nginx-Starter

Минимальный шаблон для развёртывания трёхуровневого веб-стека:
- **PostgreSQL** – уровень хранения данных
- **Flask (Gunicorn)** – прикладной уровень (WSGI-сервер)
- **Nginx** – обратный прокси, балансировка нагрузки

---

## 📦 Структура проекта

```sh
flask-postgres-nginx-starter/
├── app.py
├── requirements.txt
├── README.md
└── config/
    ├── gunicorn.service
    └── myapp.nginx

```

- **app.py** — самое простое Flask-приложение с сохранением/чтением записей из PostgreSQL.
- **requirements.txt** — зависимости Python.
- **config/gunicorn.service** — unit-файл systemd для запуска Gunicorn.
- **config/myapp.nginx** — конфигурация Nginx для проксирования запросов.

---

## 🔧 Предварительные требования

На Ubuntu/Debian-&-похожих:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip postgresql nginx

1. Настройка базы данных

    Переключитесь на пользователя postgres и создайте базу и роль:
```sh
sudo -u postgres psql <<EOF
CREATE DATABASE myapp;
CREATE USER appuser WITH PASSWORD 'secret';
GRANT ALL PRIVILEGES ON DATABASE myapp TO appuser;
\q
EOF

```
2. Развёртывание приложения

Клонируйте репозиторий и перейдите в папку:

```sh
git clone https://github.com/your-org/flask-postgres-nginx-starter.git
cd flask-postgres-nginx-starter
```
Создайте и активируйте виртуальное окружение:
```sh
python3 -m venv venv
source venv/bin/activate
```
Установите зависимости
```sh
pip install -r requirements.txt
```

Быстрый запуск для разработки

```sh
python3 app.py
```

Откройте в браузере http://localhost:5000.
Маршрут /add/<текст> добавляет запись, / выводит все записи.


3. Продакшн-развёртывание
3.1 Gunicorn + systemd

    Скопируйте файл config/gunicorn.service в /etc/systemd/system/myapp.service:
```ini
[Unit]
Description=Gunicorn instance to serve myapp
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/flask-postgres-nginx-starter
ExecStart=/usr/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```
Активируйте и запустите сервис:
```sh
sudo systemctl daemon-reload
sudo systemctl start myapp
sudo systemctl enable myapp
```
Проверьте статус:
```sh
sudo systemctl status myapp
```

3.2 Nginx

    Скопируйте config/myapp.nginx в /etc/nginx/sites-available/myapp:

```nginx
server {
    listen 80;
    server_name example.com;  # замените на ваш домен или IP

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
Включите сайт и перезагрузите Nginx:
```sh
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
📑 Логи и отладка

    Gunicorn:
```sh
sudo journalctl -u myapp -f
```
🔍 Возможные расширения

    Подключить HTTPS через Let's Encrypt (certbot --nginx).

    Добавить Docker-файлы для контейнеризации.

    Ввести переменные окружения и .env-файл (например, с python-decouple).

    Расширить приложение фронтом на React/Vue.


