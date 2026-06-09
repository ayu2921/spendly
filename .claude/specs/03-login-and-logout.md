# Spec: Login and Logout

## Overview
This step adds session-based authentication to Spendly. Users can log in with their email and password, and the server stores their identity in a signed Flask session cookie. Logging out clears that session. This is the gateway that all future protected routes (dashboard, expenses) will depend on — without it, there is no concept of "the current user."

## Depends on
- Step 01 — Database Setup (users table, `get_db()`, password hashing with werkzeug)
- Step 02 — Registration (users exist in the database with hashed passwords)

## Routes
- `POST /login` — validate credentials, set session, redirect to dashboard stub — public
- `GET /logout` — clear session, redirect to landing page — public (no login guard needed)

## Database changes
No database changes. The `users` table already has `email` and `password_hash` columns from Step 01.

A new helper is needed in `database/db.py`:
- `get_user_by_email(email)` — returns a single user row dict or `None`

## Templates
- **Modify:** `templates/login.html` — add a `<form method="POST">` with email + password fields, CSRF-safe action via `url_for('login')`, and a flash message block for errors

## Files to change
- `app.py` — convert `GET /login` to handle both GET and POST; implement `POST /logout`
- `database/db.py` — add `get_user_by_email(email)`
- `templates/login.html` — add the POST form and flash error display

## Files to create
No new files.

## New dependencies
No new dependencies. `flask.session` and `werkzeug.security.check_password_hash` are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw SQLite via `get_db()` only
- Parameterised queries only — never f-strings in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Use CSS variables — never hardcode hex values in templates or stylesheets
- All templates extend `base.html`
- Store only `user_id` and `user_name` in the session — never store the password hash or full row
- On failed login, flash a **generic** error ("Invalid email or password") — never reveal which field was wrong
- After successful login, redirect to `url_for('dashboard')` (the existing stub is fine)
- After logout, redirect to `url_for('index')`
- `GET /login` must redirect to dashboard if a session already exists (avoid double-login)

## Definition of done
- [ ] Visiting `/login` while already logged in redirects to `/` (or dashboard stub) without showing the form
- [ ] Submitting `/login` with a valid email + correct password sets the session and redirects away from `/login`
- [ ] Submitting `/login` with a valid email + wrong password re-renders the login form with a flash error and no session is set
- [ ] Submitting `/login` with an email that does not exist re-renders the login form with the same generic flash error
- [ ] Visiting `/logout` clears the session and redirects to the landing page
- [ ] After logout, visiting `/login` shows the form (no redirect loop)
- [ ] The demo user (`demo@spendly.com` / `demo123`) can log in and log out successfully
