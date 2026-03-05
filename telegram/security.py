"""
telegram/security.py

Local whitelist checker for authorized Telegram user IDs.
Provides a second layer of defense after the Vercel cloud filter.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def get_authorized_ids() -> set:
    """
    Reads the AUTHORIZED_TELEGRAM_IDS from .env and returns a set of integer user IDs.
    """
    raw = os.getenv("AUTHORIZED_TELEGRAM_IDS", "")
    ids = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return ids


def is_authorized(user_id: int) -> bool:
    """
    Returns True if the given Telegram user ID is in the authorized whitelist.
    """
    authorized = get_authorized_ids()
    return user_id in authorized
