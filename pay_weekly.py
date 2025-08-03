from aiogram import types
from loader import dp, bot
from database.db import (
    get_all_investments, get_user_by_id,
    update_balance, record_profit_payment
)
from handlers.calculation import calculate_profit
from utils.referral_utils import has_3_active_referrals_same_plan
from utils.logger import logger
from datetime import datetime

# لیست ادمین‌ها
ADMIN_IDS = [123456789]  # ← آیدی ادمین را با مقدار واقعی جایگزین کن

# 📤 اجرای دستی سوددهی هفتگی برای همه کاربران
@dp.message_handler(commands=["admin_pay_profits"])
async def handle_weekly_payout(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ شما دسترسی به این بخش ندارید.")
        logger.warning(f"⛔ دسترسی غیرمجاز به سوددهی دستی توسط: {message.from_user.id}")
        return

    investments = get_all_investments()
    count = 0
    today = datetime.today().strftime("%Y-%m-%d")
    logger.info(f"📤 سوددهی دستی توسط {message.from_user.id} آغاز شد.")

    for inv in investments:
        user_id = inv[1]
        asset_type = inv[2]
        plan_type = inv[3]
        start_date = inv[5]
        ownership = inv[6]

        if not user_id or not asset_type or not plan_type:
            logger.warning(f"[❌] داده ناقص در سرمایه‌گذاری: {inv}")
            continue

        user = get_user_by_id(user_id)
        if not user:
            logger.warning(f"[❌] کاربر یافت نشد: {user_id}")
            continue

        has_referrals = has_3_active_referrals_same_plan(user_id, plan_type, asset_type)

        result = calculate_profit(asset_type, plan_type, ownership, has_referrals, start_date)
        if "error" in result:
            logger.error(f"[❌] خطا در محاسبه سود برای {user_id} → {result['error']}")
            continue

        weekly_profit = round(result["weekly_profit"], 2)
        update_balance(user_id, weekly_profit)
        record_profit_payment(user_id, weekly_profit)

        try:
            await bot.send_message(
                user_id,
                f"🎉 سود هفتگی پلن <b>{plan_type}</b> برای {asset_type} شما به مبلغ <b>{weekly_profit} USDT</b> واریز شد.\n"
                f"📆 تاریخ واریز: {today}\n"
                f"{'🎁 سود افزایش‌یافته با داشتن ۳ زیرمجموعه فعال' if has_referrals else '📉 سود پایه (بدون زیرمجموعه)'}",
                parse_mode="HTML"
            )
            count += 1
        except Exception as e:
            logger.error(f"[❗] خطا در ارسال پیام سود به {user_id}: {e}")

    await message.answer(
        f"✅ پرداخت سود هفتگی با موفقیت برای <b>{count}</b> کاربر انجام شد.",
        parse_mode="HTML"
    )
    logger.info(f"✅ پرداخت سود به {count} کاربر تکمیل شد.")