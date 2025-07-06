from aiogram.types import Message
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from ...db.models.models import Users

from ...core.bot import bot
from ...templates.manager.payment_manager import *
from ...keyboards.manager.payment_manager import *
from ...utils.manager.payment_manager import *


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

    await callback.message.edit_text(
        text=f'✅ Сообщение было отправлено пользователю {user_id}!'
    )


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

    await callback.message.edit_text(
        text=f'✅ Сообщение было отправлено пользователю {user_id}!',
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await state.update_data(user_id=user_id, order_id=order_id)


# Обработка кнопки "Адрес"
@router.callback_query(F.data.startswith("address:"))
async def address_user(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = data_list[1]
    order_id = data_list[2]

    await callback.message.edit_text(
        text=f'Отправьте актуальный адрес в группу!',
        reply_markup=back_manager_menu(user_id, order_id)
    )
    await state.set_state(OrderManagerStates.address)
    await state.update_data(user_id=user_id, order_id=order_id)


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
    address = message.text


# Обработка кнопки "Назад" у менеджера
@router.callback_query(F.data.startswith("back_manager:"))
async def back_manager(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data_list = callback.data.split(":")
    user_id = data_list[1]
    order_id = data_list[2]

    

    await callback.message.edit_text(
        text=format_order_text(),
        reply_markup=await manager_panel_keyb(user_id, order_id, bot)
    )
    await state.update_data(user_id=user_id, order_id=order_id)