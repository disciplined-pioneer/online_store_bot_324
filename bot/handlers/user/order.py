from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...keyboards.user.order import *
from ...templates.user.order import *

from ...core.bot import bot


router = Router()


# Обрабатывает подтверждение заказа по выбранному товару.
@router.callback_query(F.data.regexp(r"^order_confirm:(\d+)$"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):

    index = int(callback.data.split(":")[1])
    new_msg = await callback.message.answer(
        text=choose_image_size_text,
        reply_markup=size_selection_menu
    )
    await callback.message.delete()
    
    await state.update_data(
        number_order=index,
        last_id_message=new_msg.message_id
    )