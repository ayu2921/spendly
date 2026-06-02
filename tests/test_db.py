import sqlite3
import pytest
from database.db import get_db, init_db, seed_db


def test_get_db_returns_connection(app):
    db = get_db()
    assert isinstance(db, sqlite3.Connection)


def test_get_db_same_connection_within_request(app):
    db1 = get_db()
    db2 = get_db()
    assert db1 is db2


def test_get_db_foreign_keys_enabled(app):
    db = get_db()
    result = db.execute('PRAGMA foreign_keys').fetchone()
    assert result[0] == 1


def test_get_db_row_factory_is_sqlite_row(app):
    db = get_db()
    assert db.row_factory is sqlite3.Row


def test_init_db_creates_users_table(app):
    db = get_db()
    result = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()
    assert result is not None


def test_init_db_creates_expenses_table(app):
    db = get_db()
    result = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"
    ).fetchone()
    assert result is not None


def test_init_db_is_idempotent(app):
    init_db()
    init_db()


def test_seed_db_inserts_users(app):
    seed_db()
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    assert count >= 1


def test_seed_db_inserts_expenses(app):
    seed_db()
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
    assert count >= 8


def test_seed_db_is_idempotent(app):
    seed_db()
    seed_db()
    db = get_db()
    count = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    assert count == 1


def test_expenses_fk_enforced(app):
    db = get_db()
    db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('Test User', 'test@example.com', 'fakehash')
    )
    db.commit()
    user_id = db.execute(
        'SELECT id FROM users WHERE email = ?', ('test@example.com',)
    ).fetchone()['id']
    db.execute(
        'INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)',
        (user_id, 100.0, 'Food', '2025-05-01')
    )
    db.commit()
    db.execute('DELETE FROM users WHERE id = ?', (user_id,))
    db.commit()
    remaining = db.execute(
        'SELECT COUNT(*) FROM expenses WHERE user_id = ?', (user_id,)
    ).fetchone()[0]
    assert remaining == 0


def test_invalid_category_rejected(app):
    db = get_db()
    db.execute(
        'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
        ('X', 'x@x.com', 'h')
    )
    db.commit()
    uid = db.execute(
        'SELECT id FROM users WHERE email = ?', ('x@x.com',)
    ).fetchone()['id']
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            'INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)',
            (uid, 50.0, 'INVALID_CATEGORY', '2025-05-01')
        )
        db.commit()
