"""
components/footer.py — Compact feature-summary footer.

Colour scheme: light — matches the dashboard's teal-on-white palette.
Language: English.
"""

import streamlit as st


def render_footer() -> None:
    """Render the light-themed feature footer for the E-commerce Analytics Dashboard."""

    members = [
        "Huynh Duc Thinh",
        "Nguyen Minh Nhut",
    ]

    member_chips = "".join(
        [
            f'<div class="ec-ftr-chip"><span class="ec-ftr-dot"></span>{m}</div>'
            for m in members
        ]
    )

    html = f"""
<div class="ec-ftr-wrapper">
<div class="ec-ftr-container">
<div class="ec-ftr-features-grid">

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Market Overview</div>
<ul class="ec-ftr-list">
<li><span>Platform Share:</span> Listings distribution between Tiki and eBay</li>
<li><span>Price Distribution:</span> Side-by-side box plots Tiki vs. eBay (VND)</li>
<li><span>eBay Condition Mix:</span> New · Used · Refurbished breakdown</li>
<li><span>Market Signals:</span> Stagnation risk · Active discounts · New-item share</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Pricing &amp; Promotions</div>
<ul class="ec-ftr-list">
<li><span>Price Structure:</span> Violin plots, scatter &amp; histograms by category</li>
<li><span>Discount Segments:</span> Discount rate and depth across Tiki listings</li>
<li><span>Platform Comparison:</span> Tiki–eBay median price gap by active filters</li>
<li><span>Best Sellers:</span> Top-performing products and their pricing profiles</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Trust &amp; Reputation</div>
<ul class="ec-ftr-list">
<li><span>Trust Level:</span> High Trust / Normal / Low Trust seller classification</li>
<li><span>Feedback Score:</span> eBay seller rating distribution analysis</li>
<li><span>Top Sellers:</span> Ranking by listings volume and reputation score</li>
<li><span>Risk Detection:</span> Sellers with low feedback flagged for review</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Characteristics &amp; Trends</div>
<ul class="ec-ftr-list">
<li><span>Category Analysis:</span> Top Tiki categories by volume and price</li>
<li><span>Time Series:</span> Listing timeline by eBay posting date</li>
<li><span>Correlations:</span> Rating vs. Sales, Price vs. Discount</li>
</ul>
<div class="ec-ftr-col-title" style="margin-top:14px">Accessibility</div>
<ul class="ec-ftr-list">
<li><span>Colorblind Mode:</span> Deuteranopia-safe palette via one-click toggle</li>
<li><span>Global Filters:</span> Filter by platform and price range at any time</li>
<li><span>Auto Insights:</span> Contextual commentary after every chart section</li>
</ul>
</div>

</div>
<div class="ec-ftr-divider-main"></div>
<div class="ec-ftr-bottom">
<div class="ec-ftr-info">
<div class="ec-ftr-brand">
<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="18" height="18" rx="2"/>
  <path d="M3 9h18M9 21V9"/>
  <path d="M16 17l-4-4-4 4"/>
</svg>
<span>E-commerce Analytics Dashboard</span>
</div>
<div class="ec-ftr-divider"></div>
<div class="ec-ftr-text">Ho Chi Minh City University of Science</div>
<div class="ec-ftr-divider"></div>
<div class="ec-ftr-text">Instructor: Bui Tien Len</div>
<div class="ec-ftr-divider"></div>
<div class="ec-ftr-text">Data Visualization Lab · 2026</div>
</div>
<div class="ec-ftr-team-box">
<div class="ec-ftr-team-label">Development Team</div>
<div class="ec-ftr-marquee">
<div class="ec-ftr-track">
{member_chips}{member_chips}
</div>
</div>
</div>
</div>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
