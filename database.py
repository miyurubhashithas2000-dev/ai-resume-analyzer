import sqlite3
from datetime import datetime

DB_NAME = "resume_history.db"


def init_db():
    """Create the database table if it doesn't exist"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            job_description TEXT,
            match_score INTEGER,
            missing_keywords TEXT,
            strengths TEXT,
            weaknesses TEXT,
            suggestions TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(job_description, result):
    """Save one analysis result into the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_history 
        (date, job_description, match_score, missing_keywords, strengths, weaknesses, suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        job_description,
        result["match_score"],
        ", ".join(result["missing_keywords"]),
        ", ".join(result["strengths"]),
        ", ".join(result["weaknesses"]),
        ", ".join(result["suggestions"])
    ))
    conn.commit()
    conn.close()


def get_all_history():
    """Retrieve all past analyses, newest first"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows