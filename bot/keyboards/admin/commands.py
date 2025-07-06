from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_admin_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пользователи", callback_data='users')],
        [InlineKeyboardButton(text="Клиенты", callback_data='clients')],
        [InlineKeyboardButton(text="QR-код", callback_data='qr_code')]
    ]
)

back_menu_admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

qr_code_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Старый", callback_data='old')],
        [InlineKeyboardButton(text="Сформировать", callback_data='form')],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)