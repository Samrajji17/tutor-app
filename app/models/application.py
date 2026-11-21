from ..extensions import db
from ..utils import utcnow

STATUSES = ("new", "contacted", "enrolled", "rejected")


class Application(db.Model):
    """An admission application.

    Phase 2 note: a future ``Student`` model can reference ``applications.id``
    so enrolled applicants convert into managed students without re-entry.
    """

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(24), unique=True, nullable=False, index=True)

    student_name = db.Column(db.String(100), nullable=False, index=True)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    school_name = db.Column(db.String(150), nullable=False)
    student_class = db.Column(db.String(10), nullable=False, index=True)
    subjects = db.Column(db.String(255), nullable=False)

    parent_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    alt_mobile = db.Column(db.String(20))
    email = db.Column(db.String(120))

    mode = db.Column(db.String(10), nullable=False)
    preferred_days = db.Column(db.String(120))
    preferred_time = db.Column(db.String(30))
    notes = db.Column(db.Text)

    status = db.Column(db.String(12), nullable=False, default="new", index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)
