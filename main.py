import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    from config.settings import settings

    try:
        from database.connection import create_tables
        await create_tables()
        logger.info("✅ Database ulandi!")
    except Exception as e:
        logger.error(f"❌ Database xatosi: {e}")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    try:
        from middlewares.auth import AuthMiddleware
        dp.update.middleware(AuthMiddleware())
        logger.info("✅ Auth middleware ulandi!")
    except Exception as e:
        logger.error(f"❌ Middleware xatosi: {e}")

    try:
        from handlers.start import router as start_router
        dp.include_router(start_router)
        logger.info("✅ Start handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Start xatosi: {e}")
        logger.error(traceback.format_exc())

    try:
        from handlers.situation import router as situation_router
        dp.include_router(situation_router)
        logger.info("✅ Situation handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Situation xatosi: {e}")
        logger.error(traceback.format_exc())

    try:
        from handlers.document import router as document_router
        dp.include_router(document_router)
        logger.info("✅ Document handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Document xatosi: {e}")
        logger.error(traceback.format_exc())

    try:
        from handlers.profile import router as profile_router
        dp.include_router(profile_router)
        logger.info("✅ Profile handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Profile xatosi: {e}")
        logger.error(traceback.format_exc())

    try:
        from handlers.referral import router as referral_router
        dp.include_router(referral_router)
        logger.info("✅ Referral handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Referral xatosi: {e}")
        logger.error(traceback.format_exc())

    try:
        from handlers.admin import router as admin_router
        dp.include_router(admin_router)
        logger.info("✅ Admin handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Admin xatosi: {e}")
        logger.error(traceback.format_exc())
    try:
        from handlers.premium import router as premium_router
        dp.include_router(premium_router)
        logger.info("✅ Premium handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Premium xatosi: {e}")
        logger.error(traceback.format_exc())
    try:
        from handlers.settings import router as settings_router
        dp.include_router(settings_router)
        logger.info("✅ Settings handler ulandi!")
    except Exception as e:
        import traceback
        logger.error(f"❌ Settings xatosi: {e}")
        logger.error(traceback.format_exc())

    logger.info("🚀 ZIYRAK AI Bot ishga tushdi!")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())