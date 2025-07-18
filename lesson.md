## 📌 Цель:

Научиться контейнеризировать Python-приложение. Мы изолируем только Flask-приложение в Docker, при этом база данных остаётся на хосте, как и Nginx.
Это базовый и важный шаг — начало пути к полной контейнеризации.

## Что мы будем делать

В этом шаге:

    Мы создадим Dockerfile — инструкция, как собрать контейнер.

    Обеспечим запуск Flask-приложения внутри контейнера.

    Разберём, как Flask узнаёт параметры БД (через переменные среды).

    Научимся передавать .env в контейнер безопасно.

    PostgreSQL и Nginx пока остаются на хосте.

## Структура файлов, которые добавим
```sh
flask-postgres-nginx-starter/
├── Dockerfile              ← инструкция сборки образа
├── entrypoint.sh           ← скрипт ожидания БД
├── .dockerignore           ← чтобы не включать лишнее
└── .env.example            ← пример переменных среды

```


## ✅ Подготовка:

Перед началом работы убедись, что:

    Установлен Docker

    Flask-приложение (проект flask-postgres-nginx-starter) работает у тебя локально

    PostgreSQL работает локально (на хосте), как ты уже настраивал ранее

## Создай файл Dockerfile в корне проекта
```Dockerfile
# Используем официальный базовый образ Python
FROM python:3.11-slim

# Назначим рабочую директорию внутри контейнера
WORKDIR /app

# Отключим кэш Python и включим вывод
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Делаем точку входа исполняемой
RUN chmod +x entrypoint.sh

# Запускаем скрипт entrypoint перед основным процессом
ENTRYPOINT ["/app/entrypoint.sh"]

```
## Создай .dockerignore
```plaintext
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.env
```
_🔒 Важно: .env не попадёт внутрь контейнера — так безопаснее. Но нам нужно передавать переменные в контейнер другим способом._
## Скрипт entrypoint.sh
```sh
#!/bin/bash

# Ждём, пока PostgreSQL станет доступен
if [ "$DATABASE" = "postgres" ]; then
  echo "⏳ Ожидание PostgreSQL на $SQL_HOST:$SQL_PORT..."

  while ! nc -z $SQL_HOST $SQL_PORT; do
    sleep 0.1
  done

  echo "✅ PostgreSQL доступен, запускаем приложение"
fi

# Передаём управление Gunicorn или Flask
exec "$@"
```
## Пример .env.example
```ini
FLASK_ENV=development
DATABASE=postgres
SQL_HOST=127.0.0.1
SQL_PORT=5432
SQL_USER=appuser
SQL_PASSWORD=secret
SQL_DATABASE=myapp
```
_✅ Создай свой .env по этому шаблону:_
```sh
cp .env.example .env
```

## Сборка и запуск контейнера
```sh
docker build -t flask-docker-app .
```
## Запуск
```sh
docker run -it --rm --env-file .env -p 5000:5000 flask-docker-app python app.py
```
Промежуточное пояснение

Эта команда:

    запускает контейнер flask-docker-app;

    подставляет переменные из .env;

    пробрасывает порт 5000 хоста внутрь контейнера;

    выполняет python app.py, то есть запускает Flask-приложение напрямую;

    запускается в интерактивном режиме (-it) и удаляет контейнер после выхода (--rm).

⚠️ Такой способ удобен для отладки, но не предназначен для продакшена, потому что:

    приложение не будет перезапущено при сбое;

    нет логирования;

    не предусмотрено фоновое выполнение (background);

    не используется продакшен-сервер (например, gunicorn).

## Запуск Flask-приложения в контейнере в продакшене
Используем Gunicorn вместо python app.py

Gunicorn — это продакшен-ready WSGI-сервер. Мы уже добавили его в requirements.txt.

В Dockerfile мы не указывали явный запуск, а использовали:

```sh
ENTRYPOINT ["/app/entrypoint.sh"]
```
А в entrypoint.sh в конце:
```sh
exec "$@"
```
_Это значит: при запуске контейнера можно передать любую команду, и она будет исполнена._
Запуск контейнера с Gunicorn

Создайте запуск без -it и --rm, чтобы контейнер работал в фоне:
```sh
docker run -d \
  --name flask-app \
  --env-file .env \
  -p 5000:5000 \
  flask-docker-app \
  gunicorn -b 0.0.0.0:5000 app:app
```
Разбор:

    -d — detached (работает в фоне);

    --name flask-app — даёт имя контейнеру;

    -p 5000:5000 — проброс порта;

    gunicorn -b 0.0.0.0:5000 app:app — запуск Gunicorn, слушающий на всех интерфейсах контейнера, с приложением app из файла app.py.

Проверка

    Убедитесь, что контейнер запущен:

```sh
docker ps
```
Проверка в браузере:
Откройте http://<IP-сервера>:5000
Если вы на локальной машине — http://localhost:5000

Посмотреть логи:
```sh
docker logs flask-app
```
