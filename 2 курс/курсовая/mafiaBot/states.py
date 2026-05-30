from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    FirstDay = State()
    opening = State()
    Day = State()
    Night = State()
    DailyWaitingForReply = State()
    NightWaitingForReply = State()