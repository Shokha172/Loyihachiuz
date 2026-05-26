import os
from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime
from config import SUPER_ADMIN_ID, TIMEZONE
from database import db
from states.states import AdminReg, AttachProject, SearchUser, ChangeStatus, SendMedia, AddAdmin, RemoveAdmin, BroadcastState
from keyboards import kb
from utils.excel_gen import generate_report
from utils.pdf_gen import generate_user_pdf, generate_full_report_pdf

router = Router()

# Admin Panel entry
@router.callback_query(F.data == "admin_panel")
async def open_admin_panel(call: types.CallbackQuery):
    await call.message.edit_text("🛠 Admin Panel boshqaruv paneli:", reply_markup=kb.admin_panel_kb)
    await call.answer()

# --- 0. View Pending Requests ---
@router.callback_query(F.data == "view_requests")
async def view_requests(call: types.CallbackQuery):
    users = await db.get_pending_users()
    if not users:
        await call.message.edit_text("📩 Hozircha yangi arizalar yo'q.", reply_markup=kb.admin_panel_kb)
    else:
        await call.message.edit_text("📩 Kelgan arizalar ro'yxati:", reply_markup=kb.create_requests_kb(users))
    await call.answer()

@router.callback_query(F.data.startswith("req_"))
async def request_detail(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    user = await db.get_user(user_id)
    if user:
        resp = (
            f"🆕 Yangi ariza tafsilotlari:\n\n"
            f"👤 Ism: {user['full_name']}\n"
            f"📞 Tel: {user['phone']}\n"
            f"📍 Manzil: {user['address']}\n"
            f"🆔 ID: {user['tg_id']}\n"
            f"📅 Vaqt: {user['created_at']}"
        )
        # Detail buttons
        detail_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📐 Loyiha Biriktirish", callback_data=f"accept_{user_id}")],
            [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{user_id}")],
            [InlineKeyboardButton(text="📄 PDF Hujjat tayyorlash", callback_data=f"pdf_{user_id}")],
            [InlineKeyboardButton(text="⬅️ Ro'yxatga qaytish", callback_data="view_requests")]
        ])
        await call.message.edit_text(resp, reply_markup=detail_kb)
    else:
        await call.message.edit_text("❌ Ariza topilmadi.", reply_markup=kb.admin_panel_kb)
    await call.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_request(call: types.CallbackQuery, bot):
    user_id = int(call.data.split("_")[1])
    # Optionally delete from DB or just change status
    await db.update_user_status(user_id, "Rad etildi")
    await call.message.edit_text("❌ Ariza rad etildi.", reply_markup=kb.admin_panel_kb)
    try:
        await bot.send_message(user_id, "Sizning arizangiz rad etildi.")
    except: pass
    await call.answer()

@router.callback_query(F.data.startswith("accept_"))
async def accept_request_start(call: types.CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[1])
    await state.update_data(user_id=user_id)
    await state.set_state(AttachProject.loyiha_toifasi)
    await call.message.edit_text("Loyiha toifasini tanlang:", reply_markup=kb.category_kb)
    await call.answer()

# --- 1. New Client Registration (Admin) ---
@router.callback_query(F.data == "admin_reg")
async def admin_reg_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AdminReg.user_id)
    await call.message.answer("Mijoz uchun ixtiyoriy ID raqam kiriting:")
    await call.answer()

@router.message(AdminReg.user_id)
async def admin_reg_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await state.set_state(AdminReg.full_name)
    await message.answer("Mijoz Ism-familiyasi:")

@router.message(AdminReg.full_name)
async def admin_reg_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(AdminReg.phone)
    await message.answer("Mijoz telefon raqami:")

@router.message(AdminReg.phone)
async def admin_reg_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(AdminReg.address)
    await message.answer("Ob'ekt manzili:")

@router.message(AdminReg.address)
async def admin_reg_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(AdminReg.loyiha_toifasi)
    await message.answer("Loyiha toifasini tanlang:", reply_markup=kb.category_kb)

