from aiogram.fsm.state import State, StatesGroup

PHONE_REGEX = r"^(?:\+7|8)\d{10}$"

CITY_REGEX = r"^[А-Яа-яЁё\-]+$"

ALLOWED_IMAGE_FORMATS = {'image/jpeg', 'image/jpg', 'image/png'}

class OrderDetailsStates(StatesGroup):
    image = State()
    number_copies = State()
    phone_number = State()
    city = State()
    geolocation = State()
    geolocation_edit = State()