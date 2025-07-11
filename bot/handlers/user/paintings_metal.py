from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...keyboards.user.paintings_metal import *
from ...templates.user.paintings_metal import *

from ...utils.user.examples import *


router = Router()


# Запускает пагинацию по изображениям с первого элемента
@router.callback_query(F.data == "order:pictures")
async def start_pagination(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    last_id_message = data.get("last_id_message")

    index = 1
    media, total = get_media_by_index("paintings_metal_steps", index)
    total = min(total, 3)  # Ограничиваем максимум до 3 файлов

    if not media:
        await callback.message.answer("Нет доступных файлов.")
        return

    text = examples_descriptions.get(index, "Описание отсутствует.")
    keyboard = create_product_keyboard("pictures", index, total)

    # Отправляем медиа с описанием и клавиатурой
    new_msg = await media.send(callback.message, reply_markup=keyboard, caption=text)
    if last_id_message:
        try:
            await callback.message.delete()
            await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
        except:
            pass

    await state.update_data(last_id_message=new_msg.message_id)
    await callback.answer()


# Обрабатывает нажатия на кнопки пагинации по изображениям.
@router.callback_query(F.data.regexp(r"^pictures:(\d+)$"))
async def paginate(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    last_id_message = data.get("last_id_message")

    # Извлекаем номер страницы, изображения, количество
    index = int(callback.data.split(":")[1])
    media, total = get_media_by_index("paintings_metal_steps", index)
    total = min(total, 3)

    # Если медиафайл не найден — информируем пользователя и выходим
    if not media:
        await callback.answer("Файл не найден.")
        return

    # Получаем описание для текущего индекса
    text = examples_descriptions.get(index, "Описание отсутствует.")
    keyboard = create_product_keyboard("pictures", index, total)

    # Отправляем медиафайл с описанием и клавиатурой
    new_msg = await media.send(callback.message, reply_markup=keyboard, caption=text)
    if last_id_message:
        try:
            await callback.message.delete()
            await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
        except:
            pass

    await state.update_data(last_id_message=new_msg.message_id)
    await callback.answer()

