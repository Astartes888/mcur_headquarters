import asyncio

from bot_init import bd, bot
from handlers import user_handlers


print('Bot has been started')

async def main():
	bd.include_routers(user_handlers.router)
	await bot.delete_webhook(drop_pending_updates=True)
	await bd.start_polling(bot, allowed_updates=[])


if __name__ == "__main__":
	asyncio.run(main())