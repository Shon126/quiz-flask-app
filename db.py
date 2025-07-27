import sqlite3

DB_NAME = 'leaderboard.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            category TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_score(name, score, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO leaderboard (name, score, category) VALUES (?, ?, ?)', (name, score, category))
    conn.commit()
    conn.close()

def get_top_20():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Prioritize higher score, then older submission (more fair)
    c.execute('''
        SELECT name, score, category 
        FROM leaderboard 
        ORDER BY score DESC, timestamp ASC 
        LIMIT 20
    ''')
    results = c.fetchall()
    conn.close()
    return results