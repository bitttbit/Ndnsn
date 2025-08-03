from aiogram import types, Dispatcher
from config import ADMIN_IDS
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.logger import logger

# 📋 منوی مدیریت برای ادمین‌ها
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ شما به این بخش دسترسی ندارید.")
        logger.warning(f"⛔ دسترسی غیرمجاز به پنل ادمین توسط: {message.from_user.id}")
        return

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("👥 لیست کاربران"),
        KeyboardButton("⭐ ارتقاء VIP"),
        KeyboardButton("📤 پیام همگانی")
    )
    keyboard.add(
        KeyboardButton("💰 پرداخت سود"),
        KeyboardButton("📋 لیست سرمایه‌گذاری‌ها")
    )
    keyboard.add(
        KeyboardButton("💸 مدیریت فروش دارایی"),
        KeyboardButton("🔙 بازگشت به منو")
    )

    await message.answer("🎛 به پنل مدیریت خوش آمدید:", reply_markup=keyboard)
    logger.info(f"✅ پنل مدیریت باز شد توسط: {message.from_user.id}")

# 📌 ثبت هندلر
def register_admin_panel(dp: Dispatcher):
    dp.register_message_handler(admin_panel, lambda m: m.text == "🛠 مدیریت")