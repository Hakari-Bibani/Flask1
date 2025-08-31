from flask import Flask, render_template, render_template_string, url_for, abort
from jinja2 import TemplateNotFound

app = Flask(__name__, template_folder="templates", static_folder="static")

# ───────────────────────── Site-wide config ─────────────────────────
SITE_TITLE = "AI for Impact"
SITE_EMAIL = "connect@aiforimpact.net"
SITE_LOGO = "input/logo_improved.png"   # served from /static/input/logo_improved.png
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
def render_page(template_name: str, page_title: str):
    try:
        return render_template(template_name, page_title=page_title)
    except TemplateNotFound:
        # Minimal placeholder so the route still works before you create templates
        placeholder = f"""
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>{{{{ page_title }}}} — {{{{ SITE_TITLE }}}}</title>
            <link rel="stylesheet" href="{{{{ url_for('static', filename='style.css') }}}}">
            <style>
                body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji'; margin: 0; }}
                .layout {{ display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }}
                aside {{ background: #11181C; color: #EEE; padding: 24px; }}
                aside img {{ max-width: 200px; display: block; margin-bottom: 24px; }}
                aside a {{ display: block; color: #EEE; text-decoration: none; padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; }}
                aside a:hover {{ background: #1f2a30; }}
                main {{ padding: 28px 32px; }}
                .footer {{ margin-top: 48px; color: #7F8C8D; font-size: 0.9em; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="layout">
                <aside>
                    <img src="{{{{ SITE_LOGO_URL }}}}" alt="Logo" />
                    {{% for name, endpoint, _ in NAV_ITEMS %}}
                        <a href="{{{{ url_for(endpoint) }}}}">{{{{ name }}}}</a>
                    {{% endfor %}}
                    <div style="margin-top: 30px; font-size: 1.05em;">
                        <p><strong>Contact</strong></p>
                        <p>Email: <a href="mailto:{{{{ SITE_EMAIL }}}}" style="color:#1ABC9C;">{{{{ SITE_EMAIL }}}}</a></p>
                    </div>
                </aside>
                <main>
                    <h1 style="margin-top:0;">{{{{ page_title }}}}</h1>
                    <p>This is a temporary placeholder. Create <code>{template_name}</code> in <code>templates/</code> to customize this page.</p>
                    <div class="footer">{{{{ SITE_FOOTER_HTML|safe }}}}</div>
                </main>
            </div>
        </body>
        </html>
        """
        return render_template_string(placeholder, page_title=page_title)

# ───────────────────────── Routes ───────────────────────────────────
@app.route("/")
def home():
    return render_page("home.html", "Home")

@app.route("/trainings")
def trainings():
    return render_page("trainings.html", "Trainings")

@app.route("/pricing")
def pricing():
    return render_page("prices.html", "Pricing")

@app.route("/gallery")
def gallery():
    return render_page("gallery.html", "Gallery")

@app.route("/certificate")
def certificate():
    return render_page("certificate.html", "Certificate")

@app.route("/participants")
def participants():
    return render_page("participants.html", "Participants")

@app.route("/about")
def about():
    return render_page("about.html", "About")

@app.route("/contact")
def contact():
    return render_page("contact.html", "Contact")

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
    # For local development: python main.py
    app.run(debug=True, host="0.0.0.0", port=5000)

