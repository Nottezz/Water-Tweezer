from aiogram.fsm.state import State, StatesGroup


class WaterSurvey(StatesGroup):
    daily_goal = State()
    reminder_interval = State()
    user_timezone = State()
    confirm_settings = State()
