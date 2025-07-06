import os
import qrcode
from pathlib import Path
from aiogram.types import FSInputFile

from aiogram.types import CallbackQuery
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...keyboards.admin.commands import *
from ...templates.admin.commands import *
from ...db.models.models import Users, ReferralLinks


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


# Обработка кнопки "QR-код"
@router.callback_query(F.data == "qr_code")
async def qr_code(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        text='Выберите действие',
        reply_markup=qr_code_keyb
    )


# Сформировать ссылку
@router.callback_query(F.data == "form")
async def generate_referral(callback: CallbackQuery, state: FSMContext):
    
    # Получаем имя бота
    await callback.answer()
    bot_username = (await bot.get_me()).username

    # Создаём новую ссылку (пока temp)
    new_link = await ReferralLinks.create(referral_link="temp")
    referral_code = str(new_link.id)
    link = f"https://t.me/{bot_username}?start={referral_code}"

    # Обновляем реальную ссылку
    await new_link.update(referral_link=link)

    # Генерируем QR-код
    qr_path = Path(f"data/qrcodes/ref_{callback.from_user.id}.png")
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    qr = qrcode.make(link)
    qr.save(qr_path)

    # Отправляем одним сообщением
    file = FSInputFile(qr_path)
    caption = (
        f"👤 Ваша реферальная ссылка:\n"
        f"{link}\n\n"
        f"📎 QR-код для удобного перехода"
    )
    await callback.message.answer_photo(photo=file, caption=caption)
    await callback.message.delete()

    # Чистим QR-файл
    try:
        qr_path.unlink()
    except Exception as e:
        print(f"⚠️ Не удалось удалить QR-файл: {e}")

    await callback.answer()


# Обработка "Старый" реф. ссылка
@router.callback_query(F.data == "old")
async def old_referral(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text(
        text=await message_ref_links(),
        reply_markup=back_menu_admin
    )