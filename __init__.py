# 🔹 ایمپورت لاگر مرکزی
from utils.logger import logger

# 🔹 ایمپورت هندلرهای اصلی ادمین
from .panel import register_admin_panel_handlers
from .manage_users import register_manage_user_handlers

# 🔹 ایمپورت هندلرهای دیگر ماژول‌های ادمین
from .manage_investments import register_manage_investment_handlers
from .notifications import register_notification_handlers
from .cron_manager import register_cron_handlers
from .calendar_ui import register_calendar_ui_handlers
from .admin_stats import register_admin_stats_handlers
from .config_view import register_config_view_handlers
from .manage_sales import register_manage_sale_handlers
from .manage_profit import register_manage_profit_handlers  # ✅ پرداخت سود

# 🔧 تابع نهایی برای ثبت تمام هندلرهای ادمین
def register_admin_handlers(dp):
    register_admin_panel_handlers(dp)
    logger.info("✅ هندلر پنل ادمین ثبت شد.")

    register_manage_user_handlers(dp)
    logger.info("✅ هندلر مدیریت کاربران ثبت شد.")

    register_manage_investment_handlers(dp)
    logger.info("✅ هندلر مدیریت سرمایه‌گذاری‌ها ثبت شد.")

    register_notification_handlers(dp)
    logger.info("✅ هندلر نوتیفیکیشن‌ها ثبت شد.")

    register_cron_handlers(dp)
    logger.info("✅ هندلر Cron Job ثبت شد.")

    register_calendar_ui_handlers(dp)
    logger.info("✅ هندلر تقویم پرداخت ثبت شد.")

    register_admin_stats_handlers(dp)
    logger.info("✅ هندلر آمار ادمین ثبت شد.")

    register_config_view_handlers(dp)
    logger.info("✅ هندلر مشاهده تنظیمات ثبت شد.")

    register_manage_sale_handlers(dp)
    logger.info("✅ هندلر مدیریت فروش دارایی ثبت شد.")

    register_manage_profit_handlers(dp)
    logger.info("✅ هندلر پرداخت سود ثبت شد.")