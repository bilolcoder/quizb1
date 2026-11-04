import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from config import BOT_TOKEN, ADMIN_ID, setup_logging
from database import init_db
from handlers import setup_routers
from services.quiz_service import QuizService

logger = logging.getLogger("bot")


async def on_startup(bot: Bot) -> None:
    """Bot ishga tushganda bajariladigan amallar."""
    # 1. Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # 2. Savollar bazasini tekshirish va yuklash
    questions = QuizService.load_questions()
    logger.info("Savollar bazasi tayyor: jami %d ta savol.", len(questions))

    # 3. Bot ma'lumotlarini olish
    me = await bot.get_me()
    logger.info("Bot muvaffaqiyatli ishga tushdi: @%s (ID: %d)", me.username, me.id)
    logger.info("Administrator ID: %d", ADMIN_ID)


async def main() -> None:
    """Asosiy ishga tushirish funksiyasi."""
    setup_logging()
    logger.info("Bot sozlamalari yuklanmoqda...")

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "XATOLIK: BOT_TOKEN aniqlanmadi yoki standart holatda qolgan!\n"
            "Iltimos, .env faylini oching va Telegram @BotFather dan olingan\n"
            "haqiqiy tokenni BOT_TOKEN parametriga kiriting.\n"
            "=" * 60
        )
        print(
            "\n[XATOLIK] .env fayliga haqiqiy BOT_TOKEN kiritilmagan!\n"
            "Iltimos, .env faylidagi 'YOUR_BOT_TOKEN' o'rniga @BotFather tokenini yozing.\n"
        )
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Xatoliklarni ushlovchi global handler
    @dp.error()
    async def global_error_handler(event: ErrorEvent):
        logger.exception("Kutilmagan xatolik yuz berdi: %s", event.exception)
        try:
            if event.update.message:
                await event.update.message.answer(
                    "⚠️ Kutilmagan texnik nosozlik yuz berdi. Iltimos, qaytadan urinib ko‘ring."
                )
            elif event.update.callback_query:
                await event.update.callback_query.answer(
                    "⚠️ Texnik xatolik yuz berdi.", show_alert=True
                )
        except Exception:
            pass

    # Routerlarni ulash
    setup_routers(dp)

    # Startup tadbirlari
    await on_startup(bot)

    # Eski kutilayotgan yangilanishlarni tozalash va pollingni boshlash
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Polling boshlanmoqda...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot faoliyati to‘xtatildi.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot foydalanuvchi tomonidan to‘xtatildi.")
    except Exception as e:
        logger.critical("Botni ishga tushirishda jiddiy xatolik: %s", e, exc_info=True)
        sys.exit(1)