# Project Params Flow
@router.callback_query(F.data.startswith("cat_"), AdminReg.loyiha_toifasi)
async def reg_cat(call: types.CallbackQuery, state: FSMContext):
    cats = {
        "cat_1": "🏢 1-QAVATLI TURAR-JOY OBEKTLARI", 
        "cat_2": "🏢 2-QAVATLI TURAR-JOY OBEKTLARI", 
        "cat_noturar": "🏢 3-NOTURAR-JOY OBEKTLARI", 
        "cat_comp": "💻 KOMPYUTER XIZMATLARI"
    }
    await state.update_data(loyiha_toifasi=cats[call.data])
    await state.set_state(AdminReg.service_type)
    await call.message.edit_text("Xizmat turini tanlang:", reply_markup=kb.get_services_kb(call.data))
    await call.answer()

@router.callback_query(F.data.startswith("svc_"), AdminReg.service_type)
async def reg_svc(call: types.CallbackQuery, state: FSMContext):
    svc_text = call.message.reply_markup.inline_keyboard[0][0].text # Default fallback
    for row in call.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == call.data:
                svc_text = btn.text
    
    await state.update_data(service_type=svc_text)
    await state.set_state(AdminReg.total_sum)
    await call.message.answer("To'liq shartnoma summasini raqamlarda kiriting:")
    await call.answer()

@router.callback_query(F.data.startswith("stg_"), AdminReg.stage)
async def reg_stage(call: types.CallbackQuery, state: FSMContext):
    stages = {"stg_1": "1-Bosqich", "stg_2": "2-Bosqich", "stg_3": "3-Bosqich"}
    await state.update_data(stage=stages[call.data])
    await state.set_state(AdminReg.tur)
    await call.message.edit_text("Loyiha turini tanlang:", reply_markup=kb.type_kb)
    await call.answer()

@router.callback_query(F.data.startswith("type_"), AdminReg.tur)
async def reg_tur(call: types.CallbackQuery, state: FSMContext):
    types_map = {"type_doc": "📋 LOYIHA HUJJATLARI", "type_sketch": "📋 ESKIZ LOYIHA", "type_work": "📋 ISHCHI LOYIHA"}
    await state.update_data(tur=types_map[call.data])
    await state.set_state(AdminReg.total_sum)
    await call.message.answer("To'liq shartnoma summasini raqamlarda kiriting:")
    await call.answer()

@router.message(AdminReg.total_sum)
async def reg_total(message: types.Message, state: FSMContext):
    try:
        val = float(message.text.replace(' ', ''))
        await state.update_data(total_sum=val)
        await state.set_state(AdminReg.paid_sum)
        await message.answer("To'langan summani raqamlarda kiriting:")
    except:
        await message.answer("Iltimos, raqam kiriting!")

@router.message(AdminReg.paid_sum)
async def reg_paid(message: types.Message, state: FSMContext):
    try:
        val = float(message.text.replace(' ', ''))
        await state.update_data(paid_sum=val)
        await state.set_state(AdminReg.payment_method)
        await message.answer("To'lov usulini tanlang:", reply_markup=kb.payment_kb)
    except:
        await message.answer("Iltimos, raqam kiriting!")

@router.message(AdminReg.payment_method)
async def reg_pay_method(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await state.set_state(AdminReg.receipt)
    await message.answer("To'lov chekini (rasm) yuboring yoki /skip tugmasini bosing:", reply_markup=kb.remove_kb)

@router.message(AdminReg.receipt)
async def reg_receipt(message: types.Message, state: FSMContext):
    receipt_id = message.photo[-1].file_id if message.photo else None
    data = await state.get_data()
    created_at = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    await db.add_user(data['user_id'], data['full_name'], data['address'], data['phone'], created_at)
    # Notify User about payment
    total = data['total_sum']
    paid = data['paid_sum']
    rem = total - paid
    
    msg = f"Loyiha: {data['user_id']} invoist uchun -{paid:,.0f} so'm tolov amalga oshirildi, Arizangiz ko'rib chiqish jarayonida"
    if rem > 0:
        msg += f", sizda qoldiq summa {rem:,.0f} so'mni tashkil etadi,"
    
    try:
        await message.bot.send_message(data['user_id'], msg)
    except: pass
    
    await state.clear()
    await message.answer("✅ Mijoz va loyiha muvaffaqiyatli saqlandi!", reply_markup=kb.admin_panel_kb)

# --- 2. Attach New Project ---
@router.callback_query(F.data == "attach_project")
async def attach_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AttachProject.user_id)
    await call.message.answer("Loyiha biriktirish uchun Mijoz ID-sini kiriting:")
    await call.answer()

@router.message(AttachProject.user_id)
async def attach_id(message: types.Message, state: FSMContext):
    user = await db.get_user(message.text)
    if user:
        await state.update_data(user_id=message.text)
        await state.set_state(AttachProject.loyiha_toifasi)
        await message.answer(f"Mijoz: {user['full_name']}\nLoyiha toifasini tanlang:", reply_markup=kb.category_kb)
    else:
        await message.answer("Bunday ID dagi mijoz topilmadi.")

@router.callback_query(F.data.startswith("cat_"), AttachProject.loyiha_toifasi)
async def att_cat(call: types.CallbackQuery, state: FSMContext):
    cats = {
        "cat_1": "🏢 1-QAVATLI TURAR-JOY OBEKTLARI", 
        "cat_2": "🏢 2-QAVATLI TURAR-JOY OBEKTLARI", 
        "cat_noturar": "🏢 3-NOTURAR-JOY OBEKTLARI", 
        "cat_comp": "💻 KOMPYUTER XIZMATLARI"
    }
    await state.update_data(loyiha_toifasi=cats[call.data])
    await state.set_state(AttachProject.service_type)
    await call.message.edit_text("Xizmat turini tanlang:", reply_markup=kb.get_services_kb(call.data))
    await call.answer()

@router.callback_query(F.data.startswith("svc_"), AttachProject.service_type)
async def att_svc(call: types.CallbackQuery, state: FSMContext):
    svc_text = ""
    for row in call.message.reply_markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == call.data:
                svc_text = btn.text
                
    await state.update_data(service_type=svc_text)
    await state.set_state(AttachProject.total_sum)
    await call.message.answer("To'liq shartnoma summasini kiriting:")
    await call.answer()

@router.callback_query(F.data.startswith("stg_"), AttachProject.stage)
async def att_stage(call: types.CallbackQuery, state: FSMContext):
    stages = {"stg_1": "1-Bosqich", "stg_2": "2-Bosqich", "stg_3": "3-Bosqich"}
    await state.update_data(stage=stages[call.data])
    await state.set_state(AttachProject.tur)
    await call.message.edit_text("Loyiha turini tanlang:", reply_markup=kb.type_kb)
    await call.answer()

@router.callback_query(F.data.startswith("type_"), AttachProject.tur)
async def att_tur(call: types.CallbackQuery, state: FSMContext):
    types_map = {"type_doc": "📋 LOYIHA HUJJATLARI", "type_sketch": "📋 ESKIZ LOYIHA", "type_work": "📋 ISHCHI LOYIHA"}
    await state.update_data(tur=types_map[call.data])
    await state.set_state(AttachProject.total_sum)
    await call.message.answer("To'liq shartnoma summasini kiriting:")
    await call.answer()

@router.message(AttachProject.total_sum)
async def att_total(message: types.Message, state: FSMContext):
    await state.update_data(total_sum=message.text)
    await state.set_state(AttachProject.paid_sum)
    await message.answer("To'langan summani kiriting:")

@router.message(AttachProject.paid_sum)
async def att_paid(message: types.Message, state: FSMContext):
    try:
        val = float(message.text.replace(' ', ''))
        await state.update_data(paid_sum=val)
        await state.set_state(AttachProject.payment_method)
        await message.answer("To'lov usulini tanlang:", reply_markup=kb.payment_kb)
    except:
        await message.answer("Iltimos, raqam kiriting!")

@router.message(AttachProject.payment_method)
async def att_pay_method(message: types.Message, state: FSMContext):
    await state.update_data(payment_method=message.text)
    await state.set_state(AttachProject.receipt)
    await message.answer("To'lov chekini (rasm) yuboring yoki /skip tugmasini bosing:", reply_markup=kb.remove_kb)

@router.message(AttachProject.receipt)
async def att_receipt(message: types.Message, state: FSMContext):
    receipt_id = message.photo[-1].file_id if message.photo else None
    data = await state.get_data()
    await db.update_user_project(data['user_id'], {**data, 'receipt_file_id': receipt_id})
    
    # Notify User about payment
    user_info = await db.get_user(data['user_id'])
    total = user_info['total_sum']
    paid = user_info['paid_sum']
    rem = total - paid
    
    msg = f"Loyiha: {data['user_id']} invoist uchun -{paid:,.0f} so'm tolov amalga oshirildi, Arizangiz ko'rib chiqish jarayonida"
    if rem > 0:
        msg += f", sizda qoldiq summa {rem:,.0f} so'mni tashkil etadi,"
        
    try:
        await message.bot.send_message(data['user_id'], msg)
    except: pass

    await state.clear()
    await message.answer("✅ Yangi loyiha muvaffaqiyatli biriktirildi!", reply_markup=kb.admin_panel_kb)

# --- 3. Search ---
@router.callback_query(F.data == "search_id")
async def search_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(SearchUser.user_id)
    await call.message.answer("Qidirish uchun ID kiritng:")
    await call.answer()

@router.message(SearchUser.user_id)
async def search_res(message: types.Message, state: FSMContext):
    user = await db.get_user(message.text)
    if user:
        resp = f"👤 Ism: {user['full_name']}\n🏢 Toifa: {user['loyiha_toifasi']}\n⚙️ Holat: {user['status']}"
        search_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 PDF Hujjat", callback_data=f"pdf_{user['tg_id']}")],
            [InlineKeyboardButton(text="⬅️ Admin Panel", callback_data="admin_panel")]
        ])
        await message.answer(resp, reply_markup=search_kb)
    else:
        await message.answer("Mijoz topilmadi.", reply_markup=kb.admin_panel_kb)
    await state.clear()

# --- 4. Change Status ---
@router.callback_query(F.data == "change_status")
async def status_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ChangeStatus.user_id)
    await call.message.answer("Mijoz ID-sini kiriting:")
    await call.answer()

@router.message(ChangeStatus.user_id)
async def status_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await state.set_state(ChangeStatus.status)
    await message.answer("Yangi holatni tanlang:", reply_markup=kb.status_kb)

@router.message(ChangeStatus.status)
async def status_final(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    await db.update_user_status(data['user_id'], message.text)
    await state.clear()
    await message.answer(f"✅ Holat o'zgartirildi.", reply_markup=kb.remove_kb)
    
    # Specific message based on screenshot
    user_info = await db.get_user(data['user_id'])
    if message.text == "Loyiha hujjatlaringiz tayyorlandi":
        if "KOMPYUTER XIZMATLARI" in user_info['loyiha_toifasi']:
            status_msg = "Loyiha tashkiloti tamonidan kalstatin xizmati bo'yicha xizmat faoliyati yakunadi"
        else:
            status_msg = "Loyixa xujjatlaringiz tayyorlandi,"
    else:
        status_msg = f"🔔 Loyihangiz holati: {message.text}"
        
    try:
        await message.bot.send_message(data['user_id'], status_msg)
    except: pass
    await message.answer("🛠 Admin Panel:", reply_markup=kb.admin_panel_kb)

# --- 5. Media ---
@router.callback_query(F.data == "send_media")
async def media_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(SendMedia.user_id)
    await call.message.answer("Mijoz ID-sini kiriting:")
    await call.answer()

@router.message(SendMedia.user_id)
async def media_id(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await state.set_state(SendMedia.media)
    await message.answer("Media yoki matn yuboring:")

@router.message(SendMedia.media)
async def media_final(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    try:
        await message.copy_to(data['user_id'])
        await message.answer("✅ Yuborildi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
    await state.clear()
    await message.answer("🛠 Admin Panel:", reply_markup=kb.admin_panel_kb)

# --- 6. Excel ---
@router.callback_query(F.data == "excel_report")
async def excel_rep(call: types.CallbackQuery):
    users = await db.get_all_users()
    file_path = f"report.xlsx"
    generate_report(users, file_path)
    await call.message.answer_document(types.FSInputFile(file_path))
    os.remove(file_path)
    await call.answer()

@router.callback_query(F.data == "pdf_report")
async def pdf_report_gen(call: types.CallbackQuery):
    users = await db.get_all_users()
    file_path = f"report.pdf"
    generate_full_report_pdf(users, file_path)
    await call.message.answer_document(types.FSInputFile(file_path), caption="📊 Barcha loyihalar (PDF hisoboti)")
    os.remove(file_path)
    await call.answer()

# --- 7. Individual PDF Generator ---
@router.callback_query(F.data.startswith("pdf_"))
async def send_user_pdf(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    user = await db.get_user(user_id)
    if user:
        file_path = f"loyiha_{user_id}.pdf"
        generate_user_pdf(user, file_path)
        doc = types.FSInputFile(file_path)
        await call.message.answer_document(doc, caption=f"📄 {user['full_name']} loyiha hujjati")
        os.remove(file_path)
    else:
        await call.answer("Mijoz ma'lumotlari topilmadi.", show_alert=True)
    await call.answer()

# --- 8. Add New Admin ---
@router.callback_query(F.data == "add_new_admin")
async def add_admin_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddAdmin.user_id)
    await call.message.answer("Yangi admin tayinlash uchun uning Telegram ID raqamini kiriting:")
    await call.answer()

@router.message(AddAdmin.user_id)
async def add_admin_final(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        await db.add_admin(new_admin_id)
        await state.clear()
        await message.answer(f"✅ ID: {new_admin_id} muvaffaqiyatli admin qilib tayinlandi!", reply_markup=kb.admin_panel_kb)
    except ValueError:
        await message.answer("Iltimos, faqat raqamlardan iborat ID kiriting!")

# --- 9. Remove Admin ---
@router.callback_query(F.data == "remove_admin")
async def remove_admin_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(RemoveAdmin.user_id)
    await call.message.answer("Adminlikdan bo'shatish uchun Telegram ID raqamini kiriting:")
    await call.answer()

@router.message(RemoveAdmin.user_id)
async def remove_admin_final(message: types.Message, state: FSMContext):
    try:
        admin_id = int(message.text)
        if admin_id == SUPER_ADMIN_ID:
            await message.answer("❌ Asosiy Super Adminni o'chirib bo'lmaydi!", reply_markup=kb.admin_panel_kb)
            await state.clear()
            return
        
        await db.delete_admin(admin_id)
        await state.clear()
        await message.answer(f"✅ ID: {admin_id} adminlar ro'yxatidan o'chirildi.", reply_markup=kb.admin_panel_kb)
    except ValueError:
        await message.answer("Iltimos, faqat raqamlardan iborat ID kiriting!")

# --- 10. Statistics ---
@router.callback_query(F.data == "stats")
async def stats_view(call: types.CallbackQuery):
    stats = await db.get_stats()
    debt = stats['total_contracts'] - stats['total_paid']
    resp = (
        f"📊 Loyihalar Statistikasi:\n\n"
        f"👥 Jami mijozlar: {stats['total_users']} ta\n"
        f"💰 Umumiy shartnomalar: {stats['total_contracts']:,.0f} so'm\n"
        f"✅ Jami to'langan: {stats['total_paid']:,.0f} so'm\n"
        f"❌ Jami qarzdorlik: {debt:,.0f} so'm"
    )
    await call.message.edit_text(resp, reply_markup=kb.admin_panel_kb)
    await call.answer()

# --- 11. Broadcast ---
@router.callback_query(F.data == "broadcast")
async def broadcast_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.message)
    await call.message.answer("Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring (Matn, Rasm, Video yoki Fayl bo'lishi mumkin):")
    await call.answer()

@router.message(BroadcastState.message)
async def broadcast_final(message: types.Message, state: FSMContext, bot):
    users = await db.get_all_users()
    count = 0
    await message.answer("🚀 Xabar yuborish boshlandi...")
    for user in users:
        try:
            await message.copy_to(user['tg_id'])
            count += 1
        except: pass
    await state.clear()
    await message.answer(f"✅ Xabar {count} ta foydalanuvchiga muvaffaqiyatli yuborildi!", reply_markup=kb.admin_panel_kb)
