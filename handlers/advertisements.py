from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from db import get_user_ads, delete_ad_by_id, get_ad_by_id, get_username_by_user_id

router = Router()

def menu_kb():
    from handlers.default_handlers import main_menu_kb
    return main_menu_kb()

def my_ads_kb(ads):
    keyboard = []
    for i, ad in enumerate(ads, 1):
        keyboard.append([InlineKeyboardButton(text=f"{i}. {ad['title']}", callback_data=f"show_ad_{ad['id']}")])
    if ads:
        keyboard.append([InlineKeyboardButton(text="Удалить объявление", callback_data="delete_ad")])
    keyboard.append([InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def ads_index_by_id(ads, ad_id):
    for idx, ad in enumerate(ads, 1):
        if ad['id'] == ad_id:
            return idx
    return None

async def my_ads_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    ads = get_user_ads(user_id)
    if not ads:
        await callback.message.answer(
            "У вас нет активных объявлений.",
            reply_markup=menu_kb()
        )
    else:
        msg = "Ваши объявления:\n" + "\n".join([f"{i}. {ad['title']}" for i, ad in enumerate(ads, 1)])
        await callback.message.answer(msg, reply_markup=my_ads_kb(ads))

@router.callback_query(F.data.startswith("show_ad_"))
async def show_ad(callback: types.CallbackQuery):
    ad_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    ad = get_ad_by_id(ad_id, user_id)
    if not ad:
        await callback.message.answer("Объявление не найдено.")
        return

    owner_username = get_username_by_user_id(ad['user_id'])
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

@router.callback_query(F.data == "delete_ad")
async def delete_ad_choose(callback: CallbackQuery):
    user_id = callback.from_user.id
    ads = get_user_ads(user_id)
    if not ads:
        await callback.message.answer("Нет объявлений для удаления.", reply_markup=menu_kb())
        return
    buttons = [
        [InlineKeyboardButton(text=f"{i}", callback_data=f"choose_delete_{ad['id']}")]
        for i, ad in enumerate(ads, 1)
    ]
    buttons.append([InlineKeyboardButton(text="Отмена", callback_data="my_ads_cancel")])
    await callback.message.answer(
        "Выберите номер объявления для удаления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@router.callback_query(F.data.startswith("choose_delete_"))
async def delete_ad_confirm(callback: CallbackQuery):
    ad_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    ad = get_ad_by_id(ad_id, user_id)
    ads = get_user_ads(user_id)
    if not ad:
        await callback.message.answer("Объявление не найдено.", reply_markup=menu_kb())
        return
    idx = ads_index_by_id(ads, ad_id)
    text = (
        f"Вы точно хотите удалить {idx} объявление?\n"
        f"<b>{ad['title']}</b>\n{ad['description']}\nДата: {ad['dates']}\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"confirm_delete_{ad_id}")],
        [InlineKeyboardButton(text="Нет", callback_data="my_ads")]
    ])
    await callback.message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("confirm_delete_"))
async def do_delete_ad(callback: CallbackQuery):
    ad_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    delete_ad_by_id(ad_id, user_id)
    ads = get_user_ads(user_id)
    if not ads:
        await callback.message.answer("Все объявления удалены.", reply_markup=menu_kb())
    else:
        msg = "Ваши объявления:\n" + "\n".join([f"{i}. {ad['title']}" for i, ad in enumerate(ads, 1)])
        await callback.message.answer(msg, reply_markup=my_ads_kb(ads))

@router.callback_query(F.data == "my_ads")
async def cb_my_ads(callback: CallbackQuery):
    await my_ads_menu(callback)

@router.callback_query(F.data == "my_ads_cancel")
async def cb_my_ads_cancel(callback: CallbackQuery):
    await my_ads_menu(callback)

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=menu_kb())

def register(dp):
    dp.include_router(router)
