import asyncio
import os
import random
from datetime import date
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
import database as db
from keyboards import (
    main_menu,
    weight_classes,
    profile_kb,
    camp_kb,
    upgrades_kb,
    economy_kb,
    business_kb,
    stats_kb,
    back_main,
)
# ============================================================
# НАСТРОЙКИ
# ============================================================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN не найден")
bot = Bot(token=TOKEN)
dp = Dispatcher(
    storage=MemoryStorage()
)
# ============================================================
# WEBHOOK
# ============================================================
WEBHOOK_PATH = "/webhook"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(
    os.getenv("PORT", 10000)
)
# ============================================================
# FSM СОСТОЯНИЯ
# ============================================================
class Reg(StatesGroup):
    weight = State()
class FighterPhoto(StatesGroup):
    waiting_photo = State()
class ChannelState(StatesGroup):
    waiting_channel = State()
class SearchPlayer(StatesGroup):
    waiting_username = State()
# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
WEIGHT_NAMES = {
    "fly": "Легчайший вес",
    "light": "Легкий вес",
    "middle": "Средний вес",
    "heavy": "Тяжелый вес",
}
def fighter_card(user):
    return (
        "🥊 ПРОФИЛЬ БОЙЦА\n\n"
        f"👤 Имя: {user.get('fighter_name', 'Боец')}\n"
        f"⚖️ Вес: {user.get('weight_class', 'Не выбран')}\n"
        f"❤️ Форма: {user.get('form', 60)}/100\n"
        f"📱 Медиа: {user.get('media', 13)}\n\n"
        "🏆 РЕКОРД\n"
        f"Победы: {user.get('wins', 0)}\n"
        f"Поражения: {user.get('losses', 0)}\n"
        f"Ничьи: {user.get('draws', 0)}\n\n"
        "💥 ПОБЕДЫ ПО МЕТОДУ\n"
        f"KO: {user.get('ko_wins', 0)}\n"
        f"TKO: {user.get('tko_wins', 0)}\n"
        f"SUB: {user.get('sub_wins', 0)}\n"
        f"DEC: {user.get('dec_wins', 0)}\n\n"
        f"💰 Баланс: ${user.get('balance', 0):,}"
    )
async def ensure_user(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return False
    return True
# ============================================================
# START
# ============================================================
@dp.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext
):
    await state.clear()
    user = await db.get_user(
        message.from_user.id
    )
    if user and user.get("weight_class"):
        await message.answer(
            f"🥊 С возвращением, "
            f"{user.get('fighter_name', 'Боец')}!\n\n"
            f"🏆 Добро пожаловать в EFL\n"
            f"💰 Баланс: ${user['balance']:,}",
            reply_markup=main_menu()
        )
        return
    await message.answer(
        "🥊 ДОБРО ПОЖАЛОВАТЬ В EFL!\n\n"
        "Elite Fighting League — твоя карьера бойца.\n\n"
        "Выбери свою весовую категорию:",
        reply_markup=weight_classes()
    )
    await state.set_state(
        Reg.weight
    )
# ============================================================
# ВЫБОР ВЕСОВОЙ КАТЕГОРИИ
# ============================================================
@dp.callback_query(
    F.data.startswith("weight_")
)
async def choose_weight(
    callback: CallbackQuery,
    state: FSMContext
):
    weight_code = callback.data.replace(
        "weight_",
        ""
    )
    weight_name = WEIGHT_NAMES.get(
        weight_code
    )
    if not weight_name:
        await callback.answer(
            "Неизвестная категория"
        )
        return
    await db.create_user(
        callback.from_user.id,
        callback.from_user.username,
        weight_name
    )
    await state.clear()
    await callback.message.edit_text(
        "🥊 Регистрация завершена!\n\n"
        f"⚖️ Весовая категория: {weight_name}\n"
        "❤️ Форма: 60/100\n"
        "💰 Стартовый баланс: $2,654\n\n"
        "Добро пожаловать в EFL!"
    )
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu()
    )
    await callback.answer()
# ============================================================
# ПРОФИЛЬ
# ============================================================
@dp.message(F.text == "👤 Профиль")
async def profile(
    message: Message
):
    user = await db.get_user(
        message.from_user.id
    )
    if not user:
        await message.answer(
            "Сначала выполни регистрацию через /start."
        )
        return
    await message.answer(
        fighter_card(user),
        reply_markup=profile_kb()
    )
