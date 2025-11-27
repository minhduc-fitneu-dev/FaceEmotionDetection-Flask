import sqlite3
from config import Config

def connect_db():
    return sqlite3.connect(Config.DB_PATH)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        uid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lophoc (
        id_lophoc INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_lop TEXT NOT NULL,
        so_sv INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        uid INTEGER NOT NULL,
        FOREIGN KEY(uid) REFERENCES user(uid)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sinhvien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_lophoc INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        face_path TEXT NOT NULL,
        emotion TEXT NOT NULL,
        confidence REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(id_lophoc) REFERENCES lophoc(id_lophoc)
    )''')

    conn.commit()
    conn.close()
