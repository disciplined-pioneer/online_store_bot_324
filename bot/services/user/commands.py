import os
import logging
from ...db.models.models import Users
from ...settings import settings

async def add_admins():

    """Добавляет админов из настроек, если их нет в БД."""

    for tg_id in settings.bot.ADMINS:
        info_user = await Users.get(tg_id=tg_id)
        if info_user:
            await info_user.update(role='admin')
            logging.info(f"Пользователь '{tg_id}' был добавлен как 'admin'")
        else:
            await Users.create(
                tg_id=tg_id,
                role='admin'
            )
            logging.info(f"Роль пользователя '{tg_id}' изменена на 'admin'")

async def save_or_update_user(tg_id, name):

    """Добавляет пользователей из настроек, если их нет в БД."""

    try:
        info_user = await Users.get(tg_id=tg_id)
        if info_user:
            await info_user.update(
                name=name
            )
        else:
            await Users.create(
                tg_id=tg_id,
                name=name
            )
    except Exception as e:
        logging.error(f'Пользователь {tg_id} не был добавлен: {e}')
        

def create_data_folders():
    
    """Создание папок для хранения файлов"""

    base_paths = ['bot/data/admin', 'bot/data/user']
    folders = [
        'bot/data/user/custom_engraving',
        'bot/data/user/paintings_metal',
        'bot/data/user/paintings_metal_steps',
        'bot/data/admin/excel',
        'bot/data/admin/zip',
        'bot/data/admin/qrcodes'
    ]

    # Создание базовых папок
    for base_path in base_paths:
        os.makedirs(base_path, exist_ok=True)

    # Создание вложенных папок
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