# ============================================================
# ФОТО БОЙЦА
# ============================================================
@dp.callback_query(
    F.data == "change_photo"
)
async def change_photo(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "🖼 Отправь фотографию, "
        "которую хочешь установить в профиль."
    )
    await state.set_state(
        FighterPhoto.waiting_photo
    )
    await callback.answer()
@dp.message(
    FighterPhoto.waiting_photo,
    F.photo
)
async def receive_photo(
    message: Message,
    state: FSMContext
):
    photo = message.photo[-1]
    await db.update_user(
        message.from_user.id,
        photo_file_id=photo.file_id
    )
    await state.clear()
    await message.answer(
        "✅ Фото бойца обновлено!",
        reply_markup=main_menu()
    )
@dp.callback_query(
    F.data == "remove_photo"
)
async def remove_photo(
    callback: CallbackQuery
):
    await db.update_user(
        callback.from_user.id,
        photo_file_id=None
    )
    await callback.answer(
        "Фото удалено"
    )
    await callback.message.answer(
        "🗑 Фото бойца удалено."
    )
# ============================================================
# ИСТОРИЯ БОЁВ
# ============================================================
@dp.callback_query(
    F.data == "fight_history"
)
async def fight_history(
    callback: CallbackQuery
):
    fights = await db.get_fights(
        callback.from_user.id,
        10
    )
    if not fights:
        text = (
            "📜 ИСТОРИЯ БОЁВ\n\n"
            "У тебя пока нет проведённых боёв."
        )
    else:
        text = "📜 ИСТОРИЯ БОЁВ\n\n"
        for fight in fights:
            text += (
                f"⚔️ Противник: "
                f"{fight['opponent']}\n"
                f"Результат: {fight['result']}\n"
                f"Метод: {fight['method']}\n"
                f"Счёт: "
                f"{fight['user_score']}:"
                f"{fight['opponent_score']}\n"
                "────────────\n"
            )
    await callback.message.answer(
        text,
        reply_markup=back_main()
    )
    await callback.answer()
# ============================================================
# ПРОКАЧКА
# ============================================================
@dp.message(F.text == "🏋️ Прокачка")
async def camp(
    message: Message
):
    user = await db.get_user(
        message.from_user.id
    )
    if not user:
        return
    await message.answer(
        "🏕 ТРЕНИРОВОЧНЫЙ ЛАГЕРЬ\n\n"
        f"❤️ Форма: {user['form']}/100\n"
        f"🏋️ Тренировок сегодня: "
        f"{user['trainings_today']}/5\n\n"
        "Развивай бойца и улучшай лагерь.",
        reply_markup=camp_kb()
    )
