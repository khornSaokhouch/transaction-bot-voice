import asyncio
import uvicorn
from fastapi import FastAPI, Request
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.config.config import TELEGRAM_TOKEN
from src.utils.logger import setup_logging
from src.services.bakong_service import BakongService
from src.handlers.commands import start_command, help_command
from src.handlers.messages import handle_message
from src.config.state import load_subscribed_users

app = FastAPI()
ptb_app = None

@app.post("/webhook/bakong")
async def bakong_webhook(request: Request):
    """Receives JSON payloads from Bakong or Payment Gateway"""
    data = await request.json()
    
    amount = data.get("amount", "0.00")
    currency = data.get("currency", "USD")
    sender = data.get("fromAccountId") or data.get("sender_name") or "Unknown Sender"
    tx_hash = data.get("hash") or data.get("transaction_id") or "N/A"
    
    curr_symbol = "៛" if currency in ["KHR", "kh"] else "$"
    
    alert_msg = (
        f"🔔 *ការទូទាត់ទទួលបានជោគជ័យ! (Payment Received by Webhook)*\n\n"
        f"💵 ចំនួន: *{curr_symbol}{float(amount):,.2f}*\n"
        f"🆔 TxID: `{tx_hash}` \n"
        f"✅ ផ្ញើពី (From): `{sender}`\n\n"
        f"សូមអរគុណ! 🙏"
    )
    
    try:
        voice_fp = await BakongService.generate_voice_alert(float(amount), currency)
    except Exception as e:
        print(f"Webhook voice error: {e}")
        voice_fp = None
    
    # Broadcast to all subscribed users
    if ptb_app:
        users = load_subscribed_users()
        for chat_id in users:
            try:
                await ptb_app.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="Markdown")
                if voice_fp:
                    voice_fp.seek(0)
                    await ptb_app.bot.send_audio(chat_id=chat_id, audio=voice_fp, title="Payment Alert", performer="Bakong")
            except Exception as e:
                print(f"Failed to send alert to {chat_id}: {e}")
                
    return {"status": "success"}


async def main():
    logger = setup_logging()
    bakong_service = BakongService()
    
    global ptb_app
    ptb_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    ptb_app.add_handler(CommandHandler("start", start_command))
    ptb_app.add_handler(CommandHandler("help", help_command))
    ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: handle_message(u, c, bakong_service)))
    
    # Initialize and start the Telegram Bot in the same async loop
    await ptb_app.initialize()
    await ptb_app.start()
    await ptb_app.updater.start_polling()
    
    logger.info("💰 Telegram Bot is running...")
    logger.info("🌐 Webhook Listener started on port 8000 (endpoints: /webhook/bakong)")
    
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    
    # Block forever running the server alongside the bot
    await server.serve()
    
    # Graceful shutdown once the server stops
    logger.info("Shutting down bot...")
    await ptb_app.updater.stop()
    await ptb_app.stop()
    await ptb_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
