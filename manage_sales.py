from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from utils.logger import logger  # ✅ لاگر اضافه شد
from database.db import (
    get_all_sale_requests,
    complete_sale_request,
    reject_sale_request,
    update_balance,
    get_user_by_id
)

# 📦 نمایش لیست درخواست‌های فروش
async def list_sale_requests(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        logger.warning(f"⛔ دسترسی غیرمجاز به لیست فروش توسط: {message.from_user.id}")
        await message.reply("⛔ شما به این بخش دسترسی ندارید.")
        return

    try:
        requests = get_all_sale_requests()

        if not requests:
            logger.info("📭 هیچ درخواست فروش فعالی یافت نشد.")
            await message.answer("📭 هیچ درخواست فروش فعالی ثبت نشده است.")
            return

        logger.info(f"📦 لیست {len(requests)} درخواست فروش برای ادمین {message.from_user.id} نمایش داده شد.")
        for req in requests:
            user_id = req['user_id']
            inv_id = req['investment_id']
            plan = req['plan']
            product_type = req['type']
            price = req['price']
            date = req['date']
            username = req.get('username') or f"User {user_id}"

            text = (
                f"🛒 <b>درخواست فروش پلن:</b>\n\n"
                f"👤 <b>کاربر:</b> {username} | <code>{user_id}</code>\n"
                f"🚴‍♀️ <b>محصول:</b> {product_type} | <b>پلن:</b> {plan}\n"
                f"💵 <b>قیمت فروش:</b> <code>{price:.2f} USDT</code>\n"
                f"📅 <b>تاریخ خرید:</b> {date}\n"
                f"🆔 <b>ID سرمایه‌گذاری:</b> <code>{inv_id}</code>"
            )

            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("✅ تأیید و پرداخت", callback_data=f"approve_sale|{user_id}|{inv_id}|{price}"),
                InlineKeyboardButton("❌ رد درخواست", callback_data=f"reject_sale|{user_id}|{inv_id}")
            )

            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

    except Exception as e:
        logger.error(f"❌ خطا در نمایش لیست درخواست‌های فروش: {e}")
        await message.answer("❌ خطا در نمایش لیست فروش‌ها.")


# ✅ تأیید درخواست فروش و واریز وجه
async def approve_sale(callback: types.CallbackQuery):
    try:
        _, user_id, inv_id, amount = callback.data.split("|")
        user_id, inv_id = int(user_id), int(inv_id)
        amount = float(amount)

        update_balance(user_id, amount)
        complete_sale_request(user_id, inv_id)

        logger.success(f"✅ فروش پلن {inv_id} برای کاربر {user_id} تأیید شد. مبلغ: {amount} USDT")
        await callback.message.edit_text(
            f"✅ درخواست فروش <b>{inv_id}</b> تأیید شد.\n"
            f"💰 مبلغ <code>{amount:.2f} USDT</code> به حساب کاربر <code>{user_id}</code> اضافه شد.",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ خطا در تأیید فروش پلن {inv_id} برای کاربر {user_id}: {e}")
        await callback.message.edit_text(f"❌ خطا در تأیید فروش:\n<code>{str(e)}</code>", parse_mode="HTML")


# ❌ رد درخواست فروش
async def reject_sale(callback: types.CallbackQuery):
    try:
        _, user_id, inv_id = callback.data.split("|")
        user_id, inv_id = int(user_id), int(inv_id)

        reject_sale_request(user_id, inv_id)

        logger.info(f"🚫 درخواست فروش پلن {inv_id} از کاربر {user_id} رد شد.")
        await callback.message.edit_text(
            f"🚫 درخواست فروش <b>{inv_id}</b> از کاربر <code>{user_id}</code> رد شد.",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ خطا در رد فروش پلن {inv_id} از کاربر {user_id}: {e}")
        await callback.message.edit_text(f"❌ خطا در رد درخواست:\n<code>{str(e)}</code>", parse_mode="HTML")


# ✅ ثبت هندلر
def register_manage_sale_handlers(dp: Dispatcher):
    dp.register_message_handler(list_sale_requests, lambda m: m.text == "💸 مدیریت فروش دارایی", state="*")
    dp.register_callback_query_handler(approve_sale, lambda c: c.data.startswith("approve_sale|"))
    dp.register_callback_query_handler(reject_sale, lambda c: c.data.startswith("reject_sale|"))