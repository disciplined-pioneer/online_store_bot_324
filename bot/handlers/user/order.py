from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...keyboards.user.order import *
from ...templates.user.order import *
from ...db.models.models import OrderUsers
from ...utils.user.order import OrderDetailsStates, ALLOWED_IMAGE_FORMATS, prices_dict, image_dict


router = Router()


# Обрабатывает подтверждение заказа по выбранному товару
@router.callback_query(F.data.regexp(r"^order_confirm:(\d+)$"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):

    # Данные
    await state.clear()
    index = int(callback.data.split(":")[1])
    image_size = image_dict[str(index)]
    
    new_msg = await callback.message.answer(
        text=add_image_instruction,
        reply_markup=image_menu
    )
    await callback.message.delete()

    await state.update_data(
        image_size=image_size,
        price=prices_dict[str(index)],
        number_order=index,
        last_id_message=new_msg.message_id
    )
    await state.set_state(OrderDetailsStates.image)


# Обработка "файлов" (если пользователь прикрепил документ)
@router.message(OrderDetailsStates.image, F.document)
async def handle_document_image(message: Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    number_order = data.get('number_order', 1)
    last_id_message = data.get('last_id_message')

    mime_type = message.document.mime_type
    try:
        if mime_type in ALLOWED_IMAGE_FORMATS:
            
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=enter_copies_count_text,
                reply_markup=previous_stepn_keyboard(f'back_step_user:image_back')
            )
            await state.set_state(OrderDetailsStates.number_copies)
            await state.update_data(file_info={'file_id': message.document.file_id, 'type': 'document'})
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_image_format_text,
                reply_markup=previous_stepn_keyboard(f'order_confirm:{number_order}')
            )
    except:
        return
    

# Обработка изображения от пользователя
@router.message(OrderDetailsStates.image, F.photo)
async def handle_photo(message: Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    number_order = data.get('number_order', 1)
    last_id_message = data.get('last_id_message')

    try:
        await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=last_id_message,
            text=invalid_image_text,
            reply_markup=previous_stepn_keyboard(f'order_confirm:{number_order}')
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
        price = data.get('price', 1)
        image_size = data.get('image_size')
        last_id_message = data.get('last_id_message')
        text = message.text.strip()

        if not text.isdigit():
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_integer_input_text,
                reply_markup=previous_stepn_keyboard(f'size:{image_size}')
            )
            return

        count = int(text)
        if count < 1:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=copies_count_minimum_error_text,
                reply_markup=previous_stepn_keyboard(f'size:{image_size}')
            )
            return
    except:
        return

    # Если уже есть хотя бы 1 необработанный заказ, то не включаем доставку
    all_price = price * count
    info_order = await OrderUsers.filter(
        tg_id=message.from_user.id,
        dispatch_status='not_sent'
    )
    if not info_order:
        all_price += 200

    # Всё ок, сохраняем в состояние
    await state.set_state(None)
    await state.update_data(copies_count=count, all_price=all_price)
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=last_id_message,
        text=choose_delivery_method_text,
        reply_markup=delivery_pickup_menu
    )


# Обработка кнопки "Назад" для пользователя
@router.callback_query(F.data.startswith("back_step_user:"))
async def back_step_user(callback: types.CallbackQuery, state: FSMContext):

    parametr = callback.data.split(':')[1]
    
    if parametr == 'image_back':
        new_msg = await callback.message.edit_text(
            text=add_image_instruction,
            reply_markup=image_menu
        )
        await state.set_state(OrderDetailsStates.image)

    elif parametr == 'return_copies':
        new_msg = await callback.message.edit_text(
            text=enter_copies_count_text,
            reply_markup=previous_stepn_keyboard(f'back_step_user:image_back')
        )
        await state.set_state(OrderDetailsStates.number_copies)
    await state.update_data(last_id_message=new_msg.message_id)