from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.db import get_sellable_investments, log_sale_request
from config_view import back_to_menu
from utils.logger import logger  # ✅ سیستم لاگ‌گیری مرکزی

# 🎯 وضعیت مربوط به فروش پلن
class SellStates(StatesGroup):
    choosing_plan = State()

# 🛒 شروع فرآیند فروش پلن
async def ask_sellable_plans(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    logger.info(f"📩 فروش: شروع بررسی پلن‌های قابل فروش توسط {user_id}")

    try:
        plans = get_sellable_investments(user_id)

        if not plans:
            await callback_query.message.edit_text(
                "❌ شما هیچ پلنی برای فروش ندارید.\n"
                "🕒 فقط پلن‌هایی که بیش از ۳۰ روز از خرید آن‌ها گذشته باشد قابل فروش هستند.",
                reply_markup=back_to_menu()
            )
            logger.warning(f"❌ کاربر {user_id} هیچ پلن قابل فروشی ندارد.")
            return

        text = "🛒 پلن‌های قابل فروش شما:\n\n"
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        for plan in plans:
            plan_id = plan['id']
            plan_type = plan['type']
            plan_name = plan['plan']
            buy_date = plan['date']
            ownership = plan['ownership']
            amount_paid = plan['amount']

            btn_text = f"{plan_type} | {plan_name} | {ownership}% | {buy_date}"
            callback_data = f"sell_{plan_id}"

            keyboard.add(types.InlineKeyboardButton(text=btn_text, callback_data=callback_data))
            text += f"• {btn_text}\n"

        keyboard.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_menu"))

        await callback_query.message.edit_text(text.strip(), reply_markup=keyboard)
        await SellStates.choosing_plan.set()
        logger.info(f"📋 کاربر {user_id} لیست پلن‌های قابل فروش را مشاهده کرد.")

    except Exception as e:
        logger.error(f"❌ خطا در نمایش پلن‌های فروش برای کاربر {user_id} → {e}")
        await callback_query.message.edit_text("❌ خطا در دریافت اطلاعات پلن‌ها.", reply_markup=back_to_menu())


# ✅ ثبت درخواست فروش
async def confirm_sell_request(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if not data.startswith("sell_"):
        return

    try:
        investment_id = int(data.split("_")[1])
        log_sale_request(user_id, investment_id)

        await callback_query.message.edit_text(
            "✅ درخواست فروش شما با موفقیت ثبت شد.\n"
            "💸 مبلغ فروش طی ۲۴ ساعت آینده به کیف پول داخلی شما اضافه خواهد شد.",
            reply_markup=back_to_menu()
        )
        logger.info(f"📝 درخواست فروش برای پلن {investment_id} توسط کاربر {user_id} ثبت شد.")

    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ خطا در ثبت درخواست فروش:\n<code>{str(e)}</code>",
            reply_markup=back_to_menu(),
            parse_mode="HTML"
        )
        logger.error(f"❌ خطا در ثبت فروش پلن {data} توسط {user_id} → {e}")

    finally:
        await state.finish()


# 🛠 ثبت هندلرها
def register_sell_plan_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(ask_sellable_plans, lambda c: c.data == "sell_plan", state="*")
    dp.register_callback_query_handler(confirm_sell_request, lambda c: c.data.startswith("sell_"), state=SellStates.choosing_plan)