import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Database connection parameters from .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
# Flask secret key
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = SECRET_KEY

def get_conn():
    """
    Establish a new database connection using parameters from environment.
    """
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def init_db():
    """
    Create the notes table and ensure created_at column exists.
    """
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            # Create table if it doesn't exist
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL
                );
                """
            )
            # Add created_at column if missing
            cur.execute(
                """
                ALTER TABLE notes
                ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
                """
            )
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            conn = get_conn()
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'INSERT INTO notes (content) VALUES (%s);',
                        (content,)
                    )
            conn.close()
        return redirect(url_for('index'))

    conn = get_conn()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                'SELECT id, content, created_at FROM notes ORDER BY created_at DESC;'
            )
            notes = cur.fetchall()
    conn.close()

    return render_template('index.html', notes=notes)


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM notes WHERE id = %s;', (note_id,))
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Initialize database if needed
    init_db()
    # Start Flask development server
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=True
    )
