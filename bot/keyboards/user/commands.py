from settings import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

async def start_user_keyb(bot):
    
    chanel_link = settings.bot.CHANEL_LINK
    base_buttons = [
        [InlineKeyboardButton(text="Примеры работ", callback_data='examples')],
        [InlineKeyboardButton(text="Заказать", callback_data='order')],
        [InlineKeyboardButton(text="Мои заказы", callback_data='my_orders')],
        [InlineKeyboardButton(text="Отзывы", url=chanel_link)],
    ]

    try:
        await bot.send_chat_action(settings.bot.SUPPORT_ID, action="typing")
        base_buttons.append([InlineKeyboardButton(text="Поддержка", url=f"tg://user?id={settings.bot.SUPPORT_ID}")])
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Поддержка", callback_data='support_unavailable')])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)
