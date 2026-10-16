"""4단계 — 내 식사 기록을 SQLite 파일(lunch.db)에 남긴다. 봇을 껐다 켜도 남는다.

- sqlite3는 파이썬에 들어 있어서 따로 설치하지 않는다
- lunch.db는 Git에 올리지 않는다 (.gitignore)
- 확인: uv run pytest tests/test_db.py
"""

import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "lunch.db"


def connect(path=DB_PATH):
    """DB 파일을 열고 연결을 돌려준다.

    - 표가 없으면 만든다: meals (id INTEGER PRIMARY KEY, eaten_at TEXT, menu TEXT)
    - id는 DB가 1, 2, 3… 번호표를 붙인다 → 같은 분에 두 번 적어도 순서를 안다
    - path에 ":memory:"를 주면 파일 없이 메모리에서만 (테스트용)
    - 웹 서버(FastAPI)는 요청마다 다른 일꾼(스레드)이 처리한다 → sqlite3.connect(path, check_same_thread=False)
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS meals ("
        "id INTEGER PRIMARY KEY, eaten_at TEXT, menu TEXT)"
    )
    conn.commit()
    return conn


def now():
    """지금 한국 시간을 "2026-10-15 12:31" 모양 글자로.

    - 서버(EC2)는 UTC라서 그냥 지금 시각을 쓰면 9시간 어긋난다 → 한국 시간(UTC+9)을 직접 정한다
    - zoneinfo는 Windows에서 추가 설치가 필요해 쓰지 않는다 (datetime.timezone(timedelta(hours=9)))
    """
    korea = timezone(timedelta(hours=9))
    return datetime.now(korea).strftime("%Y-%m-%d %H:%M")


def save_meal(conn, menu, eaten_at):
    """먹은 것 한 줄을 저장한다. commit까지 해야 파일에 써진다."""
    conn.execute("INSERT INTO meals (eaten_at, menu) VALUES (?, ?)", (eaten_at, menu))
    conn.commit()


def recent_meals(conn, limit=5):
    """최근에 먹은 것을 [(먹은 시각, 메뉴), ...]로 돌려준다. 최근 것부터 limit개 (id 큰 순)."""
    rows = conn.execute(
        "SELECT eaten_at, menu FROM meals ORDER BY id DESC LIMIT ?", (limit,)
    )
    return rows.fetchall()
