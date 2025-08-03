from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from config import ADMIN_IDS
from utils.logger import logger  # ✅ اضافه شد
from database.db import (
    get_all_users,
    get_user_by_id,
    get_user_profit_info,
    update_balance,
    record_profit_payment
)

# 👨‍💼 نمایش لیست کاربران برای پرداخت سود دستی
async def show_users_for_profit(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ دسترسی غیرمجاز.")
        logger.warning(f"⛔ دسترسی غیرمجاز به سوددهی توسط کاربر: {message.from_user.id}")
        return

    users = get_all_users()
    if not users:
        await message.answer("📭 هیچ کاربری یافت نشد.")
        logger.info("📭 هیچ کاربری جهت پرداخت سود یافت نشد.")
        return

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for user in users:
        display_name = f"@{user['username']}" if user['username'] else f"User {user['user_id']}"
        keyboard.add(
            types.InlineKeyboardButton(
                f"👤 {display_name} ({user['user_id']})",
                callback_data=f"payprofit_{user['user_id']}"
            )
        )

    logger.info(f"👥 نمایش لیست کاربران برای پرداخت سود توسط ادمین: {message.from_user.id}")
    await message.answer("👥 لطفاً کاربر مورد نظر را برای پرداخت سود انتخاب کنید:", reply_markup=keyboard)


# 💸 پرداخت سود دستی به کاربر انتخاب‌شده
async def pay_profit_to_user(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        logger.warning(f"⛔ تلاش غیرمجاز برای پرداخت سود توسط: {callback.from_user.id}")
        return

    user_id = int(callback.data.split("_")[1])
    user = get_user_by_id(user_id)
    if not user:
        await callback.message.edit_text("❌ کاربر یافت نشد.")
        logger.error(f"❌ کاربر با آیدی {user_id} یافت نشد.")
        return

    profit_info = get_user_profit_info(user_id)
    if not profit_info:
        await callback.message.edit_text("❌ اطلاعات سوددهی برای این کاربر یافت نشد.")
        logger.error(f"❌ اطلاعات سوددهی برای کاربر {user_id} یافت نشد.")
        return

    amount = profit_info["weekly_profit"]
    has_bonus = profit_info.get("has_bonus", False)

    update_balance(user_id, amount)
    record_profit_payment(user_id, amount)

    text = (
        f"✅ سود هفتگی برای کاربر <code>{user_id}</code> با موفقیت واریز شد.\n"
        f"💰 <b>مبلغ:</b> <code>{amount:.2f} USDT</code>\n"
        f"{'🎉 <b>وضعیت:</b> VIP (دارای ۳ زیرمجموعه فعال)' if has_bonus else '👤 <b>وضعیت:</b> عادی'}"
    )
    await callback.message.edit_text(text, parse_mode="HTML")

    logger.success(f"💸 سود {amount:.2f} USDT برای کاربر {user_id} با {'وضعیت VIP' if has_bonus else 'عادی'} پرداخت شد.")

# ✅ ثبت هندلرها
def register_manage_profit_handlers(dp: Dispatcher):
    dp.register_message_handler(show_users_for_profit, Text("💰 پرداخت سود"), state="*")
    dp.register_callback_query_handler(pay_profit_to_user, lambda c: c.data.startswith("payprofit_"))