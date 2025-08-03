from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_IDS
from datetime import datetime
from utils.logger import logger  # اضافه شد
import sqlite3

DB_NAME = "rentalbot.db"

# 📥 دریافت لیست آخرین سرمایه‌گذاری‌ها
async def show_all_investments(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ شما دسترسی به این بخش ندارید.")
        logger.warning(f"⛔ تلاش غیرمجاز برای دسترسی به لیست سرمایه‌گذاری‌ها توسط: {message.from_user.id}")
        return

    logger.info(f"📥 ادمین {message.from_user.id} در حال مشاهده لیست سرمایه‌گذاری‌ها است.")

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # دریافت ۳۰ سرمایه‌گذاری اخیر
        c.execute('''
            SELECT inv.id, inv.user_id, inv.plan, inv.product_type, inv.percent, inv.start_date, u.username
            FROM investments inv
            JOIN users u ON u.user_id = inv.user_id
            ORDER BY inv.start_date DESC
            LIMIT 30
        ''')
        investments = c.fetchall()

        if not investments:
            await message.answer("📭 هنوز هیچ سرمایه‌گذاری ثبت نشده است.")
            logger.info("📭 هیچ سرمایه‌گذاری یافت نشد.")
            return

        # بررسی زیرمجموعه فعال برای هر کاربر
        referral_map = {}
        for inv in investments:
            user_id = inv[1]
            c.execute('''
                SELECT COUNT(*) FROM referrals r
                JOIN users u ON u.user_id = r.user_id
                WHERE r.inviter_id = ? AND u.active_investment = 1
            ''', (user_id,))
            referral_map[user_id] = c.fetchone()[0]

        conn.close()

        # ساخت پیام نهایی
        text = "📋 <b>آخرین ۳۰ سرمایه‌گذاری ثبت‌شده:</b>\n\n"
        for inv in investments:
            inv_id, user_id, plan, product_type, percent, start_date, username = inv
            percent_display = int(percent)
            date_display = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y/%m/%d")

            referral_count = referral_map.get(user_id, 0)
            is_vip = referral_count >= 3
            vip_status = "✅ VIP" if is_vip else "❌ عادی"

            text += (
                f"🆔 <b>ID:</b> {inv_id}\n"
                f"👤 <b>کاربر:</b> @{username or 'ندارد'} | <code>{user_id}</code>\n"
                f"🚴‍♀️ <b>محصول:</b> {product_type} | <b>پلن:</b> {plan} | <b>مالکیت:</b> {percent_display}%\n"
                f"🏷 <b>وضعیت:</b> {vip_status} | <b>زیرمجموعه فعال:</b> {referral_count} نفر\n"
                f"📅 <b>تاریخ شروع:</b> {date_display}\n"
                f"────────────\n"
            )

        await message.answer(text.strip(), parse_mode="HTML")
        logger.info(f"✅ لیست سرمایه‌گذاری‌ها برای ادمین {message.from_user.id} ارسال شد.")

    except Exception as e:
        await message.answer("❌ خطا در دریافت لیست سرمایه‌گذاری‌ها.")
        logger.error(f"❌ خطا در دریافت لیست سرمایه‌گذاری‌ها توسط ادمین {message.from_user.id}: {e}")

# ✅ ثبت هندلر
def register_manage_investment_handlers(dp: Dispatcher):
    dp.register_message_handler(show_all_investments, commands=["investments_list"])