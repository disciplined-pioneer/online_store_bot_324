from ...settings import settings
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

order_options_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Картины на металле", callback_data="order:pictures")],
        [InlineKeyboardButton(text="Индивидуальная гравировка", callback_data="order:engraving")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

engraving_info_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Узнать цены", callback_data="price_engraving")],
        [InlineKeyboardButton(text="Примеры работ", callback_data="viewing:engraving")],
        [InlineKeyboardButton(text="Назад", callback_data="make_order")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

async def price_engraving_menu(bot):
    
    base_buttons = []

    try:
        # Проверяем, существует ли пользователь
        await bot.get_chat(settings.bot.SUPPORT_ID)
        base_buttons.append([InlineKeyboardButton(text="Чат с менеджером", url=f"tg://user?id={settings.bot.MANAGER_ID}")])
    
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Чат с менеджером (недоступен)", callback_data='manager_unavailable')])

    base_buttons.append([InlineKeyboardButton(text="Назад", callback_data='order:engraving')])
    base_buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data='back_menu')])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)
