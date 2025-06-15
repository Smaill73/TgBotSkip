from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from db import add_advertisement

router = Router()

class PublicationFSM(StatesGroup):
    title = State()
    description = State()
    dates = State()
    price = State()
    photo = State()
    confirm = State()

def menu_kb():
    from handlers.default_handlers import main_menu_kb
    return main_menu_kb()

def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выложить объявление", callback_data="publish_confirm")],
            [InlineKeyboardButton(text="Изменить объявление", callback_data="publish_edit")],
            [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
        ]
    )

async def start_publication(callback: CallbackQuery, state: FSMContext):
    # Проверка наличия username
    if not callback.from_user.username:
        await callback.message.answer(
            "❗️ Для публикации объявления необходимо создать никнейм (@username) в настройках Telegram.\n"
            "Пожалуйста, добавьте никнейм и повторите попытку."
        )
        await state.clear()
        return

    await state.clear()
    await callback.message.answer("Введите название техники (например: кран):")
    await state.set_state(PublicationFSM.title)

@router.message(PublicationFSM.title)
async def set_title(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text.strip())
    await msg.answer("Введите описание (например: 25 тонн):")
    await state.set_state(PublicationFSM.description)

@router.message(PublicationFSM.description)
async def set_description(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text.strip())
    await msg.answer("Введите срок сдачи (например: 07.10.25-16.10.25):")
    await state.set_state(PublicationFSM.dates)

@router.message(PublicationFSM.dates)
async def set_dates(msg: Message, state: FSMContext):
    await state.update_data(dates=msg.text.strip())
    await msg.answer("Введите цену (например: 10000р за сутки):")
    await state.set_state(PublicationFSM.price)

@router.message(PublicationFSM.price)
async def set_price(msg: Message, state: FSMContext):
    await state.update_data(price=msg.text.strip())
    await msg.answer("Отправьте фото техники:")
    await state.set_state(PublicationFSM.photo)

@router.message(PublicationFSM.photo, F.photo)
async def set_photo(msg: Message, state: FSMContext):
    photo_file_id = msg.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    data = await state.get_data()
    preview = (
        f"<b>{data['title']}</b>\n"
        f"{data['description']}\n"
        f"Дата: {data['dates']}\n"
        f"Стоимость: {data['price']}\n"
        f"Связаться: @{msg.from_user.username}\n"
    )
    await msg.answer_photo(
        photo_file_id,
        caption=preview,
        reply_markup=confirm_kb()
    )
    await state.set_state(PublicationFSM.confirm)

@router.message(PublicationFSM.photo)
async def not_photo(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, отправьте именно фото техники.")

@router.callback_query(PublicationFSM.confirm, F.data == "publish_confirm")
async def confirm_publication(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    hashtag = data['title'].lower()
    add_advertisement(
        user_id=callback.from_user.id,
        title=data['title'],
        description=data['description'],
        dates=data['dates'],
        price=data['price'],
        hashtag=hashtag,
        photo_file_id=data['photo_file_id']
    )
    await callback.message.answer("✅ Объявление опубликовано!", reply_markup=menu_kb())
    await state.clear()

@router.callback_query(PublicationFSM.confirm, F.data == "publish_edit")
async def edit_publication(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Давайте заполним объявление заново.\n\nВведите название техники:")
    await state.set_state(PublicationFSM.title)

@router.callback_query(PublicationFSM.confirm, F.data == "back_to_menu")
async def publication_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню:", reply_markup=menu_kb())

def register(dp):
    dp.include_router(router)
