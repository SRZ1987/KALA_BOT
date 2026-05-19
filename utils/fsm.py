from aiogram.fsm.state import State, StatesGroup




class FeedbackState(StatesGroup):
    waiting_feedback = State()

class SOSState(StatesGroup):
    problem = State()
    location = State()
    phone = State()


class RideAdState(StatesGroup):
    city = State()
    ad_type = State()
    text = State()
