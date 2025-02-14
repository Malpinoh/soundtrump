import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))  # Railway will assign a port

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Webhook request handler
async def handle_webhook(request):
    try:
        body = await request.json()
        logging.info(f"🔹 Webhook received: {body}")
        
        update = Update.model_validate(body)
        await dp.feed_update(bot, update)
        
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"❌ Webhook error: {e}")
        return web.Response(status=500)

# Webhook setup functions
async def on_startup(_):
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook set: {WEBHOOK_URL}")
    else:
        logging.error("❌ WEBHOOK_URL is missing!")

async def on_shutdown(_):
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("🔴 Bot shutdown complete.")

# Create web server for webhook
app = web.Application()
app.router.add_post("/", handle_webhook)

# Run the bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=PORT)
