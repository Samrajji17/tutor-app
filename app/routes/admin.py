import csv
import io
from datetime import datetime, timedelta
from functools import wraps

from flask import (Blueprint, Response, current_app, flash, redirect, render_template,
                   request, session, stream_with_context, url_for)
from sqlalchemy import case, func, select

from ..extensions import db
from ..forms.admission import CLASS_CHOICES
from ..forms.auth import LoginForm
from ..models import STATUSES, Admin, Application, ContactMessage
from ..services import ratelimit
from ..utils import to_local, utcnow

bp = Blueprint("admin", __name__, url_prefix="/admin")

CSV_COLUMNS = ["Reference", "Received", "Status", "Student", "Date of birth", "Gender", "School",
               "Class", "Subjects", "Parent/guardian", "Relationship", "Mobile", "Alternate",
               "Email", "Mode", "Days", "Time", "Notes"]


def current_admin():
    """The signed-in admin for this request (cached per request, not per app context)."""
    if "tuition.admin" not in request.environ:
        admin_id = session.get("admin_id")
        request.environ["tuition.admin"] = db.session.get(Admin, admin_id) if admin_id else None
    return request.environ["tuition.admin"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_admin() is None:
            session.pop("admin_id", None)
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_admin():
        return redirect(url_for(".dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        if not ratelimit.allow(f"login:{request.remote_addr}", 15, 900):
            flash("Too many sign-in attempts. Please wait 15 minutes.", "error")
            return render_template("admin/login.html", form=form), 429
        admin = Admin.query.filter_by(username=form.username.data.strip().lower()).first()
        if admin and not admin.is_locked and admin.check_password(form.password.data):
            admin.failed_attempts, admin.locked_until, admin.last_login = 0, None, utcnow()
            db.session.commit()
            session.clear()  # new session on login prevents fixation
            session["admin_id"] = admin.id
            session.permanent = True
            return redirect(url_for(".dashboard"))
        if admin and not admin.is_locked:
            admin.failed_attempts += 1
            if admin.failed_attempts >= current_app.config["MAX_LOGIN_ATTEMPTS"]:
                admin.locked_until = utcnow() + timedelta(minutes=current_app.config["LOCKOUT_MINUTES"])
                admin.failed_attempts = 0
            db.session.commit()
        # One message for every failure so usernames cannot be guessed.
        flash("Sign-in failed. Check your details, or wait a few minutes if you tried several times.", "error")
    return render_template("admin/login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for(".login"))


@bp.get("/")
@login_required
def dashboard():
    month_start = utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total, new, month = db.session.execute(select(
        func.count(Application.id),
        func.sum(case((Application.status == "new", 1), else_=0)),
        func.sum(case((Application.created_at >= month_start, 1), else_=0)),
    )).one()
    recent = Application.query.order_by(Application.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", total=total or 0, new=new or 0,
                           month=month or 0, recent=recent)


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def _filters():
    return {
        "q": request.args.get("q", "").strip()[:100],
        "cls": request.args.get("cls", ""),
        "status": request.args.get("status", ""),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
    }


def _filtered_query(f):
    query = Application.query
    if f["q"]:
        escaped = f["q"].replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Application.student_name.ilike(f"%{escaped}%", escape="\\"))
    if f["cls"] in {value for value, _ in CLASS_CHOICES if value}:
        query = query.filter(Application.student_class == f["cls"])
    if f["status"] in STATUSES:
        query = query.filter(Application.status == f["status"])
    start, end = _parse_date(f["date_from"]), _parse_date(f["date_to"])
    if start:
        query = query.filter(Application.created_at >= start)
    if end:
        query = query.filter(Application.created_at < end + timedelta(days=1))
    return query.order_by(Application.created_at.desc())


@bp.get("/applications")
@login_required
def applications():
    f = _filters()
    page = request.args.get("page", 1, type=int)
    pagination = _filtered_query(f).paginate(
        page=page, per_page=current_app.config["ADMIN_PER_PAGE"], error_out=False)
    query_args = {k: v for k, v in f.items() if v}
    return render_template("admin/applications.html", pagination=pagination, filters=f,
                           query_args=query_args, statuses=STATUSES, class_choices=CLASS_CHOICES[1:])


@bp.get("/applications/<int:app_id>")
@login_required
def detail(app_id):
    application = db.get_or_404(Application, app_id)
    return render_template("admin/detail.html", a=application, statuses=STATUSES)


@bp.post("/applications/<int:app_id>/status")
@login_required
def update_status(app_id):
    application = db.get_or_404(Application, app_id)
    status = request.form.get("status", "")
    if status in STATUSES:
        application.status = status
        db.session.commit()
        flash(f"Status changed to {status}.", "success")
    else:
        flash("Choose a valid status.", "error")
    return redirect(url_for(".detail", app_id=app_id))


def _csv_safe(value):
    """Stop spreadsheet formula injection from submitted text."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


@bp.get("/applications/export.csv")
@login_required
def export_csv():
    query = _filtered_query(_filters())

    def generate():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(CSV_COLUMNS)
        yield "\ufeff" + buffer.getvalue()  # BOM so Excel reads UTF-8 correctly
        for a in query.yield_per(200):
            buffer.seek(0)
            buffer.truncate(0)
            writer.writerow([_csv_safe(v) for v in (
                a.reference, to_local(a.created_at), a.status, a.student_name,
                a.date_of_birth, a.gender, a.school_name, a.student_class, a.subjects,
                a.parent_name, a.relationship, a.mobile, a.alt_mobile, a.email, a.mode,
                a.preferred_days, a.preferred_time, a.notes)])
            yield buffer.getvalue()

    filename = f"applications-{utcnow():%Y-%m-%d}.csv"
    return Response(stream_with_context(generate()), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@bp.get("/messages")
@login_required
def messages():
    page = request.args.get("page", 1, type=int)
    pagination = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=current_app.config["ADMIN_PER_PAGE"], error_out=False)
    return render_template("admin/messages.html", pagination=pagination)
