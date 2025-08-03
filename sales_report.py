from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from database.db import get_approved_sales
from utils.logger import logger  # لاگر مرکزی پروژه

# 📋 گزارش فروش‌های تأییدشده
async def show_sales_report(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ شما به این بخش دسترسی ندارید.")
        logger.warning(f"⛔ دسترسی غیرمجاز به گزارش فروش توسط: {message.from_user.id}")
        return

    try:
        sales = get_approved_sales()

        if not sales:
            await message.answer("📭 هیچ فروش تأییدشده‌ای ثبت نشده است.")
            return

        text = "📦 <b>آخرین فروش‌های تأییدشده:</b>\n\n"

        for s in sales[-10:]:  # فقط ۱۰ فروش آخر برای خلاصه‌سازی
            uid = s['user_id']
            username = s.get('username') or "---"
            plan = s['plan']
            product = s['product_type']
            amount = s['amount']
            date = s['request_date']

            text += (
                f"👤 <b>کاربر:</b> @{username} | <code>{uid}</code>\n"
                f"🔹 <b>پلن:</b> {product} | {plan}\n"
                f"💰 <b>مبلغ فروش:</b> <code>{amount:.2f} USDT</code>\n"
                f"📆 <b>تاریخ:</b> {date}\n"
                f"───────────────\n"
            )

        await message.answer(text.strip(), parse_mode="HTML")
        logger.info(f"📋 گزارش فروش ارسال شد توسط: {message.from_user.id}")

    except Exception as e:
        await message.answer("❌ خطا در دریافت گزارش فروش.")
        logger.error(f"[❌ گزارش فروش] توسط {message.from_user.id} → {e}")


# ✅ ثبت هندلر
def register_sales_report_handlers(dp: Dispatcher):
    dp.register_message_handler(show_sales_report, lambda m: m.text == "📊 گزارش فروش", state="*")