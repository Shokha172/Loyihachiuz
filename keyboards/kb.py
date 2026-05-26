from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# --- User Keyboards ---
user_start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
])

phone_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
], resize_keyboard=True)

location_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)]
], resize_keyboard=True)

# --- Admin Keyboards ---
admin_panel_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📩 Kelgan Arizalar", callback_data="view_requests")],
    [InlineKeyboardButton(text="📝 Yangi Mijozni Ro'yxatdan o'tkazish", callback_data="admin_reg")],
    [InlineKeyboardButton(text="📐 Yangi Loyiha Biriktirish", callback_data="attach_project")],
    [InlineKeyboardButton(text="🔍 Invoist ID bo'yicha qidirish", callback_data="search_id")],
    [InlineKeyboardButton(text="💼 Ish holatini o'zgartirish", callback_data="change_status")],
    [InlineKeyboardButton(text="📁 Mijozga Media/Xabar yuborish", callback_data="send_media")],
    [InlineKeyboardButton(text="📊 Excel barcha loyihalar hisoboti", callback_data="excel_report")],
    [InlineKeyboardButton(text="📄 PDF barcha loyihalar hisoboti", callback_data="pdf_report")],
    [InlineKeyboardButton(text="➕ Yangi Admin Qo'shish", callback_data="add_new_admin")],
    [InlineKeyboardButton(text="➖ Adminni Olib Tashlash", callback_data="remove_admin")],
    [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
    [InlineKeyboardButton(text="📢 Xabar Yuborish", callback_data="broadcast")]
])

# Project Category
category_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏢 1-QAVATLI TURAR-JOY OBEKTLARI", callback_data="cat_1")],
    [InlineKeyboardButton(text="🏢 2-QAVATLI TURAR-JOY OBEKTLARI", callback_data="cat_2")],
    [InlineKeyboardButton(text="🏢 3-NOTURAR-JOY OBEKTLARI", callback_data="cat_noturar")],
    [InlineKeyboardButton(text="💻 KOMPYUTER XIZMATLARI", callback_data="cat_comp")]
])

def get_services_kb(cat_id):
    kb_list = []
    if cat_id == "cat_1":
        services = ["LOYIHA HUJJATLARI", "LOYIHA HUJJATLARI TO'G'IRLASH"]
    elif cat_id == "cat_2":
        services = ["LOYIHA HUJJATLARI"]
    elif cat_id == "cat_noturar":
        services = ["ESKIZ LOYIHA", "SMETA", "RABOCHIY PROEKT"]
    elif cat_id == "cat_comp":
        services = ["KALSTANTIN XIZMATI (loyiha hujjati bo'yicha)", "BOSHQA TURDAGI KALSTANTIN XIZMAT"]
    else:
        return None
        
    for svc in services:
        kb_list.append([InlineKeyboardButton(text=svc, callback_data=f"svc_{svc[:20]}")])
    return InlineKeyboardMarkup(inline_keyboard=kb_list)

# Status
status_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Jarayonda")],
    [KeyboardButton(text="Loyiha hujjatlaringiz tayyorlandi")]
], resize_keyboard=True)

# Payment methods
payment_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Naqd"), KeyboardButton(text="Click")],
    [KeyboardButton(text="Payme"), KeyboardButton(text="Perichisleniye")]
], resize_keyboard=True)

# Helper to remove keyboard
remove_kb = ReplyKeyboardRemove()

def create_requests_kb(users):
    kb_list = []
    for user in users:
        kb_list.append([InlineKeyboardButton(text=f"👤 {user['full_name']}", callback_data=f"req_{user['tg_id']}")])
    kb_list.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=kb_list)
