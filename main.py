"""Головний модуль запуску Telegram-бота тестування з Python.

Ініціалізує екземпляри Bot та Dispatcher, підключає маршрутизатори (роутери),
запускає легковиковий HTTP-сервер для health-check на безкоштовному тарифі Render
та забезпечує стабільний Long Polling з автоперезапуском при мережевих збоях.
"""

import asyncio
import logging
import os
import sys
import time
from typing import Dict, Any

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, validate_config
from handlers import quiz_router

# Глобальний стан для моніторингу працездатності
STATE: Dict[str, Any] = {
    "start_time": time.time(),
    "bot_status": "starting",
    "last_error": None,
}


async def health_check_handler(request: web.Request) -> web.Response:
    """HTTP endpoint для перевірки стану бота сервісом Render та користувачем."""
    uptime_sec = int(time.time() - STATE["start_time"])
    status_text = (
        f"🤖 Telegram Python Quiz Bot is LIVE on Render!\n"
        f"• Status: {STATE['bot_status']}\n"
        f"• Uptime: {uptime_sec}s\n"
        f"• Telegram Link: https://t.me/bohdan_python_quiz_bot\n"
    )
    if STATE["last_error"]:
        status_text += f"\n⚠️ Last error: {STATE['last_error']}\n"

    return web.Response(
        text=status_text,
        content_type="text/plain",
        charset="utf-8",
        status=200
    )


async def start_health_server(port: int, logger: logging.Logger) -> web.AppRunner:
    """Запускає вбудований aiohttp вебсервер для прив'язки до порту Render."""
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    app.router.add_get("/health", health_check_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Вбудований вебсервер успішно запущено на 0.0.0.0:%d", port)
    return runner


async def poll_with_retry(bot: Bot, dp: Dispatcher, logger: logging.Logger) -> None:
    """Запускає polling у стійкому циклі з перехопленням мережевих помилок."""
    while True:
        try:
            STATE["bot_status"] = "running"
            STATE["last_error"] = None
            logger.info("Запуск aiogram polling...")
            await dp.start_polling(bot, handle_signals=False)
        except asyncio.CancelledError:
            logger.info("Polling скасовано.")
            break
        except Exception as exc:
            STATE["bot_status"] = "error"
            STATE["last_error"] = str(exc)
            logger.exception("Помилка під час polling: %s. Перезапуск через 5 сек...", exc)
            await asyncio.sleep(5)


async def main() -> None:
    """Точка входу в програму."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    validate_config()
    logger.info("Ініціалізація Telegram-бота...")

    session = AiohttpSession(timeout=60.0)
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(quiz_router)

    port = int(os.getenv("PORT", "10000"))
    runner = await start_health_server(port, logger)

    # Безпечне скидання webhook перед стартом
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning("Не вдалося скинути webhook (можливо мережева затримка): %s", e)

    logger.info("Бот готовий до роботи. Запуск polling циклу...")
    try:
        await poll_with_retry(bot, dp, logger)
    finally:
        await runner.cleanup()
        await bot.session.close()
        logger.info("Сесію бота завершено.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Процес завершено.")
