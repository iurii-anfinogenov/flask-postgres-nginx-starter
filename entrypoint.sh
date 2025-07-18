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