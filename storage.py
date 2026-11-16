"""Local lead database. No external CRM or email sending."""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'prospects.db'

def connect():
    connection = sqlite3.connect(DB)
    connection.execute('''CREATE TABLE IF NOT EXISTS prospects (
        id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL,
        company TEXT NOT NULL, sector TEXT, score INTEGER, status TEXT DEFAULT 'Needs review',
        report_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    return connection

def save(url, report):
    with connect() as db:
        db.execute('''INSERT INTO prospects(url,company,sector,score,report_json)
        VALUES(?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET
        company=excluded.company, sector=excluded.sector,
        score=excluded.score, report_json=excluded.report_json''',
        (url, report['company'], report['sector'], report['score'], json.dumps(report)))

def all_prospects():
    with connect() as db:
        return db.execute('SELECT company,url,sector,score,status,created_at FROM prospects ORDER BY created_at DESC').fetchall()

def get_prospect(url):
    """Retrieve a saved prospect and its full research report."""
    with connect() as db:
        row = db.execute(
            """
            SELECT company, url, sector, score, status,
                   report_json, created_at
            FROM prospects
            WHERE url = ?
            """,
            (url,)
        ).fetchone()

    if row is None:
        return None

    return {
        "company": row[0],
        "url": row[1],
        "sector": row[2],
        "score": row[3],
        "status": row[4],
        "report": json.loads(row[5]),
        "created_at": row[6],
    }


def update_status(url, status):
    """Update a prospect's human-review status."""
    allowed = {"Needs review", "Qualified", "Not qualified"}

    if status not in allowed:
        raise ValueError("Invalid prospect status.")

    with connect() as db:
        db.execute(
            "UPDATE prospects SET status = ? WHERE url = ?",
            (status, url)
        )
