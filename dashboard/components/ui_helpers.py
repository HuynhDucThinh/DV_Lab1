import streamlit as st

# ── Colour defaults (used when no color argument is passed) ───────────────────
_TEAL  = "#0d9488"
_SLATE = "#94a3b8"
_DARK  = "#0f172a"
_WHITE = "#ffffff"


def icon_header(
    fa_class: str,
    text: str,
    level: int = 3,
    color: str = _TEAL,
) -> None:
    """Render a section heading with an inline Font Awesome icon."""
    tag = f"h{level}"
    st.markdown(
        f'<{tag} style="margin:0.6rem 0 0.3rem;line-height:1.4;">'
        f'<i class="{fa_class}" style="color:{color};margin-right:0.5rem;"></i>'
        f'{text}</{tag}>',
        unsafe_allow_html=True,
    )


def fa_callout(fa_class: str, color: str, text: str) -> None:
    """Render a highlighted callout block with a Font Awesome icon."""
    bg = f"{color}18"   # ~10% opacity tint
    st.markdown(
        f'<div style="background:{bg};border-left:4px solid {color};'
        f'padding:0.55rem 0.9rem;border-radius:0 6px 6px 0;margin:0.4rem 0;">'
        f'<i class="{fa_class}" style="color:{color};margin-right:0.5rem;"></i>'
        f'{text}</div>',
        unsafe_allow_html=True,
    )


def stat_card(
    fa_class: str,
    label: str,
    value: str,
    desc: str,
    accent: str = _TEAL,
) -> None:
    """Render a premium bordered KPI stat card with a Font Awesome icon."""
    st.markdown(
        f'<div style="background:{_WHITE};border-radius:12px;padding:1.3rem 1.4rem;'
        f'box-shadow:0 2px 12px rgba(0,0,0,0.09);border-left:5px solid {accent};">'
        f'<div style="display:flex;align-items:center;gap:0.45rem;'
        f'font-size:0.68rem;font-weight:700;color:{_SLATE};'
        f'text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.55rem;">'
        f'<i class="{fa_class}" style="color:{accent};font-size:0.78rem;"></i>'
        f'{label}</div>'
        f'<div style="font-size:2.1rem;font-weight:800;color:{_DARK};line-height:1;'
        f'margin-bottom:0.35rem;">{value}</div>'
        f'<div style="font-size:0.74rem;color:{_SLATE};line-height:1.4;">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
