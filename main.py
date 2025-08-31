# main.py
from flask import Flask, render_template, render_template_string, url_for
from jinja2 import TemplateNotFound
import os
import json
import pathlib
import csv

# Optional: MySQL participants view
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder="templates", static_folder="static")

# ───────────────────────── Site-wide config ─────────────────────────
SITE_TITLE = "AI for Impact"
SITE_EMAIL = "connect@aiforimpact.net"
SITE_LOGO = "input/logo_improved.png"   # put the file at static/input/logo_improved.png
SITE_FOOTER_HTML = """
<div style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #7F8C8D;">
    aiforimpact © 2024<br>
    Powered by Climate Resilience Fundraising Platform B.V.
</div>
"""

# Navbar items (name, endpoint, template name)
NAV_ITEMS = [
    ("Home",         "home",         "home.html"),
    ("Trainings",    "trainings",    "trainings.html"),
    ("Pricing",      "pricing",      "prices.html"),
    ("Gallery",      "gallery",      "gallery.html"),
    ("Certificate",  "certificate",  "certificate.html"),
    ("Participants", "participants", "participants.html"),
    ("About",        "about",        "about.html"),
    ("Contact",      "contact",      "contact.html"),
]

# Make nav + globals available in all templates
@app.context_processor
def inject_globals():
    return {
        "SITE_TITLE": SITE_TITLE,
        "SITE_EMAIL": SITE_EMAIL,
        "SITE_LOGO_URL": url_for("static", filename=SITE_LOGO),
        "NAV_ITEMS": NAV_ITEMS,
        "SITE_FOOTER_HTML": SITE_FOOTER_HTML,
    }

