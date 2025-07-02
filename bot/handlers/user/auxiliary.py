from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from ...settings import settings
from ...db.models.models import Users
from aiogram.types import CallbackQuery

from ...core.bot import bot
from ...templates.user.commands import hello_user_msg
from ...keyboards.user.commands import start_user_keyb

from ...templates.admin.commands import hello_admin_msg
from ...keyboards.admin.commands import start_admin_keyb


router = Router()


# Обработка кнопки "Меню"
@router.callback_query(F.data == "back_menu")
async def back_buttons(callback: types.CallbackQuery, state: FSMContext):

    # Информация о пользователе
    tg_id = callback.from_user.id
    info_users = await Users.get(tg_id=tg_id)
    role = info_users.role

    if role == 'admin': # Админ
        await callback.message.edit_text(
            text=hello_admin_msg,
            reply_markup=start_admin_keyb
        )

    else: # Пользователь
        await callback.message.edit_text(
            text=hello_user_msg,
            reply_markup=await start_user_keyb(bot)
        )

    await state.clear()
    await callback.answer()


# Обработка кнопки "Меню" - когда в сообщении изображение
@router.callback_query(F.data == "back_menu:images")
async def back_buttons_images(callback: types.CallbackQuery, state: FSMContext):

    # Данные
    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    # Информация о пользователе
    tg_id = callback.from_user.id
    info_users = await Users.get(tg_id=tg_id)
    role = info_users.role

    if role == 'admin': # Админ
        await callback.message.answer(
            text=hello_admin_msg,
            reply_markup=start_admin_keyb
        )

    else: # Пользователь
        await callback.message.answer(
            text=hello_user_msg,
            reply_markup=await start_user_keyb(bot)
        )

    await bot.delete_message(chat_id=callback.from_user.id, message_id=last_id_message)
    await state.clear()


# Когда поддержка недоступна
@router.callback_query(F.data == "support_unavailable")
async def support_unavailable_cb(query: CallbackQuery):
    await query.answer(
        "Поддержка временно недоступна ⏳",
        show_alert=True
    )


# Удаление сообщений, не подключённых к состоянию
@router.message()
async def handle_unexpected_message(message: types.Message, state: FSMContext):
    print('🛑 Удаляем сообщение - не в состоянии 🛑')
    await message.delete()    