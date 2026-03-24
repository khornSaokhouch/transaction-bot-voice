from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from src.config.constants import WELCOME_TEXT_KHMER, WELCOME_TEXT_ENGLISH, HELP_TEXT
from src.config.state import add_subscribed_user

def get_main_menu_keyboard():
    # Simple explicit keyboard layout for better compatibility
    keyboard = [
        [KeyboardButton("💰 បង់ប្រាក់ (Pay)")],
        [KeyboardButton("ℹ️ អំពី (About)")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a friendly welcome message when the command /start is issued."""
    chat_id = update.effective_chat.id
    add_subscribed_user(chat_id)
    
    user_name = update.effective_user.first_name or "បង/ប្អូន"
    welcome_msg = f"👋 សួស្តី {user_name}!\n\n{WELCOME_TEXT_KHMER}\n\n---\n\n{WELCOME_TEXT_ENGLISH}\n\n_Tap the button below to pay_ 👇"
    
    await update.message.reply_text(
        welcome_msg, 
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")
