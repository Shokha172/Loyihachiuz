from aiogram.fsm.state import State, StatesGroup

class UserReg(StatesGroup):
    full_name = State()
    phone = State()
    location = State()

class AdminReg(StatesGroup):
    user_id = State()
    full_name = State()
    phone = State()
    address = State()
    
    # Project Params
    loyiha_toifasi = State()
    service_type = State()
    stage = State()
    tur = State()
    total_sum = State()
    paid_sum = State()
    payment_method = State()
    receipt = State()

class AttachProject(StatesGroup):
    user_id = State()
    loyiha_toifasi = State()
    service_type = State()
    stage = State()
    tur = State()
    total_sum = State()
    paid_sum = State()
    payment_method = State()
    receipt = State()

class SearchUser(StatesGroup):
    user_id = State()

class ChangeStatus(StatesGroup):
    user_id = State()
    status = State()

class SendMedia(StatesGroup):
    user_id = State()
    media = State()

class AddAdmin(StatesGroup):
    user_id = State()

class RemoveAdmin(StatesGroup):
    user_id = State()

class BroadcastState(StatesGroup):
    message = State()
