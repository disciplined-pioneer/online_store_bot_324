from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from core.bot import bot
from bot.keyboards.user.examples import *
from bot.templates.user.examples import *

from settings import settings
from datetime import datetime


router = Router()


# Обработка кнопки "Примеры"
@router.callback_query(F.data == "examples")
async def examples(callback: types.CallbackQuery, state: FSMContext):
    
    await callback.message.edit_text(
        text=examples_text,
        reply_markup=examples_menu
    )