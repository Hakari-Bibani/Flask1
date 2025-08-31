import os
import json
import csv
import pathlib
import mimetypes
from flask import Flask, render_template, render_template_string, url_for
import mysql.connector
from mysql.connector import Error

# ────────────────────── Ensure SVG served correctly ──────────────────────
mimetypes.add_type("image/svg+xml", ".svg")

app = Flask(__name__, template_folder="templates", static_folder="static")

# ────────────────────────── Site-wide config ────────────────────────────
SITE_TITLE = "AI for Impact"
SITE_EMAIL = "connect@aiforimpact.net"
SITE_LOGO = "input/logo_improved.png"  # put at static/input/logo_improved.png
SITE_FOOTER_HTML = """
<div style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #7F8C8D;">
    aiforimpact © 2024<br>
    Powered by Climate Resilience Fundraising Platform B.V.
</div>
"""

NAV_ITEMS = [
    ("Home", "home", "home.html"),
    ("Trainings", "trainings", "trainings.html"),
    ("Pricing", "pricing", "prices.html"),
    ("Gallery", "gallery", "gallery.html"),
    ("Certificate", "certificate", "certificate.html"),
    ("Participants", "participants", "participants.html"),
    ("About", "about", "about.html"),
    ("Contact", "contact", "contact.html"),
]

@app.context_processor
def inject_globals():
    return {
        "SITE_TITLE": SITE_TITLE,
        "SITE_EMAIL": SITE_EMAIL,
        "SITE_LOGO_URL": url_for("static", filename=SITE_LOGO),
        "NAV_ITEMS": NAV_ITEMS,
        "SITE_FOOTER_HTML": SITE_FOOTER_HTML,
    }

def render_page(template_name: str, page_title: str, **ctx):
    try:
        return render_template(template_name, page_title=page_title, **ctx)
    except Exception:
        # fallback minimal page
        return render_template_string(
            """
            <!doctype html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>{{ page_title }} — {{ SITE_TITLE }}</title>
                <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            </head>
            <body>
                <div class="layout">
                    <aside class="sidebar">
                        <img src="{{ SITE_LOGO_URL }}" class="logo">
                        {% for name, endpoint, _ in NAV_ITEMS %}
                          <a class="nav-link" href="{{ url_for(endpoint) }}">{{ name }}</a>
                        {% endfor %}
                    </aside>
                    <main class="content">
                        <h1>{{ page_title }}</h1>
                        <p>Template {{ template_name }} not found.</p>
                        <div class="footer">{{ SITE_FOOTER_HTML|safe }}</div>
                    </main>
                </div>
            </body>
            </html>
            """,
            page_title=page_title, template_name=template_name
        )

# ─────────────────────────── Home / simple pages ───────────────────────────
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

# ─────────────────────────── Trainings page ───────────────────────────────
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

# ─────────────────────────── Gallery page ────────────────────────────────
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

# ─────────────────────────── Certificate page ───────────────────────────
GITHUB_BASE_URL = "https://raw.githubusercontent.com/hawkarabdulhaq/pythondemo/main/"

def load_certificates(csv_path="input/certificate.csv"):
    rows = []
    if not os.path.exists(csv_path):
        return rows
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rec = {k.strip(): (v or "").strip() for k, v in r.items()}
            if rec.get("date of completion"):
                cert_path = rec.get("certificate", "")
                if cert_path.startswith("certificates/"):
                    rec["_certificate_url"] = GITHUB_BASE_URL + cert_path
                elif os.path.exists(cert_path):
                    rec["_certificate_url"] = cert_path
                else:
                    rec["_certificate_url"] = None
                rows.append(rec)
    return rows

@app.route("/certificate")
def certificate():
    participants = load_certificates()
    return render_page("certificate.html", "Certificate", participants=participants)

# ─────────────────────────── Participants page ──────────────────────────
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
    for num in REQUIRED_TABS:
        req = REQUIRED_TABS[num]
        done = weeks_dict.get(num, 0) or 0
        pct = min(100, round(done / req * 100))
        items.append({"num": num, "done": done, "req": req, "pct": pct, "color": WEEK_COLORS[num]})
    return items

def fetch_participants():
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
        print("DB error:", getattr(e, "msg", e))
    return sorted(out, key=lambda r: (-r["percent"], r["fullname"]))

@app.route("/participants")
def participants():
    data = fetch_participants()
    avg = (sum(p["percent"] for p in data) / len(data)) if data else 0.0
    stats = {"count": len(data), "avg": f"{avg:.1f}"}
    return render_page("participants.html", "Participants", participants=data, stats=stats)

# ─────────────────────────── Error handlers ──────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template_string(
        "<h1>404 — Page Not Found</h1><p><a href='{{ url_for('home') }}'>Back Home</a></p>"
    ), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
