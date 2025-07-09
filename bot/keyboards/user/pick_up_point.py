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

def payment_keyb(payment_url: str='https://www.google.com/', parametr: str='edit_geolocation'):

    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payment_url)],
            [InlineKeyboardButton(text="Назад", callback_data=f"alternative_back:{parametr}")],
        ]
    )
    return keyb

async def create_edit_geolocation_keyboard(bot) -> InlineKeyboardMarkup:
    
    base_buttons = [
        [InlineKeyboardButton(text="Город", callback_data="edit_geolocation:city")],
        [InlineKeyboardButton(text="Улица", callback_data="edit_geolocation:street")],
        [InlineKeyboardButton(text="Дом", callback_data="edit_geolocation:house")],
        [InlineKeyboardButton(text="Всё верно", callback_data="everything_correct")]
    ]

    try:
        # Проверяем, существует ли пользователь
        await bot.get_chat(settings.bot.SUPPORT_ID)
        base_buttons.append([InlineKeyboardButton(text="Поддержка", url=f"tg://user?id={settings.bot.SUPPORT_ID}")])
    
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Поддержка (недоступен)", callback_data='support_unavailable')])

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
        await bot.get_chat(settings.bot.SUPPORT_ID)
        base_buttons.append([InlineKeyboardButton(text="Поддержка", url=f"tg://user?id={settings.bot.SUPPORT_ID}")])
    
    except TelegramBadRequest:
        base_buttons.append([InlineKeyboardButton(text="Поддержка  (недоступен)", callback_data='support_unavailable')])

    base_buttons.append([InlineKeyboardButton(text="Назад", callback_data='alternative_back:choice_city')])
    base_buttons.append([InlineKeyboardButton(text="🔙 Меню", callback_data='back_menu')])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)