# Helper: render a page, falling back to a minimal placeholder if template missing
def render_page(template_name: str, page_title: str, **ctx):
    try:
        return render_template(template_name, page_title=page_title, **ctx)
    except TemplateNotFound:
        placeholder = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{{{{ page_title }}}} — {{{{ SITE_TITLE }}}}</title>
            <link rel="icon" href="{{{{ SITE_LOGO_URL }}}}">
            <link rel="stylesheet" href="{{{{ url_for('static', filename='style.css') }}}}">
        </head>
        <body>
            <div class="layout">
                <aside class="sidebar">
                    <img src="{{{{ SITE_LOGO_URL }}}}" alt="Logo" class="logo" />
                    {{% for name, endpoint, _ in NAV_ITEMS %}}
                      <a class="nav-link" href="{{{{ url_for(endpoint) }}}}">{{{{ name }}}}</a>
                    {{% endfor %}}
                    <div class="sidebar-contact">
                        <p><strong>Contact</strong></p>
                        <p><a href="mailto:{{{{ SITE_EMAIL }}}}">{{{{ SITE_EMAIL }}}}</a></p>
                    </div>
                </aside>
                <main class="content">
                    <h1 style="margin-top:0;">{{{{ page_title }}}}</h1>
                    <p>This is a temporary placeholder. Create <code>{template_name}</code> in <code>templates/</code> to customize this page.</p>
                    <div class="footer">{{{{ SITE_FOOTER_HTML|safe }}}}</div>
                </main>
            </div>
        </body>
        </html>
        """
        return render_template_string(placeholder, page_title=page_title)

# ───────────────────────── Home / simple pages ──────────────────────
@app.route("/")
def home():
    return render_page("home.html", "Home")

@app.route("/pricing")
def pricing():
    return render_page("prices.html", "Pricing")

@app.route("/about")
def about():
    return render_page("about.html", "About")

@app.route("/contact")
def contact():
    return render_page("contact.html", "Contact")

# ───────────────────────── Trainings page ───────────────────────────
def get_trainings():
    return {
        "courses": [
            {
                "name": "Advanced Machine Learning and Real-Time Deployment (Advanced Plan)",
                "image": "https://i.imgur.com/iIMdWOn.jpeg",
                "impact": (
                    "Participants will develop advanced skills in coding, database management, machine learning, and real-time "
                    "application deployment. This course focuses on practical implementations, enabling learners to create "
                    "AI-driven solutions, deploy them in real-world scenarios, and integrate apps with cloud and database systems."
                ),
                "chapters": [
                    "Week 1: Ice Breaker for Coding",
                    "Week 2: Modularity Programming",
                    "Week 3: UI and App Building",
                    "Week 4: Advanced SQL and Databases",
                    "Week 5: Fundamental of Statistics for Machine Learning",
                    "Week 6: Unsupervised Machine Learning",
                    "Week 7: Supervised Machine Learning",
                    "Week 8: Neural Network Machine Learning",
                    "Week 9: Capstone Project",
                    "9 Weeks, each week contain a theoretical and practical session",
                ],
                "availability": "Advanced Plan",
                "price": "570$",
                "request_url": "https://calendar.app.google/o6eQcsxCDwofXNn59",
            },
        ]
    }

@app.route("/trainings")
def trainings():
    data = get_trainings()
    return render_page("trainings.html", "Trainings", courses=data["courses"])

# ───────────────────────── Gallery page ─────────────────────────────
def load_gallery_cards():
    path = pathlib.Path("input/gallery.json")
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

@app.route("/gallery")
def gallery():
    cards = load_gallery_cards()
    return render_page("gallery.html", "Gallery", cards=cards)

# ───────────────────────── Certificate page ─────────────────────────
GITHUB_BASE_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/pythondemo/main/"

def load_certificates(csv_path="input/certificate.csv"):
    """
    Returns a list of participants with completed certificates.
    CSV columns: name, date of joining, date of completion, credential, certificate
    """
    rows = []
    if not os.path.exists(csv_path):
        return rows

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rec = {k.strip(): (v or "").strip() for k, v in r.items()}
            completion = rec.get("date of completion", "")
            if completion:
                cert_path = rec.get("certificate", "")
                if cert_path.startswith("certificates/"):
                    rec["_certificate_url"] = GITHUB_BASE_URL + cert_path
                elif os.path.exists(cert_path):
                    # If you put images under static/, store relative path like "certificates/abc.png"
                    # and build a static URL in the template with url_for('static', filename=...)
                    rec["_certificate_url"] = cert_path
                else:
                    rec["_certificate_url"] = None
                rows.append(rec)
    return rows

@app.route("/certificate")
def certificate():
    participants = load_certificates()
    return render_page("certificate.html", "Certificate", participants=participants)

# ───────────────────────── Participants page (MySQL) ────────────────
# progress constants (week 5 changed to 4)
REQUIRED_TABS = {1: 10, 2: 12, 3: 12, 4: 7, 5: 4}
TOTAL_REQUIRED = sum(REQUIRED_TABS.values()) or 1
WEEK_COLORS = {1: "#27c93f", 2: "#0ff", 3: "#b19cd9", 4: "#ffbd2e", 5: "#f44"}

def _get_mysql_conn():
    cfg = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", ""),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", ""),
        "autocommit": False,
    }
    return mysql.connector.connect(**cfg)

def _compute_weeks_render(weeks_dict):
    items = []
    for num in [1, 2, 3, 4, 5]:
        req = REQUIRED_TABS.get(num, 0) or 1
        done = weeks_dict.get(num, 0) or 0
        pct = min(100, round(done / req * 100))
        items.append({
            "num": num,
            "done": done,
            "req": req,
            "pct": pct,
            "color": WEEK_COLORS.get(num, "#00d4ff"),
        })
    return items

def fetch_participants():
    """
    Returns sorted list of participants:
    [
      { 'fullname': str, 'doj': 'YYYY-MM-DD', 'percent': int, 'weeks_render': [ ... ] },
      ...
    ]
    """
    query = (
        "SELECT u.fullname, u.username, u.date_of_joining, "
        "p.week1track, p.week2track, p.week3track, p.week4track, p.week5track "
        "FROM users u JOIN progress p ON u.username = p.username"
    )
    out = []
    try:
        with _get_mysql_conn() as conn:
            cur = conn.cursor()
            cur.execute(query)
            for full, user, doj, w1, w2, w3, w4, w5 in cur.fetchall():
                weeks = {1: w1 or 0, 2: w2 or 0, 3: w3 or 0, 4: w4 or 0, 5: w5 or 0}
                percent = min(100, round(sum(weeks.values()) / TOTAL_REQUIRED * 100))
                out.append({
                    "fullname": full or user,
                    "doj": doj.strftime("%Y-%m-%d") if doj else "N/A",
                    "percent": percent,
                    "weeks_render": _compute_weeks_render(weeks),
                })
    except Error as e:
        # Log error; template will show a friendly message when list is empty
        print("DB error (participants):", getattr(e, "msg", e))
    return sorted(out, key=lambda r: (-r["percent"], r["fullname"]))

@app.route("/participants")
def participants():
    data = fetch_participants()
    avg = (sum(p["percent"] for p in data) / len(data)) if data else 0.0
    stats = {"count": len(data), "avg": f"{avg:.1f}"}
    return render_page("participants.html", "Participants", participants=data, stats=stats)

# ───────────────────────── Error pages ──────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template_string(
        """
        <!doctype html>
        <title>Page Not Found — {{ SITE_TITLE }}</title>
        <div style="font-family: system-ui; padding: 40px;">
            <h1>404 — Page Not Found</h1>
            <p>We couldn't find that page. Use the menu to navigate.</p>
            <p><a href="{{ url_for('home') }}">Back to Home</a></p>
        </div>
        """,
    ), 404

# ───────────────────────── Entrypoint ───────────────────────────────
if __name__ == "__main__":
    # Local dev
    app.run(debug=True, host="0.0.0.0", port=5000)
