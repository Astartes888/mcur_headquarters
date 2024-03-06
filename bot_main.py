import asyncio

from bot_init import bd, bot
from handlers import menu, registration, reports, close
from middleware.access import AccessMiddleware


print('Bot has been started')


async def main():
    bd.include_routers(menu.router, registration.router, reports.router, close.router)
    bd.update.outer_middleware(AccessMiddleware())
    await bot.delete_webhook(drop_pending_updates=True)
    await bd.start_polling(bot, allowed_updates=[])


if __name__ == "__main__":
    asyncio.run(main())