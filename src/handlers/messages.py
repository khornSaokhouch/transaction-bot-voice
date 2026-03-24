import re
from telegram import Update
from telegram.ext import ContextTypes
from src.config.constants import HELP_TEXT
from src.handlers.commands import get_main_menu_keyboard

# Simple in-memory state dictionary
user_states = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, bakong_service):
    user_text = update.message.text.strip()
    user_id = update.effective_user.id
    
    state_obj = user_states.get(user_id, {})
    step = state_obj.get("step")

    # Handle Bakong Pay Button
    if "💰 បង់ប្រាក់" in user_text:
        user_states[user_id] = {"step": "WAITING_FOR_NAME"}
        await update.message.reply_text(
            "📝 សូមបញ្ចូលឈ្មោះរបស់អ្នក (ឧ: Sok San):\n"
            "Please enter your name (e.g., Sok San):",
            reply_markup=get_main_menu_keyboard()
        )
        return
        
    if step == "WAITING_FOR_NAME":
        user_states[user_id] = {"step": "WAITING_FOR_AMOUNT", "name": user_text}
        await update.message.reply_text(
            f"សួស្តី *{user_text}*! 👋\n\n"
            "📝 សូមបញ្ចូលចំនួនទឹកប្រាក់ (ឧ: 1.50us ឬ 10000kh):\n"
            "Please enter the amount you want to pay:",
            parse_mode="Markdown"
        )
        return

    if step == "WAITING_FOR_AMOUNT":
        try:
            match = re.match(r'^([\d\.]+)\s*(kh|khr|us|usd|\$|៛)?$', user_text, re.IGNORECASE)
            if not match:
                raise ValueError("Format Error")
                
            amount_str, curr_str = match.groups()
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
                
            currency = "USD"
            if curr_str:
                curr_str = curr_str.lower()
                if curr_str in ['kh', 'khr', '៛']:
                    currency = "KHR"
            
            customer_name = state_obj.get("name", "Customer")
            
            # --- TESTING MODE ---
            # Instantly simulate a successful payment to test the voice alert
            import uuid
            tx_hash = f"TEST-{str(uuid.uuid4())[:8].upper()}"
            curr_symbol = "៛" if currency == "KHR" else "$"
            
            alert_msg = (
                f"🔔 *ការទូទាត់ទទួលបានជោគជ័យ! (TEST Payment Received)*\n\n"
                f"💵 ចំនួន: *{curr_symbol}{amount:,.2f}*\n"
                f"🆔 Transaction (TxID): `{tx_hash}` \n"
                f"✅ ផ្ញើពី (From): `{customer_name}`\n\n"
                f"សូមអរគុណ! 🙏"
            )
            await update.message.reply_text(alert_msg, parse_mode="Markdown")

            try:
                voice_fp = await bakong_service.generate_voice_alert(amount, currency, sender_name=customer_name)
                if voice_fp:
                    await context.bot.send_audio(chat_id=update.effective_chat.id, audio=voice_fp, title="Payment Alert", performer="Bakong")
            except Exception as e:
                import logging
                logging.error(f"Voice generation failed: {e}")
            
            user_states.pop(user_id, None)
            return
            
        except ValueError:
            await update.message.reply_text(
                "❌ សូមបញ្ចូលចំនួនលេខត្រឹមត្រូវ (ឧ: 5.50us ឬ 10000kh)។\n"
                "❌ Please enter a valid amount format."
            )
            return
    
    if "ℹ️ អំពី" in user_text:
        return await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")

    # If user types something else, remind them what this bot does
    await update.message.reply_text(
        "👋 សួស្តី! ខ្ញុំជាបូតសម្រាប់ទូទាត់ប្រាក់តែប៉ុណ្ណោះ។\n"
        "Hello! I am a payment-only bot. Please use the menu below.",
        reply_markup=get_main_menu_keyboard()
    )

async def poll_transaction(context: ContextTypes.DEFAULT_TYPE):
    """Repeatedly checks if a transaction is successful via Bakong API."""
    job = context.job
    data = job.data
    chat_id = data['chat_id']
    amount = data['amount']
    curr_symbol = data.get('curr_symbol', '$')
    customer_name = data.get('customer_name')
    md5_hash = data['md5']
    bakong_service = data['bakong_service']
    
    data['retries'] -= 1
    if data['retries'] <= 0:
        job.schedule_removal()
        await context.bot.send_message(
            chat_id=chat_id, 
            text="⏳ ការទូទាត់ផុតកំណត់។ សូមព្យាយាមម្តងទៀត! (Payment timed out.)", 
            parse_mode="Markdown"
        )
        return
        
    result = await bakong_service.check_transaction(md5_hash)
    
    if result and result.get("responseCode") == 0 and result.get("data"):
        tx_data = result["data"]
        tx_hash = tx_data.get("hash", "Unknown")
        tx_sender = tx_data.get('fromAccountId', customer_name)
        
        job.schedule_removal()
        
        alert_msg = (
            f"🔔 *ការទូទាត់ទទួលបានជោគជ័យ! (Payment Received)*\n\n"
            f"💵 ចំនួន: *{curr_symbol}{amount:,.2f}*\n"
            f"🆔 Transaction (TxID): `{tx_hash}` \n"
            f"✅ ផ្ញើពី (From): `{tx_sender}`\n\n"
            f"សូមអរគុណ! 🙏"
        )
        await context.bot.send_message(chat_id=chat_id, text=alert_msg, parse_mode="Markdown")

        try:
            voice_fp = await bakong_service.generate_voice_alert(amount, data['currency'], sender_name=tx_sender)
            if voice_fp:
                await context.bot.send_audio(chat_id=chat_id, audio=voice_fp, title="Payment Alert", performer="Bakong")
        except Exception as e:
            import logging
            logging.error(f"Voice generation failed: {e}")

