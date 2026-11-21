import time

from flask import (Blueprint, Response, current_app, flash, redirect, render_template,
                   request, session, url_for)

from ..extensions import db
from ..forms.admission import ContactForm
from ..models import ContactMessage
from ..services import notify, ratelimit

bp = Blueprint("public", __name__)


@bp.get("/")
def home():
    return render_template("public/home.html")


@bp.get("/about")
def about():
    return render_template("public/about.html")


@bp.get("/teaching")
def teaching():
    return render_template("public/teaching.html")


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if request.method == "GET":
        session["form_started"] = time.time()
    elif form.validate_on_submit():
        limit, window = current_app.config["FORM_RATE_LIMIT"]
        started = session.get("form_started")
        too_fast = started is None or time.time() - started < current_app.config["MIN_FORM_SECONDS"]
        if form.website.data:  # honeypot filled: pretend success
            return redirect(url_for(".contact"))
        if not ratelimit.allow(f"form:{request.remote_addr}", limit, window):
            flash("Too many submissions from this device. Please try again later.", "error")
        elif too_fast:
            flash("That was very quick. Please check your message and send it again.", "error")
        else:
            message = ContactMessage(name=form.name.data, phone=form.phone.data,
                                     email=form.email.data or None, message=form.message.data)
            db.session.add(message)
            db.session.commit()
            notify.new_message(message)
            flash("Thank you. Your message has been sent and the teacher will get back to you.", "success")
            return redirect(url_for(".contact") + "#contact-form")
    return render_template("public/contact.html", form=form)


@bp.get("/robots.txt")
def robots():
    base = (current_app.config["BASE_URL"] or request.url_root).rstrip("/")
    body = f"User-agent: *\nDisallow: /admin/\nAllow: /\n\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.get("/sitemap.xml")
def sitemap():
    base = (current_app.config["BASE_URL"] or request.url_root).rstrip("/")
    paths = [url_for(endpoint) for endpoint in
             ("public.home", "public.about", "public.teaching", "admission.apply", "public.contact")]
    urls = "".join(f"<url><loc>{base}{p}</loc></url>" for p in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")
