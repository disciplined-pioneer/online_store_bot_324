import os
from pathlib import Path
from aiogram.types import FSInputFile

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from ...db.models.models import Users
from ...keyboards.admin.commands import back_menu_admin
from aiogram.types import CallbackQuery

from ...core.bot import bot


router = Router()


# Обработка кнопки "Пользователи"
@router.callback_query(F.data == "users")
async def users(callback: CallbackQuery, state: FSMContext):
    
    await callback.answer()
    df = await Users.get_users_without_orders()

    # Создаём папку, если её нет
    output_dir = Path("data/excel")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Уникальное имя файла — по tg_id пользователя
    tg_id = callback.from_user.id
    file_path = output_dir / f"users_{tg_id}.xlsx"

    # Сохраняем Excel-файл
    df.to_excel(file_path, index=False)

    # Отправляем файл
    file = FSInputFile(path=file_path, filename=file_path.name)
    await callback.message.answer_document(file, caption="Пользователи без заказов")
    await callback.message.delete()

    # Удаляем файл после отправки
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"⚠️ Не удалось удалить файл {file_path}: {e}")