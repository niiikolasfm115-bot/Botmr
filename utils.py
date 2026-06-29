"""
Utility helpers and constants.
"""
from telebot import types
from db import get_all_combos

# Country codes (shortened for brevity). Add more codes as needed.
COUNTRY_CODES = {
    "1": ("USA/Canada", "🇺🇸", "US"),
    "20": ("Egypt", "🇪🇬", "EG"),
    "44": ("United Kingdom", "🇬🇧", "UK"),
    "49": ("Germany", "🇩🇪", "DE"),
    "62": ("Indonesia", "🇮🇩", "ID"),
    "98": ("Iran", "🇮🇷", "IR"),
    "213": ("Algeria", "🇩🇿", "DZ"),
}


def safe_html(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

# Force-sub helpers (very small reimplementation)
from db import get_all_force_sub_channels if False else None


def force_sub_check(user_id: int):
    # placeholder implementation: return True (integrate with Telegram API in handlers if desired)
    return True


def force_sub_markup():
    # placeholder: no channels configured
    return None
