import streamlit as st


def render_footer() -> None:
    """Render the light-themed feature footer for the E-commerce Analytics Dashboard."""

    members = [
        "Phạm Ngọc Thanh",
        "Cao Tiến Thành",
        "Lê Hà Thanh Chương",
        "Nguyễn Nhựt Thanh",
        "Huỳnh Đức Thịnh",
    ]

    member_chips = "".join(
        f'<div class="ec-ftr-chip"><span class="ec-ftr-dot"></span>{m}</div>'
        for m in members
    )

    html = f"""
<div class="ec-ftr-wrapper">
<div class="ec-ftr-container">
<div class="ec-ftr-features-grid" style="grid-template-columns: repeat(6,1fr);">

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Overview</div>
<ul class="ec-ftr-list">
<li><span>Platform Share:</span> Tiki vs. eBay listing distribution</li>
<li><span>Price Snapshot:</span> Side-by-side box plots (VND)</li>
<li><span>Condition Mix:</span> New · Used · Refurbished breakdown</li>
<li><span>Market Signals:</span> Stagnation risk · Active discounts</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Pricing &amp; Promotions</div>
<ul class="ec-ftr-list">
<li><span>Price Structure:</span> Histogram, box &amp; violin by condition</li>
<li><span>Discount Segments:</span> Best Seller rate per discount tier</li>
<li><span>Shipping Overhead:</span> Stacked bar — listing vs. total cost</li>
<li><span>Top-3 Categories:</span> Highest median price &amp; shipping fee</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Trust &amp; Reputation</div>
<ul class="ec-ftr-list">
<li><span>Seller Tiers:</span> Elite · Power · Reputable · Standard</li>
<li><span>Feedback Score:</span> eBay rating distribution &amp; pricing link</li>
<li><span>Rating Impact:</span> Tiki rating vs. sales volume</li>
<li><span>Risk Detection:</span> Low-feedback sellers flagged</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Characteristics &amp; Trends</div>
<ul class="ec-ftr-list">
<li><span>Pareto Analysis:</span> Cold-start risk in Tiki categories</li>
<li><span>Condition Trends:</span> eBay listing volume by condition</li>
<li><span>Platform KDE:</span> Tiki vs. eBay price density overlay</li>
<li><span>Listing Lifecycle:</span> eBay posting timeline lollipop</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Machine Learning</div>
<ul class="ec-ftr-list">
<li><span>Best Seller Predictor:</span> Logistic Regression · Random Forest</li>
<li><span>Price Clustering:</span> K-Means market tier segmentation</li>
<li><span>Trust Score Model:</span> Gradient Boosting Regressor</li>
<li><span>Status:</span> In development · Coming soon</li>
</ul>
</div>

<div class="ec-ftr-col">
<div class="ec-ftr-col-title">Summary &amp; Conclusion</div>
<ul class="ec-ftr-list">
<li><span>Radar Profile:</span> 6-dimension Tiki vs. eBay overview</li>
<li><span>Benchmark Bar:</span> Per-metric numeric comparison</li>
<li><span>Dimension Filter:</span> Select dimensions for both charts</li>
<li><span>Final Verdict:</span> Platform recommendations by role</li>
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
<div class="ec-ftr-text">Instructor: Trần Huy Bân, Võ Nhật Tân</div>
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
