from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from db import get_all_hashtags, get_ads_by_hashtag, get_username_by_user_id

router = Router()

def menu_kb():
    from handlers.default_handlers import main_menu_kb
    return main_menu_kb()

def hashtags_kb(hashtags):
    keyboard = [[InlineKeyboardButton(text=ht, callback_data=f"view_tag_{ht}")] for ht in hashtags]
    keyboard.append([InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def ads_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к выбору техники", callback_data="view_ads")],
            [InlineKeyboardButton(text="В главное меню", callback_data="back_to_menu")]
        ]
    )

async def view_ads_menu(callback: CallbackQuery):
    hashtags = get_all_hashtags()
    if not hashtags:
        await callback.message.answer(
            "Пока нет ни одного объявления. Добавьте своё!",
            reply_markup=menu_kb()
        )
        return
    await callback.message.answer(
        "Выберите технику для просмотра объявлений:",
        reply_markup=hashtags_kb(hashtags)
    )

@router.callback_query(F.data.startswith("view_tag_"))
async def show_ads_by_tag(callback: CallbackQuery):
    hashtag = callback.data.removeprefix("view_tag_")
    ads = get_ads_by_hashtag(hashtag)
    if not ads:
        await callback.message.answer(
            f"Объявлений для <b>{hashtag}</b> не найдено.",
            reply_markup=ads_kb()
        )
        return

    for ad in ads:
        owner_username = get_username_by_user_id(ad["user_id"])
        if owner_username:
            contact = f"@{owner_username}"
        else:
            contact = f'<a href="tg://user?id={ad["user_id"]}">Профиль</a>'
        text = (
            f"<b>{ad['title']}</b>\n"
            f"{ad['description']}\n"
            f"Дата: {ad['dates']}\n"
            f"Стоимость: {ad['price']}\n"
            f"Связаться: {contact}\n"
        )
        try:
            await callback.message.answer_photo(ad['photo_file_id'], caption=text, parse_mode="HTML")
        except Exception:
            await callback.message.answer(text, parse_mode="HTML")

    await callback.message.answer(
        f"Конец объявлений для <b>{hashtag}</b>.",
        reply_markup=ads_kb()
    )

@router.callback_query(F.data == "view_ads")
async def cb_view_ads(callback: CallbackQuery):
    await view_ads_menu(callback)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=menu_kb())

def register(dp):
    dp.include_router(router)
