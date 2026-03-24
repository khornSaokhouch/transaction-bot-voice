import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bakong Config
BAKONG_API_TOKEN = os.getenv("BAKONG_API_TOKEN")
BAKONG_BASE_URL = os.getenv("BAKONG_BASE_URL", "https://api-bakong.nbc.gov.kh/")
BAKONG_ACCOUNT_ID = os.getenv("BAKONG_ACCOUNT_ID", "yourname@aba")
MERCHANT_NAME = os.getenv("MERCHANT_NAME", "Bakong Merchant")
MERCHANT_CITY = os.getenv("MERCHANT_CITY", "Phnom Penh")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in .env file")
