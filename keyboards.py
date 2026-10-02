from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👤 Профиль"),
                KeyboardButton(text="⚔️ Мой бой")
            ],
            [
                KeyboardButton(text="🏋️ Прокачка"),
                KeyboardButton(text="💼 Экономика")
            ],
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="ℹ️ Помощь")
            ],
            [
                KeyboardButton(text="🛒 Магазин")
            ]
        ],
        resize_keyboard=True
    )


# =========================
# ВЫБОР ВЕСОВОЙ КАТЕГОРИИ
# =========================

def weight_classes():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🪶 Легчайший вес",
                    callback_data="weight_fly"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🪶 Легкий вес",
                    callback_data="weight_light"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚖️ Средний вес",
                    callback_data="weight_middle"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Тяжелый вес",
                    callback_data="weight_heavy"
                )
            ]
        ]
    )


# =========================
# ПРОФИЛЬ
# =========================

def profile_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🖼 Изменить фото бойца",
                    callback_data="change_photo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Убрать фото бойца",
                    callback_data="remove_photo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📜 История боёв",
                    callback_data="fight_history"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# =========================
# ПРОКАЧКА / ЛАГЕРЬ
# =========================

def camp_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏋️ Тренировка",
                    callback_data="do_train"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏗 Улучшения лагеря",
                    callback_data="camp_upgrades"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# =========================
# УЛУЧШЕНИЯ ЛАГЕРЯ
# =========================

def upgrades_kb(balance: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏟 Зал — $10 000",
                    callback_data="upgrade_gym"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🩺 Медцентр — $10 000",
                    callback_data="upgrade_med"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖥 Аналитика — $10 000",
                    callback_data="upgrade_analytics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К прокачке",
                    callback_data="back_to_camp"
                )
            ]
        ]
    )


# =========================
# ЭКОНОМИКА
# =========================

def economy_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💼 Бизнес",
                    callback_data="business"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📱 Медиа",
                    callback_data="media"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎲 Ставки",
                    callback_data="bets"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# =========================
# БИЗНЕС
# =========================

def business_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🥤 Точка спортпитания — $12 000",
                    callback_data="buy_nutrition"
                )
            ],
            [
                InlineKeyboardButton(
                    text="☕️ Кофейня у зала — $25 000",
                    callback_data="buy_coffee"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏋️ Зал единоборств — $60 000",
                    callback_data="buy_gym"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👕 Бренд экипировки — $120 000",
                    callback_data="buy_brand"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏢 Промоушен-агентство — $250 000",
                    callback_data="buy_promo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ К экономике",
                    callback_data="back_economy"
                )
            ]
        ]
    )


# =========================
# СТАТИСТИКА
# =========================

def stats_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏆 Рейтинги",
                    callback_data="ratings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Топ игроков",
                    callback_data="top_players"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👕 Ростер EFL",
                    callback_data="roster"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Поиск игрока",
                    callback_data="search_player"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# =========================
# КНОПКА НАЗАД В МЕНЮ
# =========================

def back_main():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ В меню",
                    callback_data="main_menu"
                )
            ]
        ]
    )
