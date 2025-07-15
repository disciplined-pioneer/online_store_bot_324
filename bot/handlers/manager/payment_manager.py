from aiogram.types import Message
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery
from ...db.models.models import OrderUsers

from ...core.bot import bot
from ...settings import settings
from ...utils.manager.payment_manager import *
from ...templates.manager.payment_manager import *
from ...keyboards.manager.payment_manager import *
from services_runner.utils.payment_manager import send_or_update_order_message


router = Router()


# Обработка кнопки "Отправить"
@router.callback_query(F.data.startswith("send:"))
async def send_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    await callback.message.edit_reply_markup(reply_markup=None)
    data_list = callback.data.split(":")
    user_id = int(data_list[1])
    order_id = int(data_list[2])

    # Изменяем статус отправки
    info_order = await OrderUsers.get(id=order_id)
    if info_order:
        await info_order.update(dispatch_status='sent')

    await bot.send_message(
        chat_id=user_id,
        text=order_sent_msg(order_id)
    )

    await callback.message.answer(text=user_notified_msg(user_id))


# Обработка кнопки "Оповестить"
@router.callback_query(F.data.startswith("notify:"))
async def notify_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = int(data_list[1])
    order_id = int(data_list[2])

    await bot.send_message(
        chat_id=user_id,
        text=ozon_pickup_request_msg(order_id)
    )

    await callback.message.answer(
        text=message_sent_msg(user_id),
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await callback.message.delete()
    await state.update_data(user_id=user_id, order_id=order_id)


# Обработка кнопки "Адрес"
@router.callback_query(F.data.startswith("address:"))
async def address_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = int(data_list[1])
    order_id = int(data_list[2])

    new_msg = await callback.message.answer(
        text=send_address_request_msg,
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await callback.message.delete()
    await state.set_state(OrderManagerStates.address)
    await state.update_data(user_id=user_id, order_id=order_id, last_id_msg=new_msg.message_id)


# Получаем актуальный адрес
@router.message(OrderManagerStates.address)
async def handle_address(message: Message, state: FSMContext):

    await message.delete()
    if message.chat.type not in ("group", "supergroup"):
        await state.clear()
        return
    
    # Данные
    data = await state.get_data()
    user_id = data.get('user_id')
    order_id = data.get('order_id')
    last_id_msg = data.get('last_id_msg')
    address = message.text

    # Изменяем статус отправки
    info_order = await OrderUsers.get(id=order_id)
    if info_order:
        await info_order.update(geolocation=address)

    await bot.send_message(
        chat_id=user_id,
        text=address_updated_msg(order_id, address)
    )

    await bot.edit_message_text(
        message_id=last_id_msg,
        chat_id=settings.bot.CHANEL_ID,
        text=address_update_confirm_msg(order_id, address, user_id),
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await state.update_data(user_id=user_id, order_id=order_id)


# Обработка кнопки "Назад" у менеджера
@router.callback_query(F.data.startswith("back_manager:"))
async def back_manager(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    await state.set_state(None)
    data_list = callback.data.split(":")
    user_id = int(data_list[1])
    order_id = int(data_list[2])
    await callback.message.edit_text(files_uploading_msg(order_id))

    # Получаем информацию о заказе
    new_existing_order = await OrderUsers.get(id=order_id)
    await send_or_update_order_message(order=new_existing_order, bot=bot)
    await callback.message.delete()

    # Обновляем state
    await state.update_data(user_id=user_id, order_id=order_id)


# Когда пользователь недоступен
@router.callback_query(F.data == "contact_unavailable")
async def contact_unavailable(query: CallbackQuery):
    await query.answer(
        user_unavailable_msg = "Пользователь временно недоступна ⏳",
        show_alert=True
    )