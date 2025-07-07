from aiogram.fsm.state import State, StatesGroup

PHONE_REGEX = r"^(?:\+7|8)\d{10}$"

ALLOWED_IMAGE_FORMATS = {'image/jpeg', 'image/jpg', 'image/png'}

CITY_REGEX = r"^[А-Яа-яЁё\s\-]+$"

STREET_REGEX = r"^[А-Яа-яЁё0-9\s\-]+$"

HOUSE_REGEX = r"^[А-Яа-яЁё0-9\s\-\/]+$"

class OrderDetailsStates(StatesGroup):
    image = State()
    number_copies = State()
    phone_number = State()
    city = State()
    geolocation = State()
    geolocation_edit = State()

prices_dict = {
    '1': 3200,
    '2': 2000,
    '3': 1100
}

image_dict = {
    '1': '30*40 см',
    '2': '20*30 см',
    '3': '14*20 см'
}