# ============================================================
# ТРЕНИРОВКА
# ============================================================
@dp.callback_query(
    F.data == "do_train"
)
async def do_train(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    if not user:
        await callback.answer(
            "Пользователь не найден"
        )
        return
    success = await db.add_training(
        callback.from_user.id
    )
    if not success:
        await callback.answer(
            "Лимит тренировок на сегодня: 5",
            show_alert=True
        )
        return
    gain = random.randint(3, 8)
    await db.change_form(
        callback.from_user.id,
        gain
    )
    user = await db.get_user(
        callback.from_user.id
    )
    await callback.message.answer(
        "🏋️ ТРЕНИРОВКА ЗАВЕРШЕНА!\n\n"
        f"📈 Форма: +{gain}\n"
        f"❤️ Текущая форма: "
        f"{user['form']}/100\n"
        f"🔥 Сегодня: "
        f"{user['trainings_today']}/5"
    )
    await callback.answer()
# ============================================================
# УЛУЧШЕНИЯ ЛАГЕРЯ
# ============================================================
@dp.callback_query(
    F.data == "camp_upgrades"
)
async def camp_upgrades(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    await callback.message.answer(
        "🏗 УЛУЧШЕНИЯ ЛАГЕРЯ\n\n"
        f"🏟 Зал: ур. {user['camp_gym']}\n"
        f"🩺 Медцентр: ур. {user['camp_med']}\n"
        f"🖥 Аналитика: ур. "
        f"{user['camp_analytics']}\n\n"
        f"💰 Баланс: ${user['balance']:,}",
        reply_markup=upgrades_kb(
            user["balance"]
        )
    )
    await callback.answer()
async def process_upgrade(
    callback: CallbackQuery,
    upgrade: str,
    name: str
):
    success = await db.upgrade_camp(
        callback.from_user.id,
        upgrade
    )
    if not success:
        await callback.answer(
            "Недостаточно денег или достигнут максимальный уровень.",
            show_alert=True
        )
        return
    user = await db.get_user(
        callback.from_user.id
    )
    await callback.message.answer(
        f"✅ {name} улучшен!\n\n"
        f"💰 Баланс: ${user['balance']:,}"
    )
    await callback.answer()
@dp.callback_query(
    F.data == "upgrade_gym"
)
async def upgrade_gym(
    callback: CallbackQuery
):
    await process_upgrade(
        callback,
        "gym",
        "🏟 Зал"
    )
@dp.callback_query(
    F.data == "upgrade_med"
)
async def upgrade_med(
    callback: CallbackQuery
):
    await process_upgrade(
        callback,
        "med",
        "🩺 Медцентр"
    )
@dp.callback_query(
    F.data == "upgrade_analytics"
)
async def upgrade_analytics(
    callback: CallbackQuery
):
    await process_upgrade(
        callback,
        "analytics",
        "🖥 Аналитика"
    )
# ============================================================
# ЭКОНОМИКА
# ============================================================
@dp.message(F.text == "💼 Экономика")
async def economy(
    message: Message
):
    user = await db.get_user(
        message.from_user.id
    )
    await message.answer(
        "💼 ЭКОНОМИКА EFL\n\n"
        f"💰 Баланс: ${user['balance']:,}\n\n"
        "Развивай бизнес, медиа и управляй деньгами.",
        reply_markup=economy_kb()
    )
# ============================================================
# БИЗНЕС
# ============================================================
@dp.callback_query(
    F.data == "business"
)
async def business(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    businesses = user["businesses"]
    text = (
        "💼 БИЗНЕС\n\n"
        f"💰 Баланс: ${user['balance']:,}\n\n"
    )
    if businesses:
        text += "Твои бизнесы:\n"
        for item in businesses:
            text += f"• {item}\n"
    else:
        text += "У тебя пока нет бизнеса.\n"
    await callback.message.answer(
        text,
        reply_markup=business_kb()
    )
    await callback.answer()
BUSINESSES = {
    "buy_nutrition": (
        "🥤 Точка спортпитания",
        "nutrition",
        12000
    ),
    "buy_coffee": (
        "☕️ Кофейня у зала",
        "coffee",
        25000
    ),
    "buy_gym": (
        "🏋️ Зал единоборств",
        "fight_gym",
        60000
    ),
    "buy_brand": (
        "👕 Бренд экипировки",
        "brand",
        120000
    ),
    "buy_promo": (
        "🏢 Промоушен-агентство",
        "promo",
        250000
    ),
}
@dp.callback_query(
    F.data.in_(BUSINESSES.keys())
)
async def buy_business(
    callback: CallbackQuery
):
    name, code, price = BUSINESSES[
        callback.data
    ]
    user = await db.get_user(
        callback.from_user.id
    )
    if user["balance"] < price:
        await callback.answer(
            "Недостаточно денег.",
            show_alert=True
        )
        return
    if await db.has_business(
        callback.from_user.id,
        code
    ):
        await callback.answer(
            "Этот бизнес уже куплен.",
            show_alert=True
        )
        return
    await db.remove_balance(
        callback.from_user.id,
        price
    )
    await db.add_business(
        callback.from_user.id,
        code
    )
    await callback.message.answer(
        f"✅ Бизнес куплен!\n\n"
        f"{name}\n"
        f"💵 Цена: ${price:,}"
    )
    await callback.answer()
# ============================================================
# МЕДИА
# ============================================================
@dp.callback_query(
    F.data == "media"
)
async def media(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    channel = user.get(
        "channel_username"
    )
    if channel:
        channel_text = (
            f"📺 Канал: {channel}\n"
            f"👥 Подписчики: "
            f"{user['channel_subscribers']:,}\n"
            f"👁 Просмотры: "
            f"{user['channel_views']:,}\n"
            f"❤️ Реакции: "
            f"{user['channel_reactions']:,}"
        )
    else:
        channel_text = (
            "📺 Канал ещё не привязан."
        )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📺 Привязать канал",
                    callback_data="link_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Получить выплату",
                    callback_data="media_payout"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_economy"
                )
            ]
        ]
    )
    await callback.message.answer(
        "📱 МЕДИА EFL\n\n"
        + channel_text,
        reply_markup=keyboard
    )
    await callback.answer()
