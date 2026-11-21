import smtplib
from unittest.mock import patch

from app.extensions import db
from app.models import Application


# --- Public pages -------------------------------------------------------------
def test_public_pages_load(client):
    for path in ["/", "/about", "/teaching", "/admission/", "/contact", "/robots.txt", "/sitemap.xml"]:
        assert client.get(path).status_code == 200, path
    assert client.get("/nope").status_code == 404


def test_whatsapp_links_present(client):
    html = client.get("/").get_data(as_text=True)
    assert html.count("https://wa.me/") >= 3  # hero, footer, floating button
    assert "Hello%2C%20I%20would%20like%20to%20know%20more" in html


def test_seo_basics(client):
    html = client.get("/about").get_data(as_text=True)
    assert "<title>About" in html and 'name="description"' in html and 'property="og:title"' in html
    assert "Disallow: /admin/" in client.get("/robots.txt").get_data(as_text=True)


# --- Admission ----------------------------------------------------------------
def test_admission_success_and_storage(client, app, form_data):
    client.get("/admission/")
    resp = client.post("/admission/", data=form_data, follow_redirects=True)
    assert resp.status_code == 200 and b"Application received" in resp.data
    a = Application.query.one()
    assert a.reference.startswith("TUT-") and a.reference.encode() in resp.data
    assert a.mobile == "9876543210" and a.status == "new" and a.subjects == "Mathematics"


def test_validation_errors(client, form_data):
    client.get("/admission/")
    form_data.update(mobile="123", student_class="")
    resp = client.post("/admission/", data=form_data)
    assert b"valid 10-digit mobile" in resp.data and b"Select the student" in resp.data
    assert Application.query.count() == 0


def test_duplicate_submission_blocked(client, form_data):
    client.get("/admission/")
    client.post("/admission/", data=form_data)
    client.post("/admission/", data=form_data)
    assert Application.query.count() == 1


def test_references_unique(client, form_data):
    for i in range(3):
        client.get("/admission/")
        form_data["student_name"] = f"Student {i}"
        client.post("/admission/", data=form_data)
    refs = [a.reference for a in Application.query.all()]
    assert len(refs) == len(set(refs)) == 3


def test_honeypot_stores_nothing(client, form_data):
    client.get("/admission/")
    form_data["website"] = "http://spam.example"
    client.post("/admission/", data=form_data)
    assert Application.query.count() == 0


def test_email_failure_does_not_break_submission(client, app, form_data):
    app.config.update(MAIL_SERVER="smtp.invalid", NOTIFY_EMAIL="t@example.com")
    with patch("smtplib.SMTP", side_effect=smtplib.SMTPException("boom")):
        client.get("/admission/")
        resp = client.post("/admission/", data=form_data, follow_redirects=True)
    assert b"Application received" in resp.data and Application.query.count() == 1


def test_contact_form(client):
    client.get("/contact")
    resp = client.post("/contact", data={"name": "Priya", "phone": "9876543210", "message": "Need batch timings"},
                       follow_redirects=True)
    assert b"message has been sent" in resp.data


# --- Admin --------------------------------------------------------------------
def test_admin_routes_require_login(client):
    for path in ["/admin/", "/admin/applications", "/admin/applications/export.csv", "/admin/messages"]:
        r = client.get(path)
        assert r.status_code == 302 and "/admin/login" in r.headers["Location"], path
    assert client.post("/admin/applications/1/status", data={"status": "enrolled"}).status_code == 302


def test_login_and_invalid_login(client, login):
    assert b"Sign-in failed" in login(password="wrong-password-here").data
    assert login().status_code == 302
    assert client.get("/admin/").status_code == 200


def test_lockout_after_repeated_failures(client, login):
    for _ in range(5):
        login(password="bad")
    assert b"Sign-in failed" in login().data  # correct password refused while locked


def _seed(client, form_data, n=3):
    for i in range(n):
        client.get("/admission/")
        form_data.update(student_name=f"Pupil {i}", student_class=str(6 + i))
        client.post("/admission/", data=form_data)


def test_search_filter_status_and_csv(client, login, form_data):
    _seed(client, form_data)
    login()
    assert b"Pupil 1" in client.get("/admin/applications?q=pupil 1").data
    assert b"Pupil 0" not in client.get("/admin/applications?q=pupil 1").data
    assert b"Pupil 2" in client.get("/admin/applications?cls=8").data
    assert b"No applications match" in client.get("/admin/applications?status=enrolled").data
    assert b"No applications match" in client.get("/admin/applications?date_from=2099-01-01").data

    a = Application.query.filter_by(student_name="Pupil 0").one()
    client.post(f"/admin/applications/{a.id}/status", data={"status": "enrolled"})
    db.session.refresh(a)
    assert a.status == "enrolled"
    assert b"Pupil 0" in client.get("/admin/applications?status=enrolled").data

    csv_resp = client.get("/admin/applications/export.csv")
    assert csv_resp.mimetype == "text/csv" and b"Pupil 2" in csv_resp.data and b"Reference" in csv_resp.data


def test_csv_formula_injection_neutralised(client, login, form_data):
    client.get("/admission/")
    form_data["student_name"] = "=HYPERLINK(1)"
    client.post("/admission/", data=form_data)
    login()
    assert b"'=HYPERLINK" in client.get("/admin/applications/export.csv").data


def test_dashboard_stats_and_logout(client, login, form_data):
    _seed(client, form_data, 2)
    login()
    html = client.get("/admin/").get_data(as_text=True)
    assert "Total applications" in html and "Recent submissions" in html
    client.post("/admin/logout")
    assert client.get("/admin/").status_code == 302


def test_pagination(client, login, app, form_data):
    app.config["ADMIN_PER_PAGE"] = 2
    _seed(client, form_data, 3)
    login()
    assert b"page 1 of 2" in client.get("/admin/applications").data
