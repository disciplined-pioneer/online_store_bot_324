from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from ...keyboards.user.custom_engraving import *
from ...templates.user.custom_engraving import *

from ...core.bot import bot


router = Router()


# Обработка кнопки "Сделать заказ"
@router.callback_query(F.data == "make_order")
async def make_order(callback: CallbackQuery, state: FSMContext):

    await callback.message.delete()
    new_msg = await callback.message.answer(
        text=order_instructions_msg,
        reply_markup=order_options_menu
    )
    await state.update_data(last_id_message=new_msg.message_id)


# Обработка кнопки "Индивидуальная гравировка" при "Сделать заказ"
@router.callback_query(F.data == "order:engraving")
async def order_engraving(callback: types.CallbackQuery, state: FSMContext):

    new_msg = await callback.message.edit_text(
        text=engraving_description_msg,
        reply_markup=engraving_info_menu
    )
    await state.update_data(last_id_message=new_msg.message_id)


# Обработка кнопки "Узнать цены"
@router.callback_query(F.data == "price_engraving")
async def price_engraving(callback: types.CallbackQuery, state: FSMContext):

    new_msg = await callback.message.edit_text(
        text=support_prompt_msg,
        reply_markup=await price_engraving_menu(bot)
    )
    await state.update_data(last_id_message=new_msg.message_id)