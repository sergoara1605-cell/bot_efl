import json
import aiosqlite
from pathlib import Path
from datetime import datetime, date


# ============================================================
# НАСТРОЙКИ БАЗЫ
# ============================================================

DB_PATH = Path(__file__).parent / "ifa.db"


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def today():
    return date.today().isoformat()


def now():
    return datetime.now().isoformat(timespec="seconds")


def businesses_to_json(businesses):
    if businesses is None:
        return "[]"

    if isinstance(businesses, str):
        return businesses

    return json.dumps(businesses, ensure_ascii=False)


def businesses_from_json(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []


# ============================================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# ============================================================

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

                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,

                ko_wins INTEGER DEFAULT 0,
                tko_wins INTEGER DEFAULT 0,
                sub_wins INTEGER DEFAULT 0,
                dec_wins INTEGER DEFAULT 0,

                businesses TEXT DEFAULT '[]',

                camp_gym INTEGER DEFAULT 0,
                camp_med INTEGER DEFAULT 0,
                camp_analytics INTEGER DEFAULT 0,

                trainings_today INTEGER DEFAULT 0,
                last_train_date TEXT,

                photo_file_id TEXT,

                channel_username TEXT,
                channel_subscribers INTEGER DEFAULT 0,
                channel_views INTEGER DEFAULT 0,
                channel_reactions INTEGER DEFAULT 0,

                active_fight_id INTEGER DEFAULT NULL,

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

                user_score INTEGER DEFAULT 0,
                opponent_score INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,
                business_type TEXT,

                level INTEGER DEFAULT 1,

                income INTEGER DEFAULT 0,
                risk INTEGER DEFAULT 0,

                last_payout TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                amount INTEGER,
                prediction TEXT,
                result TEXT,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS media_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,

                subscribers INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                reactions INTEGER DEFAULT 0,
                payout INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
            )
        """)

        await db.commit()


# ============================================================
# ПОЛЬЗОВАТЕЛИ
# ============================================================

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:

            row = await cursor.fetchone()

            if not row:
                return None

            user = dict(row)

            user["businesses"] = businesses_from_json(
                user.get("businesses")
            )

            return user


async def create_user(
    user_id: int,
    username: str | None,
    weight_class: str
):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT OR IGNORE INTO users (
                user_id,
                username,
                weight_class
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                username,
                weight_class
            )
        )

        await db.commit()


async def update_user(user_id: int, **kwargs):

    if not kwargs:
        return

    if "businesses" in kwargs:
        kwargs["businesses"] = businesses_to_json(
            kwargs["businesses"]
        )

    fields = ", ".join(
        f"{key} = ?"
        for key in kwargs.keys()
    )

    values = list(kwargs.values())
    values.append(user_id)

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            f"""
            UPDATE users
            SET {fields}
            WHERE user_id = ?
            """,
            values
        )

        await db.commit()


# ============================================================
# БАЛАНС
# ============================================================

async def get_balance(user_id: int):
    user = await get_user(user_id)

    if not user:
        return 0

    return user["balance"]


async def add_balance(user_id: int, amount: int):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?
            WHERE user_id = ?
            """,
            (
                amount,
                user_id
            )
        )

        await db.commit()


async def remove_balance(user_id: int, amount: int):

    async with aiosqlite.connect(DB_PATH) as db:

        cursor = await db.execute(
            """
            UPDATE users
            SET balance = balance - ?
            WHERE user_id = ?
              AND balance >= ?
            """,
            (
                amount,
                user_id,
                amount
            )
        )

        await db.commit()

        return cursor.rowcount > 0


# ============================================================
# ТРЕНИРОВКИ
# ============================================================

async def reset_training_if_needed(user_id: int):

    user = await get_user(user_id)

    if not user:
        return

    current_day = today()

    if user["last_train_date"] != current_day:

        await update_user(
            user_id,
            trainings_today=0,
            last_train_date=current_day
        )


async def get_trainings_today(user_id: int):

    await reset_training_if_needed(user_id)

    user = await get_user(user_id)

    if not user:
        return 0

    return user["trainings_today"]


async def add_training(user_id: int):

    await reset_training_if_needed(user_id)

    user = await get_user(user_id)

    if not user:
        return False

    if user["trainings_today"] >= 5:
        return False

    await update_user(
        user_id,
        trainings_today=user["trainings_today"] + 1,
        last_train_date=today()
    )

    return True


# ============================================================
# ФОРМА
# ============================================================

async def change_form(user_id: int, amount: int):

    user = await get_user(user_id)

    if not user:
        return

    new_form = user["form"] + amount

    new_form = max(
        0,
        min(100, new_form)
    )

    await update_user(
        user_id,
        form=new_form
    )


# ============================================================
# ИСТОРИЯ БОЁВ
# ============================================================

async def add_fight(
    user_id: int,
    result: str,
    opponent: str,
    method: str,
    user_score: int = 0,
    opponent_score: int = 0
):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT INTO fights (
                user_id,
                result,
                opponent,
                method,
                user_score,
                opponent_score
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                result,
                opponent,
                method,
                user_score,
                opponent_score
            )
        )

        await db.commit()


async def get_fights(
    user_id: int,
    limit: int = 10
):

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM fights
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        ) as cursor:

            rows = await cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]


# ============================================================
# СТАТИСТИКА БОЙЦА
# ============================================================

async def add_win(
    user_id: int,
    method: str
):

    user = await get_user(user_id)

    if not user:
        return

    values = {
        "wins": user["wins"] + 1
    }

    if method == "KO":
        values["ko_wins"] = user["ko_wins"] + 1

    elif method == "TKO":
        values["tko_wins"] = user["tko_wins"] + 1

    elif method == "SUB":
        values["sub_wins"] = user["sub_wins"] + 1

    elif method == "DEC":
        values["dec_wins"] = user["dec_wins"] + 1

    await update_user(
        user_id,
        **values
    )


async def add_loss(user_id: int):

    user = await get_user(user_id)

    if not user:
        return

    await update_user(
        user_id,
        losses=user["losses"] + 1
    )


async def add_draw(user_id: int):

    user = await get_user(user_id)

    if not user:
        return

    await update_user(
        user_id,
        draws=user["draws"] + 1
    )


# ============================================================
# БИЗНЕСЫ
# ============================================================

async def get_businesses(user_id: int):

    user = await get_user(user_id)

    if not user:
        return []

    return user["businesses"]


async def add_business(
    user_id: int,
    business_type: str
):

    businesses = await get_businesses(user_id)

    if business_type in businesses:
        return False

    businesses.append(business_type)

    await update_user(
        user_id,
        businesses=businesses
    )

    return True


async def has_business(
    user_id: int,
    business_type: str
):

    businesses = await get_businesses(user_id)

    return business_type in businesses


# ============================================================
# УЛУЧШЕНИЯ ЛАГЕРЯ
# ============================================================

async def upgrade_camp(
    user_id: int,
    upgrade: str
):

    user = await get_user(user_id)

    if not user:
        return False

    allowed = {
        "gym": "camp_gym",
        "med": "camp_med",
        "analytics": "camp_analytics"
    }

    field = allowed.get(upgrade)

    if not field:
        return False

    current_level = user[field]

    if current_level >= 5:
        return False

    price = 10000 * (current_level + 1)

    if user["balance"] < price:
        return False

    await update_user(
        user_id,
        balance=user["balance"] - price,
        **{
            field: current_level + 1
        }
    )

    return True


# ============================================================
# МЕДИА
# ============================================================

async def update_media(
    user_id: int,
    subscribers: int | None = None,
    views: int | None = None,
    reactions: int | None = None
):

    user = await get_user(user_id)

    if not user:
        return

    data = {}

    if subscribers is not None:
        data["channel_subscribers"] = subscribers

    if views is not None:
        data["channel_views"] = views

    if reactions is not None:
        data["channel_reactions"] = reactions

    if data:
        await update_user(
            user_id,
            **data
        )


async def save_media_payout(
    user_id: int,
    payout: int
):

    await add_balance(
        user_id,
        payout
    )

    async with aiosqlite.connect(DB_PATH) as db:

        user = await get_user(user_id)

        await db.execute(
            """
            INSERT INTO media_stats (
                user_id,
                subscribers,
                views,
                reactions,
                payout
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user["channel_subscribers"],
                user["channel_views"],
                user["channel_reactions"],
                payout
            )
        )

        await db.commit()


# ============================================================
# СТАВКИ
# ============================================================

async def create_bet(
    user_id: int,
    amount: int,
    prediction: str
):

    success = await remove_balance(
        user_id,
        amount
    )

    if not success:
        return False

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            """
            INSERT INTO bets (
                user_id,
                amount,
                prediction
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                amount,
                prediction
            )
        )

        await db.commit()

    return True


async def finish_bet(
    bet_id: int,
    result: str
):

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM bets
            WHERE id = ?
            """,
            (bet_id,)
        ) as cursor:

            row = await cursor.fetchone()

        if not row:
            return False

        await db.execute(
            """
            UPDATE bets
            SET result = ?
            WHERE id = ?
            """,
            (
                result,
                bet_id
            )
        )

        await db.commit()

    return True


# ============================================================
# РЕЙТИНГ
# ============================================================

async def get_top_players(limit: int = 10):

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM users
            ORDER BY wins DESC, balance DESC
            LIMIT ?
            """,
            (limit,)
        ) as cursor:

            rows = await cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]


# ============================================================
# ПОИСК ИГРОКА
# ============================================================

async def find_user_by_username(
    username: str
):

    username = username.lstrip("@")

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(username) = LOWER(?)
            LIMIT 1
            """,
            (username,)
        ) as cursor:

            row = await cursor.fetchone()

            if not row:
                return None

            user = dict(row)

            user["businesses"] = businesses_from_json(
                user.get("businesses")
            )

            return user


# ============================================================
# КАНАЛ БОЙЦА
# ============================================================

async def set_channel(
    user_id: int,
    channel_username: str
):

    await update_user(
        user_id,
        channel_username=channel_username
    )


async def remove_channel(user_id: int):

    await update_user(
        user_id,
        channel_username=None,
        channel_subscribers=0,
        channel_views=0,
        channel_reactions=0
    )


# ============================================================
# АКТИВНЫЙ БОЙ
# ============================================================

async def set_active_fight(
    user_id: int,
    fight_id: int | None
):

    await update_user(
        user_id,
        active_fight_id=fight_id
    )


async def get_active_fight(user_id: int):

    user = await get_user(user_id)

    if not user:
        return None

    fight_id = user.get("active_fight_id")

    if not fight_id:
        return None

    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM fights
            WHERE id = ?
            """,
            (fight_id,)
        ) as cursor:

            row = await cursor.fetchone()

            return dict(row) if row else None
