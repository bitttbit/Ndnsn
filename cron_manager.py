import sqlite3
from datetime import datetime, timedelta
from aiogram import Dispatcher, types
from config import bot, ADMIN_IDS, DB_NAME
from database.db import record_profit_payment, get_user_by_id
from utils.referral_utils import has_3_active_referrals_same_plan

# 🔁 تنظیمات
WEEK_DAYS_WAIT = 7
MAX_WITHDRAWALS_PER_MONTH = 4

# 📌 جدول سوددهی پلن‌ها (برای ۱۰۰٪ مالکیت)
PLAN_CONFIG = {
    "دوچرخه": {
        "برنز": {"price": 500, "daily_income": 20, "base_share": 0.5, "boosted_share": 0.7},
        "گلد": {"price": 1500, "daily_income": 70, "base_share": 0.6, "boosted_share": 0.8},
        "الماس": {"price": 3000, "daily_income": 128, "base_share": 0.7, "boosted_share": 0.9},
    },
    "اسکوتر": {
        "برنز": {"price": 250, "daily_income": 10, "base_share": 0.5, "boosted_share": 0.7},
        "گلد": {"price": 750, "daily_income": 42, "base_share": 0.6, "boosted_share": 0.8},
        "الماس": {"price": 1500, "daily_income": 88, "base_share": 0.7, "boosted_share": 0.9},
    }
}

# ⏱ اجرای سوددهی هفتگی به صورت خودکار
async def run_cron_profit_distribution():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        today = datetime.today()
        week_ago = today - timedelta(days=WEEK_DAYS_WAIT)
        this_month = today.strftime("%Y-%m")

        # دریافت سرمایه‌گذاری‌های واجد شرایط (حداقل ۷ روز گذشته باشد)
        c.execute('''
            SELECT id, user_id, plan, product_type, percent, start_date
            FROM investments
            WHERE DATE(start_date) <= DATE(?)
        ''', (week_ago.strftime('%Y-%m-%d'),))
        investments = c.fetchall()

        for inv_id, user_id, plan, product_type, percent, start_date in investments:
            # محدودیت ۴ سود در ماه برای هر کاربر
            c.execute('SELECT COUNT(*) FROM profit_history WHERE user_id = ? AND date LIKE ?', (user_id, f"{this_month}-%"))
            if c.fetchone()[0] >= MAX_WITHDRAWALS_PER_MONTH:
                continue

            config = PLAN_CONFIG.get(product_type, {}).get(plan)
            if not config:
                continue

            # بررسی وضعیت زیرمجموعه برای سود بیشتر
            has_boost = has_3_active_referrals_same_plan(user_id, plan, product_type)
            share = config["boosted_share"] if has_boost else config["base_share"]

            # محاسبه سود کاربر
            daily_income = config["daily_income"] * (percent / 100)
            weekly_profit = round(daily_income * 7 * share, 2)

            # ثبت در جدول سود
            record_profit_payment(user_id, weekly_profit)

            # ارسال پیام به کاربر
            user = get_user_by_id(user_id)
            if user:
                try:
                    await bot.send_message(
                        user_id,
                        f"""
💸 <b>سود هفتگی شما واریز شد</b>

🛠 <b>پلن:</b> {plan} ({product_type})
📈 <b>درصد مالکیت:</b> {percent}٪
💵 <b>سهم سود:</b> {int(share * 100)}٪ {'🎉 (افزایش‌یافته با ۳ زیرمجموعه فعال)' if has_boost else ''}
📆 <b>تاریخ:</b> {today.strftime('%Y-%m-%d')}
💰 <b>سود این هفته:</b> <code>{weekly_profit:.2f} USDT</code>
                        """.strip(),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"[❌] خطا در ارسال پیام به کاربر {user_id}: {e}")
    except Exception as e:
        print(f"[CRON ERROR] {e}")
    finally:
        conn.close()

# 🛠 اجرای دستی توسط ادمین
async def manual_cron_trigger(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("⛔ شما دسترسی به این بخش ندارید.")
        return

    await run_cron_profit_distribution()
    await message.reply("✅ سوددهی هفتگی با موفقیت اجرا شد.")

# ✅ ثبت هندلر در Dispatcher
def register_cron_handlers(dp: Dispatcher):
    dp.register_message_handler(manual_cron_trigger, commands=["run_cron"])