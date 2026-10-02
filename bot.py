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
import asyncio

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
