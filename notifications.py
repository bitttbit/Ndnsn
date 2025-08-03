from aiogram import Dispatcher
from datetime import datetime, timedelta
from database.db import get_all_investments, get_user_by_id
from config import bot
from utils.logger import logger  # ✅ اضافه‌شدن لاگر

# 📤 نوتیف سود هفتگی قابل برداشت
async def notify_weekly_profit():
    investments = get_all_investments()
    now = datetime.now()
    notified = 0

    for inv in investments:
        inv_id = inv[0]
        user_id = inv[1]
        product_type = inv[2]
        plan = inv[3]
        percent = inv[4]
        start_date_str = inv[5]

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except Exception as e:
            logger.warning(f"[⛔ خطا در تبدیل تاریخ] ID سرمایه‌گذاری {inv_id} → {e}")
            continue

        days_passed = (now - start_date).days
        if days_passed >= 7:
            user = get_user_by_id(user_id)
            if user:
                try:
                    ownership = int(percent * 100)
                    is_vip = user.get("is_vip", False)
                    bonus_note = (
                        "🎉 سود شما با سهم ارتقاءیافته (VIP) محاسبه می‌شود."
                        if is_vip else "📊 سود شما طبق سهم پایه محاسبه می‌شود."
                    )

                    await bot.send_message(
                        user_id,
                        f"📢 سود پلن <b>{plan}</b> ({product_type}) با مالکیت <b>{ownership}%</b> شما اکنون قابل برداشت است!\n"
                        f"⏱ <i>{days_passed} روز</i> از تاریخ سرمایه‌گذاری گذشته است.\n"
                        f"{bonus_note}\n\n"
                        "برای دریافت سود، از گزینه <b>💸 برداشت</b> در منو استفاده کنید.",
                        parse_mode="HTML"
                    )
                    notified += 1
                except Exception as e:
                    logger.error(f"[❌ خطا در ارسال پیام سود] کاربر {user_id} → {e}")

    logger.success(f"✅ نوتیف سود برای {notified} کاربر ارسال شد.")

# 📤 نوتیف تأیید فروش پلن
async def notify_sale_request_accepted(user_id: int, amount: float):
    try:
        await bot.send_message(
            user_id,
            f"✅ درخواست فروش پلن شما با موفقیت تأیید شد.\n"
            f"💵 مبلغ <b>{amount:.2f} USDT</b> طی <b>۲۴ ساعت آینده</b> به حساب شما واریز خواهد شد.\n"
            "📌 برای مشاهده وضعیت موجودی، از گزینه <b>📊 داشبورد</b> استفاده کنید.",
            parse_mode="HTML"
        )
        logger.info(f"📤 نوتیف تأیید فروش برای کاربر {user_id} ارسال شد.")
    except Exception as e:
        logger.error(f"[❌ خطا در ارسال پیام فروش] کاربر {user_id} → {e}")

# 🛠 تابع ثبت هندلرها (در صورت نیاز به استفاده مستقیم)
def register_notification_handlers(dp: Dispatcher):
    # فعلاً هندلر مستقیم نیاز ندارد
    pass