from aiogram import types, Dispatcher
from config import ADMIN_IDS, DB_NAME
import sqlite3
from utils.logger import logger  # ✅ لاگر مرکزی پروژه

# 📊 ارسال آمار کلی سیستم به ادمین
async def send_admin_stats(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ADMIN_IDS:
        await message.reply("⛔ شما دسترسی به پنل مدیریت ندارید.")
        logger.warning(f"⛔ دسترسی غیرمجاز به آمار ادمین توسط: {user_id}")
        return

    try:
        # اتصال به دیتابیس
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()

            # آمار کاربران
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]

            # آمار سرمایه‌گذاری‌ها
            c.execute('SELECT COUNT(*) FROM investments')
            total_investments = c.fetchone()[0]

            # آمار برداشت‌ها
            c.execute('SELECT COUNT(*), SUM(amount) FROM withdrawals')
            withdraw_count, total_withdrawn = c.fetchone()
            withdraw_count = withdraw_count or 0
            total_withdrawn = total_withdrawn or 0

            # مجموع سود پرداخت‌شده
            c.execute('SELECT SUM(amount) FROM profit_history')
            total_profit_paid = c.fetchone()[0] or 0

            # درخواست‌های فروش
            c.execute('SELECT COUNT(*) FROM sale_requests')
            total_sales = c.fetchone()[0]

            # مجموع سرمایه‌گذاری دلاری
            c.execute('SELECT SUM(amount) FROM investments')
            total_amount = c.fetchone()[0] or 0

            # تعداد کاربران با ≥ ۳ زیرمجموعه
            c.execute('''
                SELECT inviter_id FROM referrals
                GROUP BY inviter_id
                HAVING COUNT(*) >= 3
            ''')
            strong_referrers = len(c.fetchall())

        # متن پیام نهایی
        stats_text = f"""
<b>📊 آمار کلی سیستم RideFund:</b>
━━━━━━━━━━━━━━━━━━━━
👥 <b>تعداد کاربران:</b> {total_users:,}
🚴 <b>تعداد سرمایه‌گذاری‌ها:</b> {total_investments:,}
💰 <b>حجم کل سرمایه‌گذاری:</b> <code>{total_amount:,.2f} USDT</code>
🏦 <b>تعداد برداشت‌ها:</b> {withdraw_count:,} مرتبه — <code>{total_withdrawn:,.2f} USDT</code>
📈 <b>مجموع سود پرداخت‌شده:</b> <code>{total_profit_paid:,.2f} USDT</code>
🛒 <b>درخواست‌های فروش:</b> {total_sales:,}
🤝 <b>کاربران با ≥ ۳ زیرمجموعه:</b> {strong_referrers:,}
━━━━━━━━━━━━━━━━━━━━
        """

        await message.answer(stats_text.strip(), parse_mode="HTML")
        logger.info(f"✅ آمار کامل به ادمین {user_id} ارسال شد.")

    except Exception as e:
        logger.exception("❌ خطا در دریافت آمار کلی سیستم")
        await message.reply("❌ خطا در دریافت آمار. لطفاً بعداً تلاش کنید.")

# ✅ ثبت هندلر
def register_admin_stats_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_stats, commands=["admin_stats"])