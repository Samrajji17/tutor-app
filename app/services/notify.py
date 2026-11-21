"""Email notifications. Failures are logged and never break a submission."""
import logging
import smtplib
import threading
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)
_KEYS = ("MAIL_SERVER", "MAIL_PORT", "MAIL_USERNAME", "MAIL_PASSWORD",
         "MAIL_USE_TLS", "MAIL_USE_SSL", "MAIL_SENDER", "NOTIFY_EMAIL")


def _deliver(cfg, subject, body, reply_to):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = cfg["MAIL_SENDER"] or cfg["MAIL_USERNAME"] or cfg["NOTIFY_EMAIL"]
        msg["To"] = cfg["NOTIFY_EMAIL"]
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)

        smtp_class = smtplib.SMTP_SSL if cfg["MAIL_USE_SSL"] else smtplib.SMTP
        with smtp_class(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=10) as server:
            if cfg["MAIL_USE_TLS"] and not cfg["MAIL_USE_SSL"]:
                server.starttls()
            if cfg["MAIL_USERNAME"]:
                server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception:  # noqa: BLE001 - email must never break the request
        log.exception("Could not send notification email")
        return False


def send(subject, body, reply_to=None):
    """Send an email if SMTP is configured. Returns True only if sent (sync mode)."""
    cfg = {key: current_app.config[key] for key in _KEYS}
    if not cfg["MAIL_SERVER"] or not cfg["NOTIFY_EMAIL"]:
        log.info("SMTP not configured; skipping email: %s", subject)
        return False
    if current_app.config["MAIL_ASYNC"]:
        threading.Thread(target=_deliver, args=(cfg, subject, body, reply_to), daemon=True).start()
        return True
    return _deliver(cfg, subject, body, reply_to)


def new_application(a):
    body = (
        f"New admission application: {a.reference}\n\n"
        f"Student: {a.student_name} (Class {a.student_class}, {a.school_name})\n"
        f"Subjects: {a.subjects}\n"
        f"Parent/guardian: {a.parent_name} ({a.relationship})\n"
        f"Mobile: {a.mobile}\nAlternate: {a.alt_mobile or '-'}\nEmail: {a.email or '-'}\n"
        f"Mode: {a.mode}\nDays: {a.preferred_days or '-'}\nTime: {a.preferred_time or '-'}\n"
        f"Notes: {a.notes or '-'}\n\nOpen the admin dashboard to update the status."
    )
    return send(f"New admission application {a.reference}", body, reply_to=a.email)


def new_message(m):
    body = f"From: {m.name}\nPhone: {m.phone}\nEmail: {m.email or '-'}\n\n{m.message}"
    return send(f"New website message from {m.name}", body, reply_to=m.email)
