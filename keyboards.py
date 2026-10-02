from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="⚔️ Мой бой")],
            [KeyboardButton(text="🏋️ Прокачка"), KeyboardButton(text="💼 Экономика")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="ℹ️ Помощь")],
            [KeyboardButton(text="🛒 Магазин")]
        ],
        resize_keyboard=True
    )

def weight_classes():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪶 Легчайший вес", callback_data="weight_fly")],
        [InlineKeyboardButton(text="🪶 Легкий вес", callback_data="weight_light")],
        [InlineKeyboardButton(text="⚖️ Средний вес", callback_data="weight_middle")],
        [InlineKeyboardButton(text="🏆 Тяжелый вес", callback_data="weight_heavy")]
    ])

def profile_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Изменить фото бойца", callback_data="change_photo")],
        [InlineKeyboardButton(text="🗑 Убрать фото бойца", callback_data="remove_photo")],
        [InlineKeyboardButton(text="📜 История боёв", callback_data="fight_history")]
    ])

def camp_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏋️ Тренировка ($5164)", callback_data="do_train")],
        [InlineKeyboardButton(text="🏗 Улучшения лагеря", callback_data="camp_upgrades")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_upgrade")]
    ])

def upgrades_kb(balance: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="$10 000 · 🏟 Зал → ур.1", callback_data="upgrade_gym")],
        [InlineKeyboardButton(text="$10 000 · 🩺 Медцентр → ур.1", callback_data="upgrade_med")],
        [InlineKeyboardButton(text="$10 000 · 🖥 Аналитика → ур.1", callback_data="upgrade_analytics")],
        [InlineKeyboardButton(text="⬅️ К лагерю", callback_data="back_to_camp")]
    ])

def economy_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Бизнес", callback_data="business")],
        [InlineKeyboardButton(text="📱 Медиа", callback_data="media")],
        [InlineKeyboardButton(text="🎲 Ставки", callback_data="bets")]
    ])

def business_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="$12 000 · 🥤 Точка спортпитания", callback_data="buy_nutrition")],
        [InlineKeyboardButton(text="$25 000 · ☕️ Кофейня у зала", callback_data="buy_coffee")],
        [InlineKeyboardButton(text="$60 000 · 🏋️ Зал единоборств", callback_data="buy_gym")],
        [InlineKeyboardButton(text="$120 000 · 👕 Бренд экипировки", callback_data="buy_brand")],
        [InlineKeyboardButton(text="$250 000 · 🏢 Промоушен-агентство", callback_data="buy_promo")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_economy")]
    ])

def stats_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Рейтинги", callback_data="ratings")],
        [InlineKeyboardButton(text="💰 Топ игроков", callback_data="top_players")],
        [InlineKeyboardButton(text="👕 Ростер IFA", callback_data="roster")],
        [InlineKeyboardButton(text="🔍 Поиск игрока", callback_data="search_player")]
    ])

def back_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="main_menu")]
    ])