@dp.callback_query(
    F.data == "link_channel"
)
async def link_channel(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "📺 Отправь username своего Telegram-канала.\n\n"
        "Например: @my_channel"
    )
    await state.set_state(
        ChannelState.waiting_channel
    )
    await callback.answer()
@dp.message(
    ChannelState.waiting_channel
)
async def receive_channel(
    message: Message,
    state: FSMContext
):
    channel = message.text.strip()
    if not channel.startswith("@"):
        channel = "@" + channel
    await db.set_channel(
        message.from_user.id,
        channel
    )
    await state.clear()
    await message.answer(
        f"✅ Канал {channel} привязан к профилю EFL."
    )
@dp.callback_query(
    F.data == "media_payout"
)
async def media_payout(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    if not user.get("channel_username"):
        await callback.answer(
            "Сначала привяжи канал.",
            show_alert=True
        )
        return
    views = user["channel_views"]
    payout = max(
        0,
        views // 100
    )
    if payout == 0:
        payout = 100
    await db.save_media_payout(
        callback.from_user.id,
        payout
    )
    await callback.message.answer(
        "💰 МЕДИА-ВЫПЛАТА\n\n"
        f"👁 Просмотры: {views:,}\n"
        f"💵 Выплата: ${payout:,}"
    )
    await callback.answer()
# ============================================================
# МОЙ БОЙ
# ============================================================
@dp.message(F.text == "⚔️ Мой бой")
async def my_fight(
    message: Message
):
    user = await db.get_user(
        message.from_user.id
    )
    if not user:
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ Начать бой",
                    callback_data="start_fight"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📜 История",
                    callback_data="fight_history"
                )
            ]
        ]
    )
    await message.answer(
        "⚔️ МОЙ БОЙ\n\n"
        f"🥊 Боец: {user['fighter_name']}\n"
        f"❤️ Форма: {user['form']}/100\n"
        f"🏆 Рекорд: "
        f"{user['wins']}-"
        f"{user['losses']}-"
        f"{user['draws']}",
        reply_markup=keyboard
    )
