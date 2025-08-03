from aiogram import types, Dispatcher
from database.db import get_user_investments, get_user_referrals, get_user_by_id
from datetime import datetime, timedelta
from utils.logger import logger  # ✅ سیستم لاگ‌گیری

# 📅 محاسبه تاریخ‌های پرداخت سود هر ۷ روز یکبار از تاریخ شروع سرمایه‌گذاری
def get_available_payouts(start_date_str):
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        today = datetime.today()
        payouts = []

        check_date = start_date + timedelta(days=7)
        while check_date <= today:
            payouts.append(check_date.strftime("%Y-%m-%d"))
            check_date += timedelta(days=7)

        return payouts
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه تاریخ‌های پرداخت سود: {e}")
        return []

# 💰 محاسبه درصد سود بر اساس نوع پلن و داشتن ۳ زیرمجموعه فعال
def get_profit_percent(product_type, plan, has_3_referrals):
    try:
        if product_type == "دوچرخه":
            return {
                "برنز": 70 if has_3_referrals else 50,
                "گلد": 80 if has_3_referrals else 60,
                "الماس": 90 if has_3_referrals else 70
            }.get(plan, 0)
        elif product_type == "اسکوتر":
            return {
                "برنز": 70 if has_3_referrals else 50,
                "گلد": 80 if has_3_referrals else 60,
                "الماس": 90 if has_3_referrals else 70
            }.get(plan, 0)
        return 0
    except Exception as e:
        logger.error(f"❌ خطا در محاسبه درصد سود: {e}")
        return 0

# 📊 نمایش تقویم سودهای قابل دریافت برای کاربر
async def show_user_profit_calendar(message: types.Message):
    user_id = message.from_user.id
    logger.info(f"📅 درخواست تقویم سود توسط کاربر: {user_id}")

    try:
        investments = get_user_investments(user_id)

        if not investments:
            await message.answer("⛔ شما هنوز سرمایه‌گذاری فعالی ندارید.")
            logger.info(f"⛔ کاربر {user_id} هیچ سرمایه‌گذاری ندارد.")
            return

        # بررسی زیرمجموعه‌های فعال
        referrals = get_user_referrals(user_id)
        referral_count = 0
        for ref_user in referrals:
            ref_data = get_user_by_id(ref_user["user_id"])
            if ref_data and ref_data.get("active_investment", False):
                referral_count += 1
        has_3_referrals = referral_count >= 3

        # ساخت تقویم پرداخت
        text = "📅 <b>تقویم پرداخت سود برای سرمایه‌گذاری‌های فعال شما:</b>\n\n"
        found = False

        for inv in investments:
            plan = inv["plan"]
            product_type = inv["product_type"]
            start_date = inv["start_date"]

            percent = get_profit_percent(product_type, plan, has_3_referrals)
            payout_dates = get_available_payouts(start_date)

            if not payout_dates:
                continue

            found = True
            text += f"🔹 <b>{product_type} - {plan}</b> (از {start_date})\n"
            text += f"📈 درصد سود شما: <b>{percent}%</b>\n"
            for i, d in enumerate(payout_dates, 1):
                text += f"  {i}️⃣ {d}\n"
            text += "\n"

        if not found:
            await message.answer("⏱ هنوز به زمان اولین پرداخت سود نرسیده‌اید.")
            logger.info(f"⏱ کاربر {user_id} هنوز سودی برای دریافت ندارد.")
        else:
            await message.answer(text.strip(), parse_mode="HTML")
            logger.info(f"✅ تقویم پرداخت سود برای کاربر {user_id} ارسال شد.")

    except Exception as e:
        await message.answer("❌ خطا در دریافت تقویم سود. لطفاً بعداً تلاش کنید.")
        logger.exception(f"❌ خطا در نمایش تقویم سود کاربر {user_id}: {e}")

# ✅ ثبت هندلر
def register_calendar_ui_handlers(dp: Dispatcher):
    dp.register_message_handler(show_user_profit_calendar, commands=["calendar"])