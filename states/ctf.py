from aiogram.fsm.state import StatesGroup, State


class CTFRegistration(StatesGroup):

    full_name = State()

    organization = State()

    course = State()

    email = State()

class AdminBroadcast(StatesGroup):

    message = State()

    link = State()