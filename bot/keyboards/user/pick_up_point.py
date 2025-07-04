from ...settings import settings
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

phone_number_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Указать номер телефона", callback_data="enter_phone")],
        [InlineKeyboardButton(text="Назад", callback_data="alternative_back:selection_pick-up_point")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

delivery_pickup_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ПВЗ Яндекс Маркет", callback_data="pickup:yandex")],
        [InlineKeyboardButton(text="ПВЗ OZON", callback_data="pickup:ozon")],
        [InlineKeyboardButton(text="Назад", callback_data="return_copies")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

def payment_keyb(price: int = 1):

    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url='https://www.google.com/')],
            [InlineKeyboardButton(text="Назад", callback_data="alternative_back:selection_pick-up_point")],
        ]
    )
    return keyb

async def create_edit_geolocation_keyboard(bot):
    
    base_buttons = [
        [InlineKeyboardButton(text="Город", callback_data="edit_geolocation:city")],
        [InlineKeyboardButton(text="Улица", callback_data="edit_geolocation:street")],
        [InlineKeyboardButton(text="Дом", callback_data="edit_geolocation:house")],
        [InlineKeyboardButton(text="Всё верно", callback_data="everything_correct")]
    ]

    try:
        await bot.send_chat_action(settings.bot.SUPPORT_ID, action="typing")
        base_buttons.append([InlineKeyboardButton(text="Поддержка", url=f"tg://user?id={settings.bot.SUPPORT_ID}")])
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Поддержка", callback_data='support_unavailable')])

    base_buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data='back_menu')])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)

send_location_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

def previous_stepn_keyboard(parameter: str):
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"{parameter}")],
        ]
    )
    return keyb

async def final_menu_keyb(bot):
    
    base_buttons = [
        [InlineKeyboardButton(text="Всё верно", callback_data='everything_correct')]
    ]

    try:
        await bot.send_chat_action(settings.bot.SUPPORT_ID, action="typing")
        base_buttons.append([InlineKeyboardButton(text="Поддержка", url=f"tg://user?id={settings.bot.SUPPORT_ID}")])
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Поддержка", callback_data='support_unavailable')])

    base_buttons.append([InlineKeyboardButton(text="Назад", callback_data='alternative_back:choice_city')])
    base_buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data='back_menu')])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)
