"""SQLite cache. Key = topic+grade+language+prompt version. Stores NO user data at all.
With 20-50k teachers, popular topics repeat, so most requests cost zero LLM tokens."""
import hashlib
import os
import sqlite3
import time
from collections import defaultdict, deque


def _conn():
    c = sqlite3.connect(os.getenv("CACHE_DB", "coach_cache.sqlite3"))
    c.execute("CREATE TABLE IF NOT EXISTS cache (k TEXT PRIMARY KEY, v TEXT NOT NULL, created REAL)")
    return c


def make_key(topic: str, grade: str, language: str, version: str) -> str:
    norm = " ".join(topic.lower().split())
    return hashlib.sha256(f"{version}|{norm}|{grade}|{language}".encode()).hexdigest()


def get(key: str) -> str | None:
    with _conn() as c:
        row = c.execute("SELECT v FROM cache WHERE k=?", (key,)).fetchone()
    return row[0] if row else None


def put(key: str, value: str) -> None:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO cache VALUES (?,?,?)", (key, value, time.time()))


# in-memory per-IP limiter, only applied to requests that would call the LLM (cost protection).
# IPs are kept in RAM only, never written to disk. Use a shared store (Redis) with several servers.
_hits: dict[str, deque] = defaultdict(deque)


def allow(ip: str) -> bool:
    limit = int(os.getenv("RATE_LIMIT_PER_HOUR", "20"))
    now, q = time.time(), _hits[ip]
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= limit:
        return False
    q.append(now)
    return True
