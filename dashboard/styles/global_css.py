"""
styles/global_css.py — Global page CSS injected once at startup.

Layout inspired by Vietnam-Air-Quality-Dashboard:
  • Sticky header bar (ec-hdr) with colorblind toggle
  • Hover-expand left nav rail (ec-nav)
  • Mega footer (ec-ftr-*)
  • Colorblind mode: .cb-mode class on <body> remaps chart accent colours
  • Keeps existing teal palette (#0d9488) as primary brand colour
"""

GLOBAL_CSS = """
<style>

/* ── External fonts & icons ────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.2/css/all.min.css');

/* ═══════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════ */
:root {
  /* Brand */
  --clr-teal:      #0d9488;
  --clr-teal-lt:   #14b8a6;
  --clr-teal-dk:   #0f766e;
  --clr-orange:    #f97316;
  --clr-blue:      #3b82f6;
  --clr-purple:    #7c3aed;
  --clr-red:       #ef4444;
  --clr-amber:     #f59e0b;
  --clr-green:     #22c55e;
  /* Slate neutrals */
  --clr-slate-50:  #f8fafc;
  --clr-slate-100: #f1f5f9;
  --clr-slate-200: #e2e8f0;
  --clr-slate-400: #94a3b8;
  --clr-slate-600: #475569;
  --clr-slate-800: #1e293b;
  --clr-dark:      #0f172a;
  --clr-white:     #ffffff;
  /* Header */
  --hdr-bg:        #173a5e;
  --hdr-bg2:       #102844;
  --hdr-h:         68px;
  /* Nav rail */
  --nav-w:         70px;
  --nav-expand-w:  240px;
  /* Misc */
  --radius-sm:     6px;
  --radius-md:     10px;
  --radius-lg:     16px;
  --shadow-sm:     0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:     0 4px 16px rgba(0,0,0,.09), 0 2px 6px rgba(0,0,0,.06);
  --shadow-lg:     0 10px 40px rgba(0,0,0,.12), 0 4px 16px rgba(0,0,0,.08);
  --transition:    0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ═══════════════════════════════════════════════════════════════════
   RESET & BASE
   ═══════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* ── Hide all Streamlit chrome ──────────────────────────────────── */
[data-testid="stHeader"]               { display: none !important; }
[data-testid="stToolbar"]              { display: none !important; }
[data-testid="stDecoration"]           { display: none !important; }
[data-testid="stStatusWidget"]         { display: none !important; }
[data-testid="collapsedControl"]       { display: none !important; }
[data-testid="stSidebarCollapseButton"]{ display: none !important; }
button[aria-label="Close sidebar"]     { display: none !important; }
button[aria-label="Open sidebar"]      { display: none !important; }
#MainMenu                              { display: none !important; }
footer                                 { display: none !important; }

/* ── Sidebar visibility toggle via body class (mirrors cb-mode pattern) ── */
body.sb-hidden section[data-testid="stSidebar"] { display: none !important; }


/* ── Close Panel ✕: circular icon button in sidebar header ─────────────── */
section[data-testid="stSidebar"]
  [data-testid="stHorizontalBlock"]
  [data-testid="stBaseButton-secondary"] button,
section[data-testid="stSidebar"]
  [data-testid="stHorizontalBlock"]
  [data-testid="stButton"] button {
  background: rgba(255,255,255,.07) !important;
  border: 1px solid rgba(255,255,255,.14) !important;
  border-radius: 50% !important;
  color: rgba(255,255,255,.5) !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  padding: 0 !important;
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  min-height: 30px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all .22s ease !important;
  pointer-events: auto !important;
}
section[data-testid="stSidebar"]
  [data-testid="stHorizontalBlock"]
  [data-testid="stBaseButton-secondary"] button:hover,
section[data-testid="stSidebar"]
  [data-testid="stHorizontalBlock"]
  [data-testid="stButton"] button:hover {
  background: rgba(255,255,255,.14) !important;
  border-color: rgba(255,255,255,.28) !important;
  color: #fff !important;
  transform: rotate(90deg) !important;
}

/* ── Show Panel › : hidden by default, revealed when cursor enters top-left ──
   #sb-trigger  = a transparent 72×72px position:fixed div at top:0 left:0
                  rendered ONLY when sidebar is hidden (app.py).
   Default       → button off-screen (left:-200px) + opacity:0 + no pointer events
   Hover trigger → :has(#sb-trigger:hover) slides button in and fades to 0.72
   Hover button  → :hover on the button EC keeps it visible as cursor moves over  */

/* Default — completely off-screen, invisible, non-interactive */
[data-testid="element-container"]:has(#sb-trigger)
  + [data-testid="element-container"] {
  position: fixed !important;
  left: -200px !important;
  top: 14px !important;
  z-index: 9999 !important;
  margin: 0 !important;
  padding: 0 !important;
  background: transparent !important;
  opacity: 0 !important;
  pointer-events: none !important;
  transition: opacity .22s ease !important;
  width: auto !important;
  height: auto !important;
}
/* Reveal when cursor enters the top-left trigger zone */
[data-testid="element-container"]:has(#sb-trigger:hover)
  + [data-testid="element-container"] {
  left: 0 !important;
  opacity: 0.72 !important;
  pointer-events: auto !important;
}
/* Keep visible while hovering the button itself */
[data-testid="element-container"]:has(#sb-trigger)
  + [data-testid="element-container"]:hover {
  left: 0 !important;
  opacity: 0.72 !important;
  pointer-events: auto !important;
}
/* The › button */
[data-testid="element-container"]:has(#sb-trigger)
  + [data-testid="element-container"] button {
  background: linear-gradient(160deg, #0d9488, #0a7370) !important;
  border: none !important;
  border-radius: 0 10px 10px 0 !important;
  color: #fff !important;
  font-size: 1.1rem !important;
  font-weight: 800 !important;
  padding: 0 !important;
  width: 24px !important;
  height: 54px !important;
  min-width: 24px !important;
  min-height: 54px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 3px 0 14px rgba(13,148,136,.55) !important;
  cursor: pointer !important;
  pointer-events: auto !important;
  line-height: 1 !important;
}

/* ═══════════════════════════════════════════════════════════════════
   MAIN CONTENT AREA
   ═══════════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main {
  background: linear-gradient(135deg, #f0fdf9 0%, #f8fafc 45%, #f0f4ff 100%);
  background-attachment: fixed;
  padding-top: 0 !important;
  min-height: 100vh;
}

[data-testid="stAppViewContainer"] > .main::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(13,148,136,.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(124,58,237,.04) 0%, transparent 50%),
    radial-gradient(circle at 60% 10%, rgba(59,130,246,.03) 0%, transparent 40%);
  pointer-events: none;
  z-index: 0;
}


.block-container {
  padding-top: 1rem !important;
  padding-bottom: 0 !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 100% !important;
  position: relative;
  z-index: 1;
}


/* Strip Streamlit's default top margin so header can go edge-to-edge */
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
.stMainBlockContainer,
[data-testid="stApp"],
[data-testid="stHeader"] {
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  margin-top: 0 !important;
}

/* Vertical block padding reset */
[data-testid="stAppViewContainer"] > section > div,
[data-testid="column"],
[data-testid="stVerticalBlock"] {
  padding-top: 0 !important;
}

/* ─── Sidebar (dark) ─────────────────────────────────────────────── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(180deg, #0f172a 0%, #111827 60%, #0d1b2a 100%) !important;
}
section[data-testid="stSidebar"] > div:first-child {
  border-right: 1px solid rgba(255,255,255,.06) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div > div:first-child {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:first-child {
  margin-bottom: 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 0 !important;
}





/* ═══════════════════════════════════════════════════════════════════
   SHADCN METRIC CARDS
   ═══════════════════════════════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] > div {
  transition: transform var(--transition), box-shadow var(--transition);
}
[data-testid="stHorizontalBlock"] > div:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* ═══════════════════════════════════════════════════════════════════
   CONTENT CONTAINERS / CARDS
   ═══════════════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--clr-slate-200) !important;
  border-radius: var(--radius-lg) !important;
  background: rgba(255,255,255,.85) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow var(--transition), transform var(--transition) !important;
  overflow: hidden !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-1px) !important;
}

/* Plotly */
[data-testid="stPlotlyChart"] {
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
}
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
.plotly .modebar-container { opacity: 0.2; }
.plotly .modebar-container:hover { opacity: 1; }

/* Expanders */
[data-testid="stExpander"] {
  border: 1px solid var(--clr-slate-200) !important;
  border-radius: var(--radius-md) !important;
  background: rgba(255,255,255,.7) !important;
  backdrop-filter: blur(8px) !important;
}
[data-testid="stExpander"] summary {
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  color: var(--clr-slate-800) !important;
  padding: 0.65rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
  background: rgba(13,148,136,.04) !important;
}

/* st.metric widgets */
[data-testid="stMetric"] {
  background: rgba(255,255,255,.75) !important;
  border-radius: var(--radius-md) !important;
  padding: 0.8rem 1rem !important;
  border: 1px solid var(--clr-slate-200) !important;
  backdrop-filter: blur(8px) !important;
  transition: box-shadow var(--transition) !important;
}
[data-testid="stMetric"]:hover { box-shadow: var(--shadow-md) !important; }
[data-testid="stMetricLabel"] > div {
  font-size: 0.73rem !important;
  font-weight: 600 !important;
  color: var(--clr-slate-400) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] > div {
  font-size: 1.55rem !important;
  font-weight: 800 !important;
  color: var(--clr-dark) !important;
  line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] > div {
  font-size: 0.72rem !important;
  font-weight: 500 !important;
}

/* Divider */
hr {
  border-color: var(--clr-slate-200) !important;
  margin: 1.2rem 0 !important;
}

/* Alert boxes */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border-width: 0 0 0 4px !important;
  font-size: 0.83rem !important;
}

/* ═══════════════════════════════════════════════════════════════════
   FADE-IN ANIMATION
   ═══════════════════════════════════════════════════════════════════ */
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.block-container > div {
  animation: fadeSlideIn 0.32s ease both;
}

/* ═══════════════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(13,148,136,.35);
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(13,148,136,.6); }

/* ═══════════════════════════════════════════════════════════════════
   SHIMMER DIVIDER
   ═══════════════════════════════════════════════════════════════════ */
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
.shimmer-line {
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(
    90deg,
    var(--clr-slate-200) 0%,
    var(--clr-teal) 40%,
    var(--clr-purple) 60%,
    var(--clr-slate-200) 100%
  );
  background-size: 200% auto;
  animation: shimmer 3.5s linear infinite;
  margin: 0.5rem 0 1.2rem;
}

/* ═══════════════════════════════════════════════════════════════════
   COLORBLIND MODE — body.cb-mode remaps all accent colours to a
   blue-orange deuteranopia-safe palette
   ═══════════════════════════════════════════════════════════════════ */
body.cb-mode {
  --clr-teal:    #0077bb;   /* safe blue  */
  --clr-teal-lt: #33aadd;
  --clr-teal-dk: #005599;
  --clr-orange:  #ee7733;   /* safe orange */
  --clr-blue:    #0077bb;
  --clr-purple:  #aa3377;   /* safe magenta */
  --clr-red:     #cc3311;   /* safe red-orange */
  --clr-amber:   #ee7733;
  --clr-green:   #009988;   /* safe teal-green */
}

/* Remap ec-nav active state in colorblind mode */
body.cb-mode .ec-nav-item.is-active {
  background: linear-gradient(135deg, #0077bb, #005599);
  box-shadow: 0 6px 18px rgba(0,119,187,.38);
}
body.cb-mode .ec-nav {
  border-right-color: rgba(0,119,187,.2);
}
body.cb-mode .ec-nav-icon {
  background: rgba(0,119,187,.10);
}
body.cb-mode .ec-nav-item:hover {
  background: rgba(0,119,187,.12);
  border-color: rgba(0,119,187,.28);
}

/* Header accent line in CB mode */
body.cb-mode .ec-hdr {
  border-bottom: 2px solid #ee7733;
}

/* Colorblind pattern filter for charts (optional CSS filter layer) */
body.cb-mode [data-testid="stPlotlyChart"] {
  filter: url(#cb-filter);
}

/* Stat card accents in CB mode */
body.cb-mode [data-testid="stMetric"] {
  border-top: 2px solid #0077bb !important;
}

/* ── CB Mode indicator banner ──────────────────────────────────── */
body.cb-mode::after {
  content: 'COLORBLIND MODE';
  position: fixed;
  bottom: 10px;
  right: 14px;
  background: rgba(0,119,187,.18);
  border: 1px solid rgba(0,119,187,.4);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #0077bb;
  z-index: 9999;
  pointer-events: none;
}

/* ═══════════════════════════════════════════════════════════════════
   MEGA FOOTER (ec-ftr-*) — Light theme, matches dashboard palette
   ═══════════════════════════════════════════════════════════════════ */
.ec-ftr-wrapper {
  background: #f8fafc;
  margin-top: 2.5rem;
  border-top: 2px solid;
  border-image: linear-gradient(90deg, transparent, #0d9488 30%, #7c3aed 70%, transparent) 1;
  padding: 28px 0 0;
  box-shadow: 0 -4px 24px rgba(13,148,136,.06);
}
.ec-ftr-container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 28px;
}
.ec-ftr-features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding-bottom: 22px;
}
@media (max-width: 900px) {
  .ec-ftr-features-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 560px) {
  .ec-ftr-features-grid { grid-template-columns: 1fr; }
}
.ec-ftr-col-title {
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.09em;
  color: #0d9488;
  margin-bottom: 10px;
}
.ec-ftr-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.ec-ftr-list li {
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.5;
}
.ec-ftr-list li span {
  font-weight: 700;
  color: #1e293b;
}
.ec-ftr-divider-main {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0 30%, #e2e8f0 70%, transparent);
  margin: 0 0 16px;
}
.ec-ftr-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding-bottom: 18px;
  background: #ffffff;
  border-top: 1px solid #f1f5f9;
  padding-top: 14px;
  margin: 0 -28px;
  padding-left: 28px;
  padding-right: 28px;
}
.ec-ftr-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ec-ftr-brand {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 0.82rem;
  font-weight: 700;
  color: #0d9488;
}
.ec-ftr-brand svg { stroke: #0d9488; }
.ec-ftr-divider {
  width: 1px;
  height: 14px;
  background: #e2e8f0;
}
.ec-ftr-text {
  font-size: 0.72rem;
  color: #94a3b8;
}
.ec-ftr-team-box {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ec-ftr-team-label {
  font-size: 0.62rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
}
.ec-ftr-marquee {
  width: min(420px, 60vw);
  overflow: hidden;
  position: relative;
  border-radius: 6px;
}
.ec-ftr-track {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  width: max-content;
  will-change: transform;
  animation: ec-ftr-scroll 20s linear infinite;
}
.ec-ftr-track:hover { animation-play-state: paused; }
@keyframes ec-ftr-scroll {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.ec-ftr-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 0.7rem;
  color: #475569;
  white-space: nowrap;
}
.ec-ftr-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--clr-teal);
  flex-shrink: 0;
}


/* ── Shadcn iframe tab bar (hidden when using nav rail) ─────────── */
iframe[title="streamlit_shadcn_ui.tabs"] {
  margin-bottom: 0 !important;
  border-radius: var(--radius-lg) !important;
}

/* ── Shadcn metric_card inner padding ────────────────────────────── */
iframe[title="streamlit_shadcn_ui.metric_card"] {
  border-radius: var(--radius-md) !important;
}


/* ═══════════════════════════════════════════════════════════════════
   MULTISELECT — Brand teal chips across all tabs
   ═══════════════════════════════════════════════════════════════════ */

/* Container input border */
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  border: 1.5px solid var(--clr-slate-200) !important;
  border-radius: var(--radius-md) !important;
  background: rgba(255,255,255,.9) !important;
  transition: border-color var(--transition), box-shadow var(--transition) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--clr-teal) !important;
  box-shadow: 0 0 0 3px rgba(13,148,136,.12) !important;
}

/* Each selected chip */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
  background: rgba(13,148,136,.10) !important;
  border: 1px solid rgba(13,148,136,.28) !important;
  border-radius: 20px !important;
  color: var(--clr-teal-dk) !important;
  font-size: 0.73rem !important;
  font-weight: 600 !important;
  padding: 2px 10px 2px 10px !important;
  margin: 2px 3px !important;
  gap: 4px !important;
  transition: background var(--transition) !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"]:hover {
  background: rgba(13,148,136,.18) !important;
}

/* ✕ close icon inside chip */
[data-testid="stMultiSelect"] [data-baseweb="tag"] [role="presentation"] {
  color: var(--clr-teal) !important;
  opacity: 0.7 !important;
  font-size: 0.75rem !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] [role="presentation"]:hover {
  opacity: 1 !important;
  color: var(--clr-teal-dk) !important;
}

/* Label above multiselect */
[data-testid="stMultiSelect"] label {
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  color: var(--clr-slate-600) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 4px !important;
}

/* Dropdown option list */
[data-baseweb="popover"] [role="option"] {
  font-size: 0.82rem !important;
  border-radius: var(--radius-sm) !important;
  padding: 6px 12px !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"] {
  background: rgba(13,148,136,.08) !important;
  color: var(--clr-teal-dk) !important;
}

/* Clear-all (⊗) button */
[data-testid="stMultiSelect"] button[aria-label="Clear all"] {
  color: var(--clr-slate-400) !important;
  opacity: 0.7 !important;
}
[data-testid="stMultiSelect"] button[aria-label="Clear all"]:hover {
  color: var(--clr-red) !important;
  opacity: 1 !important;
}

</style>
"""
