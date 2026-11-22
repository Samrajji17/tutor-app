# Jancy T: Mathematics Tuition Website (Phase 1)

A lightweight Flask website for a school mathematics tuition teacher: portfolio pages, online admission form, WhatsApp click-to-chat, and a private admin dashboard. Python and a browser only. No Node.js, no npm, no build step.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python run.py
```

Open http://127.0.0.1:5000. The database (`instance/tuition.db`) is created automatically on first run.
Also available: `flask --app run init-db`.

Generate a secret key and paste it into `.env` as `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Create the admin account

There is no public registration page. Create the account from the terminal:

```bash
flask --app run create-admin
```

You are prompted for a username and a password (10+ characters, hidden). Run it again to reset a forgotten password. Sign in at `/admin/login`.
Accounts lock for 15 minutes after 5 wrong passwords.

## Fill in the teacher's details

1. **`.env`**: name, phone, WhatsApp number (digits with country code, e.g. `919876543210`), email, address, Google Maps link, photo file name, social links.
2. **`app/content.py`**: tuition **timings**, biography, experience, philosophy, achievements, testimonials, FAQs. Items tagged "Sample, edit me" on the site are placeholders. Replace them, then they stop showing the tag (set `SHOW_SAMPLE_TAGS=0` to hide all tags). Only add qualifications, awards and testimonials that are real.
3. **Photo**: put the image in `app/static/images/` (JPG/WebP, about 480x600, under 100 KB) and set `TEACHER_PHOTO`. Optionally add `og-image.jpg` (1200x630) and set `OG_IMAGE` for link previews.
4. Set `BASE_URL` (for example `https://www.example.com`) so sitemap and canonical links are correct.

## Email notifications (optional)

Set `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SENDER` and `NOTIFY_EMAIL` in `.env`. For Gmail use `smtp.gmail.com`, port 587 and an app password. If SMTP is blank or fails, applications are still saved and appear in the dashboard; the error is only logged.

## Project layout

```
app/
  __init__.py        app factory, security headers, error pages
  content.py         teacher-specific content (edit this)
  models/            Admin, Application, ContactMessage
  routes/            public.py, admission.py, admin.py (blueprints)
  forms/             Flask-WTF forms and validation
  services/          email, references, rate limiting
  templates/         site/, admin/, components/, errors/
  static/            css/, js/, images/
config.py            settings from environment variables
run.py               entry point
tests/               pytest suite
migrations/          for Flask-Migrate (see below)
```

## Security notes

Password hashing (Werkzeug), CSRF on every form, hashed sessions with HttpOnly and SameSite cookies, login lockout and rate limiting, honeypot and minimum-fill-time spam checks, per-IP submission limits, CSP and other security headers, SQLAlchemy parameterised queries, CSV formula-injection protection, admin pages marked no-store and noindex, and generic error pages that never show internals.

## Deployment (Linux server, for example a small VPS)

```bash
pip install -r requirements.txt
```

In `.env` set: `SECRET_KEY`, `FLASK_DEBUG=0`, `COOKIE_SECURE=1`, `TRUST_PROXY=1`, `BASE_URL=https://yourdomain`.

Run with gunicorn behind nginx (or your host's Python app panel):

```bash
gunicorn -w 2 -b 127.0.0.1:8000 run:app
```

nginx: proxy `/` to `127.0.0.1:8000`, serve HTTPS (Let's Encrypt), and set `X-Forwarded-For`/`X-Forwarded-Proto`. On cPanel-style hosts, point the Python app at `run.py` with application object `app`.

Back up `instance/tuition.db` regularly. To move to PostgreSQL later, set `DATABASE_URL` and use Flask-Migrate (`flask --app run db init`, `db migrate`, `db upgrade`). The models use portable types.

## Tests

```bash
pip install pytest
python -m pytest
```

## Manual testing checklist

- [ ] All pages open from the menu on phone, tablet and desktop widths; mobile menu opens and closes
- [ ] Floating, hero and footer WhatsApp buttons open chat with the prefilled message
- [ ] Admission form: empty submit shows errors; bad mobile number rejected; valid form shows a reference number
- [ ] Double-clicking Submit creates only one application
- [ ] Application appears in `/admin/applications`; email arrives if SMTP is set; submission works with SMTP off
- [ ] Wrong admin password is refused; 5 wrong attempts lock the account
- [ ] `/admin/` while signed out redirects to the login page
- [ ] Search by name, filter by class, status and dates, pagination
- [ ] Changing status saves; CSV export opens in Excel with the filtered rows
- [ ] `/robots.txt` and `/sitemap.xml` load

## Phase 2 (not built)

Student, fee, attendance and parent-communication modules can be added as new blueprints and models. `Application` is designed to link to a future `Student` record.
