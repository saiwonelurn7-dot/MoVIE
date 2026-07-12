import sqlite3
from datetime import datetime

DB_PATH = "movies.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            poster_file_id TEXT,
            poster_file_path TEXT,      -- Web မှာပြဖို့
            video_file_id TEXT,
            video_file_path TEXT,
            channel_msg_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_movie(title, desc, poster_fid, poster_path, video_fid, video_path, channel_msg_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO movies (title, description, poster_file_id, poster_file_path, video_file_id, video_file_path, channel_msg_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, desc, poster_fid, poster_path, video_fid, video_path, channel_msg_id))
    conn.commit()
    movie_id = c.lastrowid
    conn.close()
    return movie_id

def get_all_movies():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # id, title, desc, poster_path, created_at
    c.execute('SELECT id, title, description, poster_file_path, created_at FROM movies ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_movie(movie_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # id, title, desc, poster_path, created_at, channel_msg_id
    c.execute('SELECT id, title, description, poster_file_path, created_at, channel_msg_id FROM movies WHERE id = ?', (movie_id,))
    row = c.fetchone()
    conn.close()
    return row
