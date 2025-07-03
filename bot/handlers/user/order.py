from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...keyboards.user.order import *
from ...templates.user.order import *
from ...utils.user.order import OrderDetailsStates, ALLOWED_IMAGE_FORMATS


router = Router()


# Обрабатывает подтверждение заказа по выбранному товару
@router.callback_query(F.data.regexp(r"^order_confirm:(\d+)$"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):

    index = int(callback.data.split(":")[1])

    new_msg = await callback.message.answer(
        text=choose_image_size_text,
        reply_markup=size_selection_menu
    )
    await callback.message.delete()
    
    await state.clear()
    await state.update_data(
        number_order=index,
        last_id_message=new_msg.message_id
    )


# Обработка выбранного размера изображения
@router.callback_query(F.data.startswith("size:"))
async def image_size(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data = await state.get_data()
    number_order = data.get('number_order', 1)
    image_size = callback.data.split(':')[1]

    new_msg = await callback.message.edit_text(
        text=add_image_instruction,
        reply_markup=get_order_confirmation_keyboard(number_order)
    )

    await state.update_data(
        image_size=image_size,
        last_id_message=new_msg.message_id
    )
    await state.set_state(OrderDetailsStates.image)


# Обработка изображения от пользователя
@router.message(OrderDetailsStates.image, F.photo)
async def handle_photo(message: Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    last_id_message = data.get('last_id_message')
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)

    try:
        if file_info.file_path.endswith((".jpg", ".jpeg", ".png")):

            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=enter_copies_count_text
            )
            await state.set_state(OrderDetailsStates.number_copies) 
            await state.update_data(file_info={'file_id': photo.file_id, 'type': 'photo'})
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_image_format_text
            )
    except:
        return


# Обработка "файлов" (если пользователь прикрепил документ)
@router.message(OrderDetailsStates.image, F.document)
async def handle_document_image(message: Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    mime_type = message.document.mime_type
    try:
        if mime_type in ALLOWED_IMAGE_FORMATS:
            
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=enter_copies_count_text
            )
            await state.set_state(OrderDetailsStates.number_copies)
            await state.update_data(file_info={'file_id': message.document.file_id, 'type': 'photo'})
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_image_format_text
            )
    except:
        return
    

# Обрабатываем количество копий
@router.message(OrderDetailsStates.number_copies)
async def process_copies_count(message: types.Message, state: FSMContext):

    try:
        # Данные
        await message.delete()
        data = await state.get_data()
        last_id_message = data.get('last_id_message')
        text = message.text.strip()

        if not text.isdigit():
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_integer_input_text
            )
            return

        count = int(text)
        if count < 1:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=copies_count_minimum_error_text
            )
            return
    except:
        return

    # Всё ок, сохраняем в состояние
    await state.set_state(None)
    await state.update_data(copies_count=count)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=last_id_message,
        text=f"✅ Количество копий установлено: {count}"
    )