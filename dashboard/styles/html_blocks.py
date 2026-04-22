"""
styles/html_blocks.py — Reusable HTML string constants/functions injected into the page.

KEY RULE: st.markdown() uses CommonMark — blank lines INSIDE an HTML block terminate it.
Build HTML via string concatenation — no blank lines in the returned string.

Show Panel mechanism:
  app.py renders st.button("▶ Show Panel") immediately AFTER make_hero_html().
  The outer hero div has class="ec-hero" so the CSS rule in global_css.py
      [data-testid="element-container"]:has(.ec-hero) + [data-testid="element-container"]
  floats that NEXT Streamlit element-container up into the hero banner visually.
  The button itself is a native Streamlit widget → click reliably triggers st.rerun().
"""

# ── Font Awesome 6 + Inter font (injected via st.html — bypasses sanitizer) ────
FA_HTML = (
    '<link rel="stylesheet" '
    'href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free'
    '@6.5.2/css/all.min.css">'
    '<link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Inter:wght'
    '@300;400;500;600;700;800&display=swap">'
)


def make_hero_html() -> str:
    """
    Return the hero banner HTML as a single string with NO blank lines.

    The outer wrapper has class="ec-hero" so global_css.py can float the adjacent
    st.button element up into the banner area using :has(.ec-hero) + * CSS rule.
    """

    # ── Build HTML ──────────────────────────────────────────────────────────
    return (
        '<div class="ec-hero" style="background:linear-gradient(135deg,#0d9488 0%,#0f766e 40%,#1e293b 100%);'
        'border-radius:16px;padding:1.4rem 2rem;margin-bottom:1.1rem;'
        'display:flex;align-items:center;justify-content:space-between;'
        'box-shadow:0 8px 32px rgba(13,148,136,.28),0 2px 8px rgba(0,0,0,.12);'
        'position:relative;overflow:hidden;">'
        '<div style="position:absolute;right:-30px;top:-40px;width:180px;height:180px;'
        'border-radius:50%;background:rgba(255,255,255,.05);pointer-events:none;"></div>'
        '<div style="position:absolute;right:60px;bottom:-60px;width:240px;height:240px;'
        'border-radius:50%;background:rgba(255,255,255,.04);pointer-events:none;"></div>'
        '<div style="display:flex;align-items:center;gap:1rem;z-index:1;">'
        '<div style="width:48px;height:48px;border-radius:12px;'
        'background:rgba(255,255,255,.15);backdrop-filter:blur(8px);'
        'display:flex;align-items:center;justify-content:center;'
        'box-shadow:0 2px 8px rgba(0,0,0,.2);flex-shrink:0;">'
        '<i class="fa-solid fa-chart-column" style="font-size:1.3rem;color:#fff;"></i>'
        '</div>'
        '<div>'
        '<p style="font-size:1.35rem;font-weight:800;color:#fff;margin:0;'
        'line-height:1.15;letter-spacing:-0.02em;">E-commerce Analytics Dashboard</p>'
        '<p style="font-size:0.8rem;color:rgba(255,255,255,.65);margin:0.2rem 0 0;">'
        '<i class="fa-solid fa-store" style="margin-right:0.35rem;"></i>Tiki'
        '&nbsp;&bull;&nbsp;'
        '<i class="fa-brands fa-ebay" style="margin-right:0.35rem;"></i>eBay'
        '&nbsp;&mdash;&nbsp;Comprehensive multi-platform market intelligence'
        '</p>'
        '</div>'
        '</div>'
        '<div style="display:flex;flex-direction:column;align-items:flex-end;gap:0.3rem;z-index:1;">'
        '<div style="background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);'
        'border-radius:8px;padding:0.3rem 0.75rem;'
        'font-size:0.75rem;color:rgba(255,255,255,.85);font-weight:500;">'
        '<i class="fa-solid fa-calendar-check" style="margin-right:0.4rem;"></i>'
        'Data snapshot &mdash; Apr 2026'
        '</div>'
        '<div style="display:flex;align-items:center;gap:0.4rem;'
        'font-size:0.72rem;color:rgba(255,255,255,.6);">'
        '<span style="width:7px;height:7px;border-radius:50%;background:#22c55e;'
        'box-shadow:0 0 0 2px rgba(34,197,94,.3);display:inline-block;"></span>'
        'Live &mdash; filters active'
        '</div>'
        '</div>'
        '</div>'
    )


# ── Backward-compat alias ──────────────────────────────────────────────────────
HERO_HTML = make_hero_html()

# ── KPI section label ──────────────────────────────────────────────────────────
KPI_HEADER = (
    '<div style="display:flex;align-items:center;gap:0.55rem;margin:0.2rem 0 0.6rem;">'
    '<i class="fa-solid fa-gauge-high" style="color:#0d9488;font-size:0.95rem;"></i>'
    '<span style="font-size:0.72rem;font-weight:700;color:#94a3b8;'
    'text-transform:uppercase;letter-spacing:0.09em;">Platform KPIs</span>'
    '<div style="flex:1;height:1px;background:linear-gradient(90deg,#e2e8f0,transparent);'
    'margin-left:0.4rem;"></div>'
    '</div>'
)

# ── Tab section label (kept for backward compat) ───────────────────────────────
TAB_HEADER = (
    '<div style="display:flex;align-items:center;gap:0.55rem;margin:0.8rem 0 0.5rem;">'
    '<i class="fa-solid fa-table-columns" style="color:#0d9488;font-size:0.95rem;"></i>'
    '<span style="font-size:0.72rem;font-weight:700;color:#94a3b8;'
    'text-transform:uppercase;letter-spacing:0.09em;">Analysis Modules</span>'
    '<div style="flex:1;height:1px;background:linear-gradient(90deg,#e2e8f0,transparent);'
    'margin-left:0.4rem;"></div>'
    '</div>'
)

# ── Animated shimmer divider ───────────────────────────────────────────────────
SHIMMER = '<div class="shimmer-line"></div>'
