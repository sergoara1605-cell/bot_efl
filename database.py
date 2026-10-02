import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "ifa.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                fighter_name TEXT DEFAULT 'Боец',
                weight_class TEXT,
                form INTEGER DEFAULT 60,
                media INTEGER DEFAULT 13,
                balance INTEGER DEFAULT 2654,
                businesses TEXT DEFAULT '[]',
                camp_gym INTEGER DEFAULT 0,
                camp_med INTEGER DEFAULT 0,
                camp_analytics INTEGER DEFAULT 0,
                trainings_today INTEGER DEFAULT 0,
                last_train_date TEXT,
                photo_file_id TEXT,
                channel_username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                result TEXT,
                opponent TEXT,
                method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_user(user_id: int, username: str | None, weight_class: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users (user_id, username, weight_class) 
               VALUES (?, ?, ?)""",
            (user_id, username, weight_class)
        )
        await db.commit()

async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        await db.commit()

async def add_fight(user_id: int, result: str, opponent: str, method: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO fights (user_id, result, opponent, method) VALUES (?, ?, ?, ?)",
            (user_id, result, opponent, method)
        )
        await db.commit()

async def get_fights(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM fights WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
