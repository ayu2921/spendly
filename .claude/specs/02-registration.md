# Spec: Registration

## Overview
Implement the user registration flow so new visitors can create a Spendly account. This step wires up the `POST /register` route, adds a `create_user()` helper to the database layer, and updates `register.html` to display validation errors via Flask flash messages. On success the user is redirected to the login page. This is the first step that introduces Flask sessions, so a `SECRET_KEY` must be configured on the app.

## Depends on
- Step 01 — Database Setup (users table, `get_db()`, and `werkzeug` must be in place)

## Routes
- `POST /register` — validates form input, creates user, redirects to login — public

The existing `GET /register` stub remains unchanged; only the POST handler is added.

## Database changes
No new tables or columns. One new helper function in `database/db.py`:

- `create_user(name, email, password)` — hashes the password and inserts a row into `users`. Returns the new user's `id` on success. Raises `sqlite3.IntegrityError` if the email is already taken (UNIQUE constraint).

## Templates
- **Modify:** `templates/register.html` — add `<form method="POST">` with `action="{{ url_for('register') }}"`, CSRF-safe hidden field is not required at this stage, flash message block for errors and success, and fields: name, email, password, confirm password.

## Files to change
- `app.py` — add `SECRET_KEY` config, import `create_user` from `database.db`, add `POST /register` route handler
- `database/db.py` — add `create_user()` function
- `templates/register.html` — update form and add flash message rendering

## Files to create
- `static/css/register.css` — page-specific styles for the registration form (imported only in `register.html`, not in `base.html`)

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterised queries only — never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` — never stored in plain text
- Use CSS variables — never hardcode hex values in `register.css`
- All templates extend `base.html`
- `SECRET_KEY` must be set on `app.config` before any flash or session usage — use `os.urandom(24)` or a fixed dev string; do not commit a production secret
- Validate server-side: name non-empty, email non-empty, password ≥ 8 characters, password matches confirm password — reject before hitting the DB
- On duplicate email, catch `sqlite3.IntegrityError` and flash a user-friendly error; do not let the 500 bubble up
- Use `flask.flash()` for all user-facing messages and `get_flashed_messages()` in the template
- On success, `redirect(url_for('login'))` — do not log the user in automatically (that is Step 3)
- Use `abort(405)` if a non-GET/POST method hits `/register`

## Definition of done
- [ ] Submitting the form with valid data creates a new row in `users` with a hashed password
- [ ] Submitting with a duplicate email shows a flash error and does not insert a duplicate row
- [ ] Submitting with mismatched passwords shows a flash error and does not touch the DB
- [ ] Submitting with a password shorter than 8 characters shows a flash error
- [ ] Submitting with any blank field shows a flash error
- [ ] Successful registration redirects to `/login`
- [ ] The registration form renders correctly at `GET /register` with no errors on a fresh load
- [ ] Flash messages are visible in the browser after a failed submission
- [ ] Existing seed data (demo user) is unaffected — `seed_db()` still runs without error on startup
