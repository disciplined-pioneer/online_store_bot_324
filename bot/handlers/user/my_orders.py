from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...db.models.models import OrderUsers
from ...templates.user.my_orders import *
from ...keyboards.user.my_orders import *


router = Router()


# Обработка кнопки "Мои заказы"
@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery, state: FSMContext):

    tg_id = callback.from_user.id
    orders = await OrderUsers.filter(tg_id=tg_id)
    if not orders:
        await callback.message.edit_text(
            text=no_orders_user,
            reply_markup=back_menu
        )
        await callback.answer()
        return

    index = 1
    order = orders[index - 1]
    text = format_order_text(order)
    keyboard = create_orders_keyboard(index, len(orders))

    # Редактируем существующее сообщение (кнопка "Мои заказы" скорее всего в этом же сообщении)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


# Пагинация кнопки "Мои заявки"
@router.callback_query(F.data.regexp(r"^user_orders:(\d+)$"))
async def paginate_orders(callback: CallbackQuery, state: FSMContext):

    tg_id = callback.from_user.id
    index = int(callback.data.split(":")[1])
    orders = await OrderUsers.filter(tg_id=tg_id)

    if not orders:
        await callback.answer("У вас нет заказов.")
        return

    total = len(orders)
    if index < 1 or index > total:
        await callback.answer("Нет такого заказа.")
        return

    order = orders[index - 1]
    text = format_order_text(order)
    keyboard = create_orders_keyboard(index, total)

    # Редактируем сообщение с заказом, не создавая нового и не удаляя
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
