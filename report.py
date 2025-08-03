from aiogram import types
from loader import dp
from database.db import (
    get_all_withdrawals,
    get_all_profits,
    get_all_investments
)
from datetime import datetime
from config import ADMIN_IDS
from utils.logger import logger  # ✅ افزودن لاگر برای پیگیری ادمین

# 📊 گزارش مدیریتی RideFund برای ادمین
@dp.message_handler(commands=["admin_report"])
async def send_admin_report(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ شما به این بخش دسترسی ندارید.")
        logger.warning(f"⛔ تلاش دسترسی غیرمجاز به گزارش توسط: {message.from_user.id}")
        return

    try:
        withdrawals = get_all_withdrawals()
        profits = get_all_profits()
        investments = get_all_investments()

        report = "📊 <b>گزارش کلی عملکرد سیستم RideFund</b>\n\n"

        # 💸 آخرین برداشت‌ها
        report += f"<b>💵 آخرین برداشت‌ها ({len(withdrawals)} کل):</b>\n"
        for w in withdrawals[-10:]:
            uid = w['user_id']
            amount = w['amount']
            status = w['status']
            date_str = w.get('request_date', 'نامشخص')
            report += f"🔹 <code>{uid}</code> | <b>{amount:.2f} USDT</b> | وضعیت: {status} | 📅 {date_str}\n"
        report += "\n"

        # 📈 آخرین پرداخت‌های سود
        report += f"<b>📈 آخرین پرداخت سود ({len(profits)} مورد):</b>\n"
        for p in profits[-10:]:
            uid = p['user_id']
            amount = p['amount']
            date_str = p.get('date', 'نامشخص')
            report += f"🔸 <code>{uid}</code> | 💰 <b>{amount:.2f} USDT</b> | 📅 {date_str}\n"
        report += "\n"

        # 🛒 آخرین سرمایه‌گذاری‌ها
        report += f"<b>📦 آخرین سرمایه‌گذاری‌ها ({len(investments)} کل):</b>\n"
        for i in investments[-10:]:
            uid = i[1]
            asset = i[2]
            plan = i[3]
            date = i[5]
            percent = i[6]
            report += f"🧩 <code>{uid}</code> | {asset} - {plan} | مالکیت: <b>{percent}%</b> | 📆 {date}\n"

        # 📆 زمان گزارش
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        report += f"\n🕒 <i>تاریخ گزارش: {now}</i>"

        await message.answer(report, parse_mode="HTML")
        logger.info(f"📤 گزارش ادمین توسط {message.from_user.id} ارسال شد.")

    except Exception as e:
        await message.answer("❌ خطا در تولید گزارش مدیریتی.")
        logger.error(f"[Report Error] ادمین {message.from_user.id} → {e}")