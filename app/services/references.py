import secrets

from flask import current_app

from ..models import Application
from ..utils import utcnow

# No 0/O/1/I so references are easy to read out over the phone.
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_reference():
    prefix = current_app.config["REFERENCE_PREFIX"]
    year = utcnow().year
    while True:
        code = "".join(secrets.choice(_ALPHABET) for _ in range(6))
        reference = f"{prefix}-{year}-{code}"
        if not Application.query.filter_by(reference=reference).first():
            return reference
