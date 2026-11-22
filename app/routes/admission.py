import time
from datetime import timedelta

from flask import (Blueprint, current_app, flash, redirect, render_template, request,
                   session, url_for)
from sqlalchemy import func

from ..extensions import db
from ..forms.admission import AdmissionForm
from ..models import Application
from ..services import notify, ratelimit
from ..services.references import generate_reference
from ..utils import clean_phone, utcnow

bp = Blueprint("admission", __name__, url_prefix="/admission")


@bp.route("/", methods=["GET", "POST"])
def apply():
    form = AdmissionForm()
    if request.method == "GET":
        session["form_started"] = time.time()
        return render_template("site/admission.html", form=form)

    if not form.validate_on_submit():
        flash("Please fix the highlighted fields and submit again.", "error")
        return render_template("site/admission.html", form=form)

    if form.website.data:  # honeypot filled: pretend success, store nothing
        return redirect(url_for("public.home"))

    limit, window = current_app.config["FORM_RATE_LIMIT"]
    started = session.get("form_started")
    if not ratelimit.allow(f"form:{request.remote_addr}", limit, window):
        flash("Too many submissions from this device. Please try again later.", "error")
        return render_template("site/admission.html", form=form), 429
    if started is None or time.time() - started < current_app.config["MIN_FORM_SECONDS"]:
        flash("That was very quick. Please review the form and submit again.", "error")
        return render_template("site/admission.html", form=form)

    mobile = clean_phone(form.mobile.data)
    # Prevent duplicates from double taps or refreshes: same student + number within 24 hours.
    existing = Application.query.filter(
        func.lower(Application.student_name) == form.student_name.data.lower(),
        Application.mobile == mobile,
        Application.created_at >= utcnow() - timedelta(hours=24),
    ).first()
    if existing:
        session["last_reference"] = existing.reference
        return redirect(url_for(".success"))

    application = Application(
        reference=generate_reference(),
        student_name=form.student_name.data,
        date_of_birth=form.date_of_birth.data,
        gender=form.gender.data or None,
        school_name=form.school_name.data,
        student_class=form.student_class.data,
        subjects=", ".join(form.subjects.data),
        parent_name=form.parent_name.data,
        relationship=form.relationship.data,
        mobile=mobile,
        alt_mobile=clean_phone(form.alt_mobile.data) or None,
        email=form.email.data or None,
        mode=form.mode.data,
        preferred_days=", ".join(form.preferred_days.data) or None,
        preferred_time=form.preferred_time.data or None,
        notes=form.notes.data or None,
    )
    db.session.add(application)
    db.session.commit()
    notify.new_application(application)  # never raises; submission already saved

    session["last_reference"] = application.reference
    return redirect(url_for(".success"))


@bp.get("/success")
def success():
    reference = session.get("last_reference")
    if not reference:
        return redirect(url_for(".apply"))
    return render_template("site/admission_success.html", reference=reference)
