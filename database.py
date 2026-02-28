import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "sudoku.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created  TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            time_secs  INTEGER NOT NULL,
            hints_used INTEGER NOT NULL,
            score      INTEGER NOT NULL,
            played_at  TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password, created) VALUES (?, ?, ?)",
            (username, hash_password(password),
             datetime.now().strftime("%Y-%m-%d"))
        )
        conn.commit()
        conn.close()
        return True, "Account created!"
    except sqlite3.IntegrityError:
        return False, "Username already taken."


def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[1] == hash_password(password):
        return True, row[0]
    return False, None


def save_score(user_id, difficulty, time_secs, hints_used, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """INSERT INTO scores
           (user_id, difficulty, time_secs, hints_used, score, played_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, difficulty, time_secs, hints_used, score,
         datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()


def get_leaderboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT u.username, s.difficulty, s.time_secs, s.score, s.played_at
        FROM scores s
        JOIN users u ON s.user_id = u.id
        ORDER BY s.score DESC
        LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def get_profile(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT created FROM users WHERE id=?", (user_id,))
    joined = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM scores WHERE user_id=?", (user_id,))
    total = c.fetchone()[0]
    c.execute("SELECT MAX(score) FROM scores WHERE user_id=?", (user_id,))
    best = c.fetchone()[0] or 0
    c.execute("SELECT SUM(score) FROM scores WHERE user_id=?", (user_id,))
    total_score = c.fetchone()[0] or 0
    by_diff = {}
    for diff in ("Easy", "Medium", "Hard", "Expert"):
        c.execute(
            """SELECT MIN(time_secs), MAX(score) FROM scores
               WHERE user_id=? AND difficulty=?""",
            (user_id, diff)
        )
        by_diff[diff] = c.fetchone()
    conn.close()
    return {
        "username":     username,
        "joined":       joined,
        "total":        total,
        "best_single":  best,
        "total_score":  total_score,
        "by_diff":      by_diff,
    }


def calculate_score(difficulty, time_secs, hints_used):
    base = {"Easy": 100, "Medium": 200, "Hard": 350, "Expert": 500}
    time_bonus   = max(0, 300 - time_secs)
    hint_penalty = hints_used * 20
    return max(0, base.get(difficulty, 100) + time_bonus - hint_penalty)
