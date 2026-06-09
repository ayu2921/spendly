import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash


def _close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        g.db = conn
    return g.db


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount      REAL    NOT NULL CHECK (amount > 0),
            category    TEXT    NOT NULL CHECK (category IN (
                            'Food', 'Transport', 'Bills', 'Health',
                            'Entertainment', 'Shopping', 'Other'
                        )),
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)


def seed_db():
    db = get_db()

    count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    if count > 0:
        return

    db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Demo User', 'demo@spendly.com', generate_password_hash('demo123'))
    )
    db.commit()

    user_id = db.execute(
        'SELECT id FROM users WHERE email = ?', ('demo@spendly.com',)
    ).fetchone()['id']

    expenses = [
        (user_id, 349.00, 'Food', '2025-05-01', 'Zomato order'),
        (user_id, 200.00, 'Transport', '2025-05-05', 'Metro card recharge'),
        (user_id, 1450.75, 'Bills', '2025-05-08', 'Electricity bill'),
        (user_id, 185.00, 'Health', '2025-05-10', 'Cold & Flu medicine'),
        (user_id, 2999.00, 'Shopping', '2025-05-13', 'Wireless headphones'),
        (user_id, 280.00, 'Food', '2025-05-17', 'Lunch at Chaayos'),
        (user_id, 145.50, 'Transport', '2025-05-20', 'Ola ride'),
        (user_id, 649.00, 'Entertainment', '2025-05-25', 'Netflix subscription'),
    ]
    db.executemany(
        'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
        expenses
    )
    db.commit()


def create_user(name, email, password):
    db = get_db()
    hashed = generate_password_hash(password)
    cursor = db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        (name, email, hashed)
    )
    db.commit()
    return cursor.lastrowid


def get_user_by_email(email):
    db = get_db()
    return db.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()
