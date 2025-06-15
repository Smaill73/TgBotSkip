from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import add_user

router = Router()

def main_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ Мои объявления", callback_data="my_ads")],
            [InlineKeyboardButton(text="2️⃣ Просмотр объявлений", callback_data="view_ads")],
            [InlineKeyboardButton(text="3️⃣ Выложить объявление", callback_data="new_ad")],
        ]
    )

@router.message(Command("start"))
async def start_cmd(msg: types.Message):
    add_user(msg.from_user.id, msg.from_user.username or "")
    await msg.answer(
        "👋 Добро пожаловать в бота объявлений по аренде техники!\n\n"
        "Используйте меню для работы с ботом.",
        reply_markup=main_menu_kb()
    )

@router.message(Command("menu"))
async def menu_cmd(msg: types.Message):
    await msg.answer(
        "Главное меню:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "my_ads")
async def main_menu_my_ads(callback: types.CallbackQuery):
    from handlers.advertisements import my_ads_menu
    await my_ads_menu(callback)

@router.callback_query(F.data == "view_ads")
async def main_menu_view_ads(callback: types.CallbackQuery):
    from handlers.viewing import view_ads_menu
    await view_ads_menu(callback)

@router.callback_query(F.data == "new_ad")
async def main_menu_new_ad(callback: types.CallbackQuery, state: FSMContext):
    from handlers.publication import start_publication
    await start_publication(callback, state)

# --- Универсальный обработчик неизвестных сообщений вне FSM ---
@router.message(StateFilter(None))
async def unknown_message(msg: types.Message):
    await msg.answer(
        "Я не понимаю это сообщение. Пожалуйста, используйте меню или команды /menu, /start."
    )

def register(dp):
    dp.include_router(router)
