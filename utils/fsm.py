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


class AdminState(StatesGroup):
    add_seller = State()
    delete_seller = State()
    ban_user = State()
    unban_user = State()


class SellerAdState(StatesGroup):
    text = State()
