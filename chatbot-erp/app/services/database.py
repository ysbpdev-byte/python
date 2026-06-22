import os
import re
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_ALLOWED_PATTERN = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
_LIMIT_PATTERN = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)
_MAX_ROWS = 100


async def run_select(sql: str) -> list[dict]:
    if not _ALLOWED_PATTERN.match(sql):
        raise ValueError("Hanya query SELECT yang diizinkan")

    if not _LIMIT_PATTERN.search(sql):
        sql = sql.rstrip().rstrip(";") + f" LIMIT {_MAX_ROWS}"

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch(sql)
        return [dict(row) for row in rows]
    finally:
        await conn.close()
