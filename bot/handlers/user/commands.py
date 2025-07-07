from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...db.models.models import Users
from ...utils.user.commands import process_start_payload
from ...services.user.commands import save_or_update_user
from ...templates.user.commands import hello_user_msg
from ...keyboards.user.commands import start_user_keyb

from ...templates.admin.commands import hello_admin_msg
from ...keyboards.admin.commands import start_admin_keyb


router = Router()


# Старт
@router.message(Command("start", ignore_case=True))
async def cmd_start(message: Message, state: FSMContext):

    # Удаляем всю историю сообщений
    await message.delete()
    data = await state.get_data()
    report_id = data["report"] if 'report' in data else message.message_id - 90
    try:
        await bot.delete_messages(message.chat.id,
                                    list(range(max(1, message.message_id - 90, report_id + 1), message.message_id + 1)))
    except Exception:
        pass

    # Добавляем пользователя/изменяем name
    tg_id = tg_id=message.from_user.id
    name = message.from_user.full_name
    await save_or_update_user(tg_id=tg_id, name=name)

    # Обработка реф. ссылки
    await process_start_payload(tg_id=tg_id, message=message)

    new_msg = await message.answer(
        text=hello_user_msg,
        reply_markup=await start_user_keyb(bot)
    )

    """# Информация о пользователе
    tg_id = message.from_user.id
    info_users = await Users.get(tg_id=tg_id)
    role = info_users.role

    if role == 'admin': # Админ
        new_msg = await message.answer(
            text=hello_admin_msg,
            reply_markup=start_admin_keyb
        )

    else: # Пользователь
        new_msg = await message.answer(
            text=hello_user_msg,
            reply_markup=await start_user_keyb(bot)
        )"""
    
    await state.update_data(last_id_message=new_msg.message_id)