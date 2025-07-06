from aiogram.fsm.state import State, StatesGroup

class OrderManagerStates(StatesGroup):
    address = State()