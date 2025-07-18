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