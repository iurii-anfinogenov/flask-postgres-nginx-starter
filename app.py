import os
from flask import Flask
import psycopg2
from dotenv import load_dotenv

# 1. Загрузка переменных окружения из .env (при наличии)
load_dotenv()

# 2. Чтение переменных с fallback-значениями
DB_NAME     = os.getenv("DB_NAME", "myapp")
DB_USER     = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
SECRET_KEY  = os.getenv("SECRET_KEY", "fallback_secret")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

def get_conn():
    conn_str = (
        f"dbname={DB_NAME} user={DB_USER} "
        f"password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
    )
    return psycopg2.connect(conn_str)

def init_db():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS notes ("
                "id SERIAL PRIMARY KEY, content TEXT);"
            )
            conn.commit()
    except Exception as e:
        app.logger.error(f"DB init error: {e}")

# Инициализация БД при старте
init_db()

@app.route('/')
def index():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT content FROM notes;")
            rows = cur.fetchall()
        return '<br>'.join(row[0] for row in rows)
    except Exception as e:
        return f"Error fetching notes: {e}", 500

@app.route('/add/<text>')
def add(text):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO notes (content) VALUES (%s);",
                (text,)
            )
            conn.commit()
        return f"Added: {text}"
    except Exception as e:
        return f"Error adding note: {e}", 500

if __name__ == '__main__':
    # Режим разработки; в продакшн используем Gunicorn
    app.run(host='0.0.0.0', port=5000)
