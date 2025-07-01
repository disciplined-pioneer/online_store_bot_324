import logging
from db.models.models import Users
from settings import settings

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
            await info_user.update(name=name)
        else:
            await Users.create(
                tg_id=tg_id,
                name=name
            )
    except Exception as e:
        logging.error(f'Пользователь {tg_id} не был добавлен: {e}')
        