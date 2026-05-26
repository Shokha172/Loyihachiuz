from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
from config import SUPER_ADMIN_ID, TIMEZONE, ENTERPRISE_NAME
from database import db
from states.states import UserReg
from keyboards import kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    if await db.is_admin(message.from_user.id):
        await message.answer(f"Xush kelibsiz, Admin! 🛠 Admin Panelga kirish uchun pastdagi tugmani bosing.", reply_markup=kb.admin_panel_kb)
    else:
        await message.answer(
            f"Salom! 🏢 {ENTERPRISE_NAME} botiga xush kelibsiz.\n\n"
            f"Loyiha xizmatlaridan foydalanish uchun ro'yxatdan o'ting.",
            reply_markup=kb.user_start_kb
        )

@router.callback_query(F.data == "register")
async def start_reg(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserReg.full_name)
    await call.message.answer("📝 To'liq Ism-familiyangizni kiriting:")
    await call.answer()

@router.message(UserReg.full_name)
async def reg_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(UserReg.phone)
    await message.answer("📱 Telefon raqamingizni yuboring:", reply_markup=kb.phone_kb)

@router.message(UserReg.phone, F.contact)
async def reg_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(UserReg.location)
    await message.answer("📍 Joylashgan manzilingizni (lokatsiya) yuboring:", reply_markup=kb.location_kb)

@router.message(UserReg.location, F.location)
async def reg_location(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    lat = message.location.latitude
    lon = message.location.longitude
    address_link = f"https://www.google.com/maps?q={lat},{lon}"
    
    created_at = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    
    await db.add_user(
        tg_id=message.from_user.id,
        full_name=data['full_name'],
        address=address_link,
        phone=data['phone'],
        created_at=created_at
    )
    
    await state.clear()
    await message.answer("✅ Ro'yxatdan muvaffaqiyatli o'tdingiz! Admin siz bilan tez orada bog'lanadi.", reply_markup=kb.remove_kb)
    
    # Notify Admin
    try:
        await bot.send_message(
            SUPER_ADMIN_ID,
            f"🆕 Yangi ariza!\n\n"
            f"👤 Mijoz: {data['full_name']}\n"
            f"📞 Tel: {data['phone']}\n"
            f"📍 Manzil: {address_link}\n"
            f"🆔 ID: {message.from_user.id}"
        )
    except Exception as e:
        print(f"Admin notification failed: {e}")

# Message Forwarding (Client to Admin)
@router.message(F.text & ~F.text.startswith('/'))
async def forward_to_admin(message: types.Message, bot):
    if not await db.is_admin(message.from_user.id):
        try:
            await bot.send_message(
                SUPER_ADMIN_ID,
                f"📨 Mijoz xabari: [{message.from_user.id}] - {message.text}"
            )
            await message.answer("Xabaringiz adminga yuborildi.")
        except Exception as e:
            print(f"Forwarding to admin failed: {e}")
            await message.answer("Xatolik: Admin hozirda xabar qabul qila olmaydi.")
