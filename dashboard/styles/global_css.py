"""
styles/global_css.py — Global page CSS injected once at startup.

Contains design tokens (CSS :root variables), layout resets, sidebar theming,
component overrides (metric cards, expanders, plotly containers), animations,
and the pill-style tab bar CSS for st.tabs().
"""

GLOBAL_CSS = """
<style>

/* ── External fonts & icons (must be first) ───────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.2/css/all.min.css');

/* ═══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════════════ */
:root {
  --clr-teal:      #0d9488;
  --clr-teal-lt:   #14b8a6;
  --clr-teal-dk:   #0f766e;
  --clr-orange:    #f97316;
  --clr-blue:      #3b82f6;
  --clr-purple:    #7c3aed;
  --clr-red:       #ef4444;
  --clr-amber:     #f59e0b;
  --clr-slate-50:  #f8fafc;
  --clr-slate-100: #f1f5f9;
  --clr-slate-200: #e2e8f0;
  --clr-slate-400: #94a3b8;
  --clr-slate-600: #475569;
  --clr-slate-800: #1e293b;
  --clr-dark:      #0f172a;
  --clr-white:     #ffffff;
  --radius-sm:     6px;
  --radius-md:     10px;
  --radius-lg:     16px;
  --shadow-sm:     0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md:     0 4px 16px rgba(0,0,0,.09), 0 2px 6px rgba(0,0,0,.06);
  --shadow-lg:     0 10px 40px rgba(0,0,0,.12), 0 4px 16px rgba(0,0,0,.08);
  --transition:    0.22s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ═══════════════════════════════════════════════════════════════════════════
   RESET & BASE
   ═══════════════════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
* { box-sizing: border-box; }

/* ── Hide all Streamlit chrome & sidebar toggle ─────────────────────────── */
[data-testid="stHeader"]             { display: none !important; }
[data-testid="stToolbar"]            { display: none !important; }
[data-testid="stDecoration"]         { display: none !important; }
[data-testid="stStatusWidget"]       { display: none !important; }
[data-testid="collapsedControl"]     { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
button[aria-label="Close sidebar"]   { display: none !important; }
button[aria-label="Open sidebar"]    { display: none !important; }
#MainMenu                            { display: none !important; }
footer                               { display: none !important; }

/* ═══════════════════════════════════════════════════════════════════════════
   MAIN CONTENT AREA
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] > .main {
  background: linear-gradient(135deg, #f0fdf9 0%, #f8fafc 45%, #f0f4ff 100%);
  background-attachment: fixed;
  padding-top: 0 !important;
  min-height: 100vh;
}

/* Subtle geometric pattern overlay */
[data-testid="stAppViewContainer"] > .main::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(13,148,136,.06) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(124,58,237,.05) 0%, transparent 50%),
    radial-gradient(circle at 60% 10%, rgba(59,130,246,.04) 0%, transparent 40%);
  pointer-events: none;
  z-index: 0;
}

.block-container {
  padding-top: 1.25rem !important;
  padding-left: 1.5rem !important;
  padding-right: 1.5rem !important;
  max-width: 100% !important;
  position: relative;
  z-index: 1;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR — dark background (widget CSS lives in components/sidebar.py)
   ═══════════════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(180deg, #0f172a 0%, #111827 60%, #0d1b2a 100%) !important;
}
section[data-testid="stSidebar"] > div:first-child {
  border-right: 1px solid rgba(255,255,255,.06) !important;
}
/* Push sidebar content flush with the top */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div:first-child,
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div > div:first-child {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
/* Collapse internal sidebar header gap (structural selector — avoids hash classes) */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:first-child {
  margin-bottom: 0 !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 0 !important;
}


/* ═══════════════════════════════════════════════════════════════════════════
   SHADCN METRIC CARDS OVERRIDE
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] > div {
  transition: transform var(--transition), box-shadow var(--transition);
}
[data-testid="stHorizontalBlock"] > div:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

/* ═══════════════════════════════════════════════════════════════════════════
   SHADCN TAB BAR
   ═══════════════════════════════════════════════════════════════════════════ */
iframe[title="streamlit_shadcn_ui.tabs"] {
  margin-bottom: 0 !important;
  border-radius: var(--radius-lg) !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CONTENT CONTAINERS / CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
  gap: 1rem !important;
}

/* Streamlit containers with border=True */
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

/* Plotly chart containers */
[data-testid="stPlotlyChart"] {
  border-radius: var(--radius-md) !important;
  overflow: hidden !important;
}

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
[data-testid="stMetric"]:hover {
  box-shadow: var(--shadow-md) !important;
}
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

/* Info / Warning / Error boxes */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border-width: 0 0 0 4px !important;
  font-size: 0.83rem !important;
}

/* ═══════════════════════════════════════════════════════════════════════════
   FADE-IN ANIMATION
   ═══════════════════════════════════════════════════════════════════════════ */
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
.block-container > div {
  animation: fadeSlideIn 0.35s ease both;
}

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBAR STYLING
   ═══════════════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(13,148,136,.35);
  border-radius: 99px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(13,148,136,.6); }

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION DIVIDER ANIMATION
   ═══════════════════════════════════════════════════════════════════════════ */
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
</style>
"""