# ============================================================
# СИМУЛЯЦИЯ БОЯ
# ============================================================
@dp.callback_query(
    F.data == "start_fight"
)
async def start_fight(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    if not user:
        return
    opponents = [
        "Макс Волков",
        "Алекс Романов",
        "Илья Орлов",
        "Данил Ковалёв",
        "Артур Смирнов",
    ]
    opponent = random.choice(
        opponents
    )
    user_power = (
        user["form"]
        + user["camp_gym"] * 5
        + random.randint(1, 30)
    )
    opponent_power = random.randint(
        40,
        110
    )
    if user_power > opponent_power:
        methods = [
            "KO",
            "TKO",
            "SUB",
            "DEC"
        ]
        method = random.choice(
            methods
        )
        await db.add_win(
            callback.from_user.id,
            method
        )
        await db.add_fight(
            callback.from_user.id,
            "Победа",
            opponent,
            method,
            user_power,
            opponent_power
        )
        result = (
            "🏆 ПОБЕДА!\n\n"
            f"🥊 Противник: {opponent}\n"
            f"💥 Метод: {method}\n"
            f"📊 Счёт: "
            f"{user_power}:{opponent_power}"
        )
    elif user_power < opponent_power:
        await db.add_loss(
            callback.from_user.id
        )
        await db.add_fight(
            callback.from_user.id,
            "Поражение",
            opponent,
            "DEC",
            user_power,
            opponent_power
        )
        result = (
            "❌ ПОРАЖЕНИЕ\n\n"
            f"🥊 Противник: {opponent}\n"
            f"📊 Счёт: "
            f"{user_power}:{opponent_power}"
        )
    else:
        await db.add_draw(
            callback.from_user.id
        )
        await db.add_fight(
            callback.from_user.id,
            "Ничья",
            opponent,
            "DEC",
            user_power,
            opponent_power
        )
        result = (
            "🤝 НИЧЬЯ\n\n"
            f"🥊 Противник: {opponent}\n"
            f"📊 Счёт: "
            f"{user_power}:{opponent_power}"
        )
    await callback.message.answer(
        result
    )
    await callback.answer()
# ============================================================
# СТАТИСТИКА
# ============================================================
@dp.message(F.text == "📊 Статистика")
async def statistics(
    message: Message
):
    await message.answer(
        "📊 СТАТИСТИКА EFL\n\n"
        "Выбери раздел:",
        reply_markup=stats_kb()
    )
@dp.callback_query(
    F.data == "ratings"
)
async def ratings(
    callback: CallbackQuery
):
    players = await db.get_top_players(
        10
    )
    text = "🏆 РЕЙТИНГ EFL\n\n"
    if not players:
        text += "Пока нет игроков."
    else:
        for index, player in enumerate(
            players,
            start=1
        ):
            text += (
                f"{index}. "
                f"{player['fighter_name']} — "
                f"{player['wins']} побед\n"
            )
    await callback.message.answer(
        text,
        reply_markup=back_main()
    )
    await callback.answer()
@dp.callback_query(
    F.data == "top_players"
)
async def top_players(
    callback: CallbackQuery
):
    players = await db.get_top_players(
        10
    )
    text = "💰 ТОП ИГРОКОВ EFL\n\n"
    for index, player in enumerate(
        players,
        start=1
    ):
        text += (
            f"{index}. "
            f"{player['fighter_name']} — "
            f"${player['balance']:,}\n"
        )
    await callback.message.answer(
        text,
        reply_markup=back_main()
    )
    await callback.answer()
@dp.callback_query(
    F.data == "roster"
)
async def roster(
    callback: CallbackQuery
):
    players = await db.get_top_players(
        20
    )
    text = "👕 РОСТЕР EFL\n\n"
    if not players:
        text += "Ростер пока пуст."
    else:
        for player in players:
            text += (
                f"🥊 {player['fighter_name']}\n"
                f"⚖️ {player['weight_class']}\n"
                f"🏆 {player['wins']}-"
                f"{player['losses']}-"
                f"{player['draws']}\n\n"
            )
    await callback.message.answer(
        text,
        reply_markup=back_main()
    )
    await callback.answer()
# ============================================================
# ПОИСК ИГРОКА
# ============================================================
@dp.callback_query(
    F.data == "search_player"
)
async def search_player(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.answer(
        "🔍 Отправь username игрока.\n\n"
        "Например: @fighter"
    )
    await state.set_state(
        SearchPlayer.waiting_username
    )
    await callback.answer()
@dp.message(
    SearchPlayer.waiting_username
)
async def search_player_result(
    message: Message,
    state: FSMContext
):
    username = message.text.strip()
    user = await db.find_user_by_username(
        username
    )
    await state.clear()
    if not user:
        await message.answer(
            "❌ Игрок не найден."
        )
        return
    await message.answer(
        "🔍 ИГРОК НАЙДЕН\n\n"
        f"🥊 {user['fighter_name']}\n"
        f"⚖️ {user['weight_class']}\n"
        f"🏆 Рекорд: "
        f"{user['wins']}-"
        f"{user['losses']}-"
        f"{user['draws']}\n"
        f"❤️ Форма: {user['form']}/100"
    )
# ============================================================
# ПОМОЩЬ
# ============================================================
@dp.message(F.text == "ℹ️ Помощь")
async def help_message(
    message: Message
):
    await message.answer(
        "ℹ️ ПОМОЩЬ EFL\n\n"
        "👤 Профиль — информация о бойце.\n"
        "🏋️ Прокачка — тренировки и лагерь.\n"
        "💼 Экономика — деньги и бизнес.\n"
        "⚔️ Мой бой — проведение боёв.\n"
        "📊 Статистика — рейтинги и ростер.\n"
        "🛒 Магазин — покупки и улучшения.\n\n"
        "EFL — твоя карьера бойца."
    )
# ============================================================
# МАГАЗИН
# ============================================================
@dp.message(F.text == "🛒 Магазин")
async def shop(
    message: Message
):
    user = await db.get_user(
        message.from_user.id
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💪 Восстановление формы — $2 000",
                    callback_data="shop_form"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❤️ Полное восстановление — $5 000",
                    callback_data="shop_full_form"
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
    await message.answer(
        "🛒 МАГАЗИН EFL\n\n"
        f"💰 Баланс: ${user['balance']:,}",
        reply_markup=keyboard
    )
@dp.callback_query(
    F.data == "shop_form"
)
async def shop_form(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    if user["balance"] < 2000:
        await callback.answer(
            "Недостаточно денег.",
            show_alert=True
        )
        return
    await db.remove_balance(
        callback.from_user.id,
        2000
    )
    await db.change_form(
        callback.from_user.id,
        10
    )
    await callback.message.answer(
        "💪 Форма восстановлена на +10."
    )
    await callback.answer()
@dp.callback_query(
    F.data == "shop_full_form"
)
async def shop_full_form(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    if user["balance"] < 5000:
        await callback.answer(
            "Недостаточно денег.",
            show_alert=True
        )
        return
    await db.remove_balance(
        callback.from_user.id,
        5000
    )
    await db.update_user(
        callback.from_user.id,
        form=100
    )
    await callback.message.answer(
        "❤️ Форма полностью восстановлена: 100/100."
    )
    await callback.answer()
# ============================================================
# КНОПКА ГЛАВНОГО МЕНЮ
# ============================================================
@dp.callback_query(
    F.data == "main_menu"
)
async def callback_main_menu(
    callback: CallbackQuery
):
    await callback.message.answer(
        "🏠 Главное меню EFL:",
        reply_markup=main_menu()
    )
    await callback.answer()
# ============================================================
# НАЗАД К ПРОКАЧКЕ
# ============================================================
@dp.callback_query(
    F.data == "back_to_camp"
)
async def back_to_camp(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    await callback.message.answer(
        "🏕 ТРЕНИРОВОЧНЫЙ ЛАГЕРЬ\n\n"
        f"❤️ Форма: {user['form']}/100\n"
        f"🏋️ Сегодня: "
        f"{user['trainings_today']}/5",
        reply_markup=camp_kb()
    )
    await callback.answer()
@dp.callback_query(
    F.data == "back_to_upgrade"
)
async def back_to_upgrade(
    callback: CallbackQuery
):
    await callback_main_menu(
        callback
    )
# ============================================================
# НАЗАД К ЭКОНОМИКЕ
# ============================================================
@dp.callback_query(
    F.data == "back_economy"
)
async def back_economy(
    callback: CallbackQuery
):
    user = await db.get_user(
        callback.from_user.id
    )
    await callback.message.answer(
        "💼 ЭКОНОМИКА EFL\n\n"
        f"💰 Баланс: ${user['balance']:,}",
        reply_markup=economy_kb()
    )
    await callback.answer()
# ============================================================
# СТАВКИ
# ============================================================
@dp.callback_query(
    F.data == "bets"
)
async def bets(
    callback: CallbackQuery
):
    await callback.message.answer(
        "🎲 СТАВКИ\n\n"
        "Раздел ставок будет подключён "
        "к системе турниров EFL."
    )
    await callback.answer()
# ============================================================
# ЕЖЕДНЕВНОЕ ОБНОВЛЕНИЕ
# ============================================================
async def daily_update():
    while True:
        try:
            await asyncio.sleep(86400)
        except asyncio.CancelledError:
            break
# ============================================================
# WEBHOOK STARTUP
# ============================================================
async def on_startup(
    bot: Bot
):
    base_url = os.getenv(
        "RENDER_EXTERNAL_URL"
    )
    if not base_url:
        raise RuntimeError(
            "RENDER_EXTERNAL_URL is not set"
        )
    webhook_url = (
        f"{base_url}{WEBHOOK_PATH}"
    )
    await bot.set_webhook(
        webhook_url
    )
    print(
        f"Webhook установлен: {webhook_url}"
    )
# ============================================================
# MAIN
# ============================================================
async def main():
    # Инициализация базы
    await db.init_db()
    # Создаём приложение
    app = web.Application()
    # Telegram webhook
    webhook_requests_handler = (
        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
    )
    webhook_requests_handler.register(
        app,
        path=WEBHOOK_PATH,
    )
    setup_application(
        app,
        dp,
        bot=bot
    )
    # Startup
    dp.startup.register(
        on_startup
    )
    # Web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        WEB_SERVER_HOST,
        WEB_SERVER_PORT
    )
    await site.start()
    print(
        f"EFL webhook server started "
        f"on port {WEB_SERVER_PORT}"
    )
    # Бесконечная работа
    while True:
        await asyncio.sleep(3600)
# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    asyncio.run(main())
