from aiogram.fsm.state import State, StatesGroup

class CareerTest(StatesGroup):
    education_level = State()
    question = State()
    mentor_chat = State()

    month_plan_goal = State()
    month_plan_action = State()

    progress_input = State()