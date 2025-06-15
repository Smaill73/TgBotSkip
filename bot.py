import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

from db import init_db

# Импорт всех хендлеров
from handlers import default_handlers, publication, viewing, advertisements

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("В файле .env не найден BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

def register_all_handlers():
    default_handlers.register(dp)
    advertisements.register(dp)
    viewing.register(dp)
    publication.register(dp)

async def set_commands():
    commands = [
        BotCommand(command="start", description="Запустить бота/Перезапуск"),
        BotCommand(command="menu", description="Главное меню"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    init_db()
    register_all_handlers()
    await set_commands()
    print("Бот успешно запущен и готов к работе!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
