import qrcode
from io import BytesIO
import hashlib
import httpx
from bakong_khqr import KHQR
from src.config.config import BAKONG_ACCOUNT_ID, MERCHANT_NAME, MERCHANT_CITY, BAKONG_BASE_URL, BAKONG_API_TOKEN

class BakongService:
    @staticmethod
    def generate_qr_string(amount: float, currency: str = "USD"):
        """Generates a KHQR string for the given amount using bakong-khqr library."""
        try:
            import uuid
            bill_num = f"INV-{str(uuid.uuid4())[:8].upper()}"
            khqr = KHQR()
            return khqr.create_qr(
                bank_account=BAKONG_ACCOUNT_ID,
                merchant_name=MERCHANT_NAME,
                merchant_city=MERCHANT_CITY,
                amount=amount,
                currency=currency,
                phone_number="",
                store_label="CamboBot",
                bill_number=bill_num,
                terminal_label="Bot-01"
            )
        except Exception as e:
            print(f"Error generating KHQR string: {e}")
            return None

    @staticmethod
    def generate_md5(qr_string: str) -> str:
        """Generate MD5 hash for the KHQR string."""
        if not qr_string:
            return ""
        return hashlib.md5(qr_string.encode('utf-8')).hexdigest()

    @staticmethod
    async def generate_deeplink(qr_string: str) -> str:
        """Generates a short deeplink using Bakong API."""
        url = f"{BAKONG_BASE_URL.rstrip('/')}/v1/generate_deeplink_by_qr"
        payload = {
            "qr": qr_string,
            "sourceInfo": {
                "appIconUrl": "https://bakong.nbc.gov.kh/images/logo.svg",
                "appName": MERCHANT_NAME,
                "appDeepLinkCallback": "https://bakong.nbc.gov.kh/"
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                data = response.json()
                if data.get("responseCode") == 0 and "data" in data:
                    return data["data"].get("shortLink", "")
            except Exception as e:
                print(f"Deeplink API Error: {e}")
        return ""

    @staticmethod
    async def check_transaction(md5_hash: str):
        """Checks transaction status by MD5 via Bakong API."""
        url = f"{BAKONG_BASE_URL.rstrip('/')}/v1/check_transaction_by_md5"
        payload = {"md5": md5_hash}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {BAKONG_API_TOKEN}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
                return response.json()
            except Exception as e:
                print(f"Check Tx API Error: {e}")
                return None

    @staticmethod
    async def generate_qr_image(qr_string: str):
        """Generates a QR code image using bakongrelay API with a local fallback."""
        if not qr_string:
            return None
            
        import base64
        # Primary API
        try:
            async with httpx.AsyncClient() as client:
                url = "https://api.bakongrelay.com/v1/generate_khqr_image"
                res = await client.post(url, json={"qr": qr_string}, timeout=8.0)
                data = res.json()
                if data.get("responseCode") == 0 and "data" in data:
                    b64_str = data["data"].get("qrImage", "")
                    if b64_str:
                        bio = BytesIO(base64.b64decode(b64_str))
                        bio.name = "qrcode.png"
                        return bio
        except Exception as e:
            print(f"QR Image API Error: {e}, using local fallback.")
            
        # Fallback to local generation
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        bio = BytesIO()
        bio.name = "qrcode.png"
        img.save(bio, format="PNG")
        bio.seek(0)
        return bio

    @staticmethod
    async def generate_voice_alert(amount: float, currency: str, sender_name: str = None, voice: str = "km-KH-SreymomNeural"):
        """Generates a text-to-speech audio alert in Khmer using Microsoft Edge TTS.
        
        Available Khmer voices:
        - 'km-KH-SreymomNeural'  -> Female voice (default)
        - 'km-KH-PisethNeural'   -> Male voice
        """
        import edge_tts
        from io import BytesIO

        s_name = sender_name if sender_name else "អតិថិជន"
        
        if currency in ["USD", "us", "$", "USD"]:
            text = f"បានទទួលប្រាក់ពី {s_name} ចំនួន {amount:.2f} ដុល្លារ សូមអរគុណ!"
        else:
            text = f"បានទទួលប្រាក់ពី {s_name} ចំនួន {amount:.2f} រៀល សូមអរគុណ!"

        communicate = edge_tts.Communicate(text, voice)
        fp = BytesIO()
        fp.name = "voice_alert.mp3"
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                fp.write(chunk["data"])
        fp.seek(0)
        return fp
        
    @staticmethod
    def verify_payment(transaction_id: str):
        """Simulated payment verification."""
        # In a real app, this would call the Bakong Open API /check-transaction-status
        return True
