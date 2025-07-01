from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.user.examples import *
from bot.templates.user.examples import examples_text

from core.bot import bot
from utils.user.examples import *


router = Router()


# Обработка кнопки "Примеры"
@router.callback_query(F.data == "examples")
async def examples(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    await bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
    new_msg = await callback.message.answer(
        text=examples_text,
        reply_markup=examples_menu
    )
    await state.update_data(last_id_message=new_msg.message_id)


# Обработка начала просмотра (только если строго "viewing:..." без номера)
@router.callback_query(F.data.in_(CATEGORIES.keys()))
async def handle_start_viewing(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    category_key = callback.data
    folder = CATEGORIES[category_key]

    media, total = get_media_by_index(folder, 1)
    if not media:
        await callback.message.answer("Нет доступных файлов.")
        return

    # Формировние сообщения
    keyboard = create_pagination_keyboard(category_key, 1, total)
    new_msg = await media.send(callback.message, reply_markup=keyboard)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
    await state.update_data(last_id_message=new_msg.message_id)


# Обработка пагинации (например: viewing:pictures:2)
@router.callback_query(F.data.regexp(r"^(viewing:[a-z_]+):(\d+)$"))
async def paginate(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Неверный формат запроса.")
        return

    category_key = f"{parts[0]}:{parts[1]}"
    index = int(parts[2])

    folder = CATEGORIES.get(category_key)
    if not folder:
        await callback.answer("Ошибка категории.")
        return

    media, total = get_media_by_index(folder, index)
    if not media:
        await callback.answer("Файл не найден.")
        return

    # Формировние сообщения
    keyboard = create_pagination_keyboard(category_key, index, total)
    new_msg = await media.send(callback.message, reply_markup=keyboard)
    await bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
    await state.update_data(last_id_message=new_msg.message_id)