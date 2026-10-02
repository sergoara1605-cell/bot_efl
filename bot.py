import asyncio
import json
import random
from datetime import date
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from keyboards import (
    main_menu, weight_classes, profile_kb, camp_kb, upgrades_kb,
    economy_kb, business_kb, stats_kb, back_main
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Reg(StatesGroup):
    weight = State()


# ========== START & REGISTRATION ==========
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if user and user.get("weight_class"):
        await message.answer(
            f"С возвращением, {user.get('fighter_name', 'Боец')}!\n"
            f"Баланс: ${user['balance']}",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            "🥊 Добро пожаловать в <b>IFA</b>")
import os
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

WEBHOOK_PATH = "/webhook"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 10000))


async def on_startup(bot: Bot):
    base_url = os.getenv("RENDER_EXTERNAL_URL")

    if not base_url:
        raise RuntimeError("RENDER_EXTERNAL_URL is not set")

    webhook_url = f"{base_url}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)


async def main():
    # Создаём таблицы базы данных
    await db.init_db()

    # Создаём веб-приложение
    app = web.Application()

    # Подключаем Telegram webhook
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    webhook_requests_handler.register(
        app,
        path=WEBHOOK_PATH,
    )

    setup_application(app, dp, bot=bot)

    # Запускаем webhook
    dp.startup.register(on_startup)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        WEB_SERVER_HOST,
        WEB_SERVER_PORT,
    )

    await site.start()

    print(f"Webhook server started on port {WEB_SERVER_PORT}")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
