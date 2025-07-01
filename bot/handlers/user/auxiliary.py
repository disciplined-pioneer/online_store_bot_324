from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from db.models.models import Users
from bot.keyboards.user.commands import start_keyb, admin_keyb
from bot.templates.user.commands import select_option_message, select_language_message


router = Router()


# Обработка кнопки "Меню"
@router.callback_query(F.data == "go_back_menu")
async def back_buttons(callback: types.CallbackQuery, state: FSMContext):

    tg_id = callback.from_user.id
    info_users = await Users.get(tg_id=tg_id)
    role = info_users.role

    if role == 'admin': # Админ
        await callback.message.edit_text(
            text=select_option_message,
            reply_markup=admin_keyb
        )

    else: # Пользователь
        await callback.message.edit_text(
            text=select_language_message,
            reply_markup=start_keyb
        )

    await state.clear()
    await callback.answer()


# Удаление сообщений, не подключённых к состоянию
@router.message()
async def handle_unexpected_message(message: types.Message, state: FSMContext):
    print('🛑 Удаляем сообщение - не в состоянии 🛑')
    await message.delete()    