import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from app.settings import settings
from app.text2sql import text2sql

dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    await message.reply(
        "Привет!\n"
        "Это бот, который отвечает на вопросы на основе аналитики видео."
        "Бот способен отвечать только одним коротким сообщеним, "
        "так что вопросы должны быть соответствующие:\n"
        "- Какие видео имеют больше просмотров, чем в среднем? ❌\n"
        "- Сколько всего видео есть в системе? ✅"
    )


@dp.message()
async def echo(message: types.Message) -> None:
    await message.answer(
        text2sql(message.text)
        if message.text is not None
        else "Некорректное сообщение. Попробуйте ещё раз"
    )


async def main() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(main())
