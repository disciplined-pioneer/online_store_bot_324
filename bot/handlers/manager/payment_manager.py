from aiogram.types import Message
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery
from ...db.models.models import OrderUsers

from ...core.bot import bot
from ...utils.manager.payment_manager import *
from ...templates.manager.payment_manager import *
from ...keyboards.manager.payment_manager import *


router = Router()


# Обработка кнопки "Отправить"
@router.callback_query(F.data.startswith("send:"))
async def send_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = data_list[1]
    order_id = data_list[2]

    await bot.send_message(
        chat_id=user_id,
        text=f'✅ Ваш заказ №{order_id} был отправлен!'
    )

    await callback.message.answer(
        text=f'✅ Сообщение было отправлено пользователю {user_id}!'
    )
    await callback.message.delete()


# Обработка кнопки "Оповестить"
@router.callback_query(F.data.startswith("notify:"))
async def notify_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = data_list[1]
    order_id = data_list[2]

    await bot.send_message(
        chat_id=user_id,
        text='Просьба зайти в приложение Ozon и выбрать удобный пункт ддя получения заказа. Срок доставки будет отражаться в приложении Ozon'
    )

    await callback.message.answer(
        text=f'✅ Сообщение было отправлено пользователю {user_id}!',
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await callback.message.delete()
    await state.update_data(user_id=user_id, order_id=order_id)


# Обработка кнопки "Адрес"
@router.callback_query(F.data.startswith("address:"))
async def address_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = data_list[1]
    order_id = data_list[2]

    new_msg = await callback.message.edit_text(
        text=f'Отправьте актуальный адрес в группу!',
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await state.set_state(OrderManagerStates.address)
    await state.update_data(user_id=user_id, order_id=order_id, last_id_msg=new_msg.message_id)


# Получаем актуальный адрес
@router.message(OrderManagerStates.address)
async def handle_address(message: Message, state: FSMContext):

    await message.delete()
    if message.chat.type not in ("group", "supergroup"):
        return

    # Данные
    data = await state.get_data()
    user_id = data.get('user_id')
    order_id = data.get('order_id')
    last_id_msg = data.get('last_id_msg')
    address = message.text

    await bot.send_message(
        chat_id=user_id,
        text=f'Актуальный адрес был изменён на: "{address}"'
    )

    await bot.edit_message_text(
        message_id=last_id_msg,
        chat_id=message.from_user.id,
        text=f'✅ Сообщение было отправлено пользователю {user_id}!',
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await state.update_data(user_id=user_id, order_id=order_id)


# Обработка кнопки "Назад" у менеджера
@router.callback_query(F.data.startswith("back_manager:"))
async def back_manager(callback: types.CallbackQuery, state: FSMContext):

    data_list = callback.data.split(":")
    user_id = int(data_list[1])
    order_id = int(data_list[2])

    # Получаем информацию о заказе
    order = await OrderUsers.get(id=order_id)

    # Форматируем текст заказа
    text = format_order_text(
        order_id=order.id,
        product_name=order.product_name,
        quantity=order.quantity,
        total_price=order.total_price,
        address=order.address,
        delivery_method=order.delivery_method,
        image_size=order.image_size,
        phone_number=order.phone_number,
    )

    # Обновляем сообщение
    await callback.message.edit_text(
        text=text,
        reply_markup=await manager_panel_keyb(user_id=user_id, order_id=order_id, bot=bot)
    )

    # Обновляем state
    await state.update_data(user_id=user_id, order_id=order_id)


# Когда поддержка недоступна
@router.callback_query(F.data == "contact_unavailable")
async def contact_unavailable(query: CallbackQuery):
    await query.answer(
        "Пользователь временно недоступна ⏳",
        show_alert=True
    )