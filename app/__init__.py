import logging

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config

from .content import load_site
from .extensions import csrf, db, migrate
from .utils import to_local, utcnow, whatsapp_url

WA_DEFAULT_MESSAGE = "Hello, I would like to know more about your tuition classes and admission process."
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
       "form-action 'self'; frame-ancestors 'none'; base-uri 'self'")


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if not app.config.get("SECRET_KEY_FROM_ENV") and not app.config.get("TESTING"):
        logging.getLogger(__name__).warning(
            "SECRET_KEY is not set. A temporary key is used, so sessions reset on restart. "
            "Set SECRET_KEY in .env.")
    if app.config.get("TRUST_PROXY"):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from . import models  # noqa: F401  (register tables)
    from .routes import admin, admission, public

    app.register_blueprint(public.bp)
    app.register_blueprint(admission.bp)
    app.register_blueprint(admin.bp)

    _register_helpers(app)
    _register_security(app)
    _register_errors(app)

    from .cli import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()
    return app


def _register_helpers(app):
    from flask import request

    site = load_site()
    from .routes.admin import current_admin

    app.jinja_env.filters["localtime"] = to_local
    app.jinja_env.globals["current_admin"] = current_admin

    @app.context_processor
    def inject():
        base = (app.config["BASE_URL"] or request.url_root).rstrip("/")
        return {
            "site": site,
            "base_url": base,
            "now_year": utcnow().year,
            "canonical_url": base + request.path,
            "wa_link": lambda message=WA_DEFAULT_MESSAGE: whatsapp_url(site["whatsapp"], message),
        }


def _register_security(app):
    from flask import request

    @app.after_request
    def set_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Content-Security-Policy", CSP)
        if app.config["SESSION_COOKIE_SECURE"]:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        if request.path.startswith("/admin"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response


def _register_errors(app):
    def show(code, title, message):
        return render_template("errors/error.html", code=code, title=title, message=message), code

    @app.errorhandler(CSRFError)
    def csrf_error(_):
        return show(400, "Please try again", "The page expired or the form could not be verified. Go back, refresh the page and submit again.")

    @app.errorhandler(404)
    def not_found(_):
        return show(404, "Page not found", "The page you are looking for does not exist or has moved.")

    @app.errorhandler(413)
    def too_large(_):
        return show(413, "Request too large", "The information sent was too large.")

    @app.errorhandler(429)
    def too_many(_):
        return show(429, "Too many requests", "Please wait a little while and try again.")

    @app.errorhandler(Exception)
    def server_error(error):
        if isinstance(error, HTTPException):
            return show(error.code, error.name, "Something went wrong with this request.")
        app.logger.exception("Unhandled error")
        db.session.rollback()
        return show(500, "Something went wrong", "An unexpected error occurred. Please try again shortly.")
