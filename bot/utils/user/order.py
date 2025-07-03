from aiogram.fsm.state import State, StatesGroup

ALLOWED_IMAGE_FORMATS = {'image/jpeg', 'image/jpg', 'image/png'}

class OrderDetailsStates(StatesGroup):
    image = State()
    number_copies = State()