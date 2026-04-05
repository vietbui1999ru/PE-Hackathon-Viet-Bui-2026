# Failure Modes & Recovery Guide

## What Was Tested & Verified

### CI/CD Pipeline
- **30/30 tests passing** on every push via GitHub Actions
- **66% code coverage** (requirement: >50%)
- CI blocks merge if tests fail — verified by running pytest with `--cov-fail-under=50`
- Stack: Ubuntu 24.04, Python 3.13.12, PostgreSQL 16, pytest 9.0.2

---

## Application Error Responses

### 400 Bad Request
**Cause:** Missing or invalid fields.
**Verified endpoints:**
- `POST /users` without email → 400
- `POST /urls` without original_url → 400
- `POST /urls` with non-http URL → 400
- `POST /events` without url_id → 400

**Response format:**
```json
{"error": "original_url and user_id are required"}
```

---

### 404 Not Found
**Cause:** Resource does not exist.
**Verified endpoints:**
- `GET /users/99999` → 404
- `GET /urls/99999` → 404
- `GET /urls/<inactive_short_code>/redirect` → 404

**Response format:**
```json
{"error": "User not found"}
```

---

### 409 Conflict
**Cause:** Unique constraint violation.
**Verified cases:**
- `POST /users` with duplicate username → 409
- `POST /urls` with duplicate short_code → 409

**Response format:**
```json
{"error": "username or email already exists"}
```

---

### 500 Internal Server Error
**Cause:** Unhandled exception or missing import.
**Observed during development:**
- `NameError: timezone not defined` — fixed by adding `from datetime import datetime, timezone`
- `NameError: IntegrityError not defined` — fixed by adding `from peewee import IntegrityError`
- `peewee.OperationalError: no such table` — fixed by calling `db.create_tables()` in `create_app()`

**Recovery:**
```bash
docker compose logs app --tail 50
```

---

## Infrastructure Failures

### PostgreSQL Sequence Desync
**Cause:** Bulk CSV load inserted explicit IDs without updating the auto-increment sequence.
**Symptom:** `IntegrityError: duplicate key value violates unique constraint "_pkey"`
**Recovery:**
```bash
uv run python -c "
from app import create_app
from app.database import db
app = create_app()
with app.app_context():
    db.execute_sql(\"SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))\")
    db.execute_sql(\"SELECT setval('urls_id_seq', (SELECT MAX(id) FROM urls))\")
    db.execute_sql(\"SELECT setval('events_id_seq', (SELECT MAX(id) FROM events))\")
"
```
**Prevention:** CI workflow runs this automatically after `load_data`.

---

### App Container Crash
**Symptom:** `curl http://localhost:5000/health` → connection refused
**Recovery:** Automatic via `restart: unless-stopped` in docker-compose.yml
**Verified:** Killed PID 1 inside container, app restarted automatically.
```bash
# simulate crash
docker compose exec app python -c "import os; os.kill(1, 9)"
# verify recovery
sleep 3 && curl http://localhost:5000/health
```

---

### Database Container Unavailable
**Symptom:** All endpoints 500, logs show `OperationalError`
**Recovery:**
```bash
docker compose restart db
docker compose logs db --tail 20
```
App container will reconnect on next request due to `reuse_if_open=True`.

---

## Health Check
```bash
curl http://localhost:5000/health
# expected: {"status": "ok"}
```

---

## Known Gaps
- Advanced hidden challenges 3 (users), 4 (urls), 6 (events) did not pass.
  These test edge cases around duplicate rejection, inactive URL handling,
  and event tracking that require further investigation.
