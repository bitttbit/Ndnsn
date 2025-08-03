from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import ADMIN_IDS
from utils.logger import logger  # ✅ لاگر اضافه شد
from database.db import get_all_users, set_vip_status, send_message_to_all

# 🎯 وضعیت‌های ماشین حالت برای ادمین
class AdminStates(StatesGroup):
    awaiting_vip_user_id = State()
    awaiting_broadcast_message = State()

# 📋 نمایش لیست کاربران
async def show_users(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"دسترسی غیرمجاز به لیست کاربران توسط {message.from_user.id}")
        await message.reply("⛔ شما دسترسی به پنل مدیریت ندارید.")
        return

    try:
        users = get_all_users()
        if not users:
            await message.answer("📭 هنوز هیچ کاربری ثبت‌نام نکرده است.")
            logger.info("📭 بدون کاربر در سیستم.")
            return

        text = "📋 <b>لیست کاربران ثبت‌شده:</b>\n\n"
        for user in users:
            uid = user.get("user_id")
            username = user.get("username") or "---"
            vip = "✅" if user.get("is_vip") else "❌"
            text += f"👤 <code>{uid}</code> - @{username} | VIP: {vip}\n"

        logger.info(f"👥 لیست کاربران برای ادمین {message.from_user.id} ارسال شد.")
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"❌ خطا در نمایش لیست کاربران: {e}")
        await message.answer("❌ خطا در نمایش لیست کاربران.")

# ⭐ شروع ارتقاء کاربر به VIP
async def ask_user_id_for_vip(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"دسترسی غیرمجاز به فرم VIP توسط {message.from_user.id}")
        return
    await message.answer("👤 لطفاً آیدی عددی کاربر را برای ارتقاء VIP وارد کنید:")
    await state.set_state(AdminStates.awaiting_vip_user_id)

# ✅ تنظیم کاربر به VIP
async def set_user_vip(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        success = set_vip_status(user_id, True)
        if success:
            logger.success(f"کاربر {user_id} با موفقیت VIP شد.")
            await message.answer(f"✅ کاربر <code>{user_id}</code> با موفقیت به VIP ارتقاء یافت.", parse_mode="HTML")
        else:
            logger.warning(f"❌ ارتقاء VIP ناموفق برای {user_id}")
            await message.answer("❌ کاربر یافت نشد یا مشکلی در ارتقاء رخ داد.")
    except ValueError:
        logger.warning(f"ورودی نامعتبر برای ارتقاء VIP: {message.text}")
        await message.answer("⚠️ لطفاً فقط عدد وارد کنید.")
    await state.finish()

# 📤 درخواست پیام همگانی از ادمین
async def ask_broadcast_message(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"⛔ دسترسی غیرمجاز به پیام همگانی توسط {message.from_user.id}")
        return
    await message.answer("📨 لطفاً پیام همگانی را وارد کنید:")
    await state.set_state(AdminStates.awaiting_broadcast_message)

# 📤 ارسال پیام همگانی به همه کاربران
async def send_broadcast(message: types.Message, state: FSMContext):
    try:
        count = await send_message_to_all(message.text)
        logger.success(f"📢 پیام همگانی برای {count} کاربر توسط {message.from_user.id}")
        await message.answer(f"📢 پیام برای <b>{count}</b> کاربر ارسال شد.", parse_mode="HTML")
    except Exception as e:
        logger.error(f"❌ خطا در ارسال پیام همگانی: {e}")
        await message.answer("❌ خطا در ارسال پیام همگانی.")
    await state.finish()

# ✅ ثبت هندلرها
def register_manage_user_handlers(dp: Dispatcher):
    dp.register_message_handler(show_users, lambda m: m.text == "👥 لیست کاربران")
    dp.register_message_handler(ask_user_id_for_vip, lambda m: m.text == "⭐ ارتقاء VIP", state="*")
    dp.register_message_handler(set_user_vip, state=AdminStates.awaiting_vip_user_id)
    dp.register_message_handler(ask_broadcast_message, lambda m: m.text == "📤 پیام همگانی", state="*")
    dp.register_message_handler(send_broadcast, state=AdminStates.awaiting_broadcast_message)