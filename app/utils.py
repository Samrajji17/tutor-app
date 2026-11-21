import re
from datetime import datetime, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

from flask import current_app


def utcnow():
    """Naive UTC timestamp (portable between SQLite and PostgreSQL)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_local(value, fmt="%d %b %Y, %I:%M %p"):
    if not value:
        return ""
    tz = ZoneInfo(current_app.config["TIMEZONE"])
    return value.replace(tzinfo=timezone.utc).astimezone(tz).strftime(fmt)


def clean_phone(value):
    """Reduce an Indian mobile number to its 10 digits where possible."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    return digits


def whatsapp_url(number, message):
    return f"https://wa.me/{number}?text={quote(message)}"
