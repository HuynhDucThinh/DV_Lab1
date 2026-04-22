"""
components/header.py — Hero banner, colorblind body-class injection, and sidebar Show Panel.

Public API:
    inject_colorblind_class()  → injects JS to add/remove body.cb-mode
    render_hero()              → renders the teal hero banner (from styles/html_blocks)
    render_show_panel()        → renders the invisible ›  Show-Panel trigger (only when sidebar hidden)
    render_header()            → legacy sticky HTML header (kept for backward compat)
"""

import streamlit as st
from styles.html_blocks import make_hero_html


# ── 1. Colorblind body-class injection ───────────────────────────────────────

def inject_colorblind_class() -> None:
    """
    Add/remove body.cb-mode class via an inline <script> tag (no page reload).
    Must be called every render so the class stays in sync with session state.
    """
    colorblind_on = bool(st.session_state.get("colorblind_mode", False))
    js = (
        "document.body.classList.add('cb-mode');"
        if colorblind_on else
        "document.body.classList.remove('cb-mode');"
    )
    st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)


# ── 2. Hero banner ────────────────────────────────────────────────────────────

def render_hero() -> None:
    """
    Render the teal gradient hero banner.
    Reads colorblind_mode from session state internally.
    """
    colorblind_on = bool(st.session_state.get("colorblind_mode", False))
    st.markdown(make_hero_html(colorblind_on=colorblind_on), unsafe_allow_html=True)


# ── 3. Show Panel trigger (only when sidebar is hidden) ───────────────────────

def render_show_panel() -> None:
    """
    Render the invisible Show-Panel ›  button in the top-left corner.

    Two-part mechanism:
      • A transparent position:fixed 72×72px div (#sb-trigger) serves as the
        hover-detection zone.  CSS :has(#sb-trigger:hover) selects the adjacent
        element-container and fades the button into view.
      • A native st.button("›") — real Streamlit widget, guaranteed rerun on click.

    Call this ONLY when sidebar is hidden.
    CSS in styles/global_css.py handles invisibility and reveal on hover.
    """
    # Hover trigger zone — position:fixed via inline style so it works even
    # before global CSS loads (avoids flash of visible button).
    st.markdown(
        '<div id="sb-trigger" style="'
        "position:fixed;top:0;left:0;width:72px;height:72px;"
        "z-index:9998;background:transparent;pointer-events:auto;"
        '"></div>',
        unsafe_allow_html=True,
    )
    if st.button("›", key="show_sidebar_btn", help="Show sidebar panel"):
        st.session_state["sidebar_hidden"] = False
        st.rerun()


# ── 4. Legacy sticky header (backward compat) ─────────────────────────────────

def render_header() -> None:
    """
    Legacy: render the sticky HTML top header bar with colorblind toggle.
    Kept for backward compatibility — prefer render_hero() for new code.
    """
    colorblind_on = bool(st.session_state.get("colorblind_mode", False))
    header_class = "ec-hdr ec-hdr-cb" if colorblind_on else "ec-hdr"
    toggle_href = "?cb=toggle"

    if colorblind_on:
        colorblind_badge = (
            f"<a class='ec-hdr-mode-link' href='{toggle_href}' target='_self' "
            f"title='Bấm để tắt chế độ mù màu'>"
            f"<div class='ec-hdr-mode ec-hdr-mode-on'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' "
            f"fill='none' stroke='currentColor' stroke-width='2.2' stroke-linecap='round' "
            f"stroke-linejoin='round' style='flex-shrink:0'>"
            f"<circle cx='12' cy='12' r='3'/>"
            f"<path d='M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12"
            f"M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12'/>"
            f"</svg>"
            f"Mù màu: Bật</div></a>"
        )
    else:
        colorblind_badge = (
            f"<a class='ec-hdr-mode-link' href='{toggle_href}' target='_self' "
            f"title='Bấm để bật chế độ mù màu'>"
            f"<div class='ec-hdr-mode'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' "
            f"fill='none' stroke='currentColor' stroke-width='2.2' stroke-linecap='round' "
            f"stroke-linejoin='round' style='flex-shrink:0'>"
            f"<path d='M9.88 9.88a3 3 0 1 0 4.24 4.24'/>"
            f"<path d='M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68'/>"
            f"<path d='M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61'/>"
            f"<line x1='2' x2='22' y1='2' y2='22'/>"
            f"</svg>"
            f"Mù màu: Tắt</div></a>"
        )

    st.markdown(
        f"""
<div class="{header_class}">
  <div class="ec-hdr-left">
    <div class="ec-hdr-logo">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
           fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3h18v18H3z" stroke="none"/>
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M3 9h18M9 21V9"/>
        <path d="M16 17l-4-4-4 4"/>
      </svg>
    </div>
    <div>
      <div class="ec-hdr-school">ĐẠI HỌC KHOA HỌC TỰ NHIÊN, ĐHQG–HCM &nbsp;·&nbsp; KHOA CNTT &nbsp;·&nbsp; Trực quan hóa Dữ liệu</div>
      <div class="ec-hdr-title">E-commerce Analytics Dashboard</div>
      <div class="ec-hdr-sub">
        Tiki &nbsp;·&nbsp; eBay &nbsp;&mdash;&nbsp; Multi-platform Market Intelligence &nbsp;·&nbsp; Apr 2026
      </div>
    </div>
  </div>
  <div class="ec-hdr-right">
    {colorblind_badge}
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
