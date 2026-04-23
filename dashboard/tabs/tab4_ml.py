"""
tab4_ml.py — Tab 4: Machine Learning & Predictive Insights

Sections:
  1. Model Overview KPIs
  2. Confusion Matrix (Plotly heatmap)
  3. ROC-AUC Curve + SHAP Summary (static images)
  4. Live Best Seller Predictor (interactive slider → XGBoost inference)
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit_shadcn_ui as ui

_SRC = Path(__file__).resolve().parents[2] / "src"
for _p in [str(_SRC), str(_SRC / "ml")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from llm_explainer import (  # type: ignore[import-untyped]
        explain as _llm_explain,
        explain_stream as _llm_explain_stream,
        PROVIDER_LABELS as _LLM_LABELS,
        INSTALL_HINTS as _LLM_HINTS,
        detect_available_providers as _llm_detect,
    )
    _LLM_AVAILABLE = True
except Exception:
    _llm_explain = None
    _llm_explain_stream = None
    _llm_detect = lambda: []
    _LLM_AVAILABLE = False
    _LLM_LABELS = {
        "openai": "OpenAI (GPT-4o mini)",
        "gemini": "Google Gemini 1.5 Flash",
        "claude": "Anthropic Claude Haiku",
        "grok":   "xAI Grok",
    }
    _LLM_HINTS = {"openai": "openai", "gemini": "google-generativeai", "claude": "anthropic", "grok": "openai"}

from components.ui_helpers import icon_header as _icon_header, fa_callout as _fa_callout
from config import get_chart_palette as _get_palette

# Artifact paths (relative to project root)
_MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
_MODEL_PATH  = _MODELS_DIR / "xgboost_tiki.pkl"
_ENC_PATH    = _MODELS_DIR / "encoders.pkl"
_CM_PATH     = _MODELS_DIR / "confusion_matrix.npy"
_MET_PATH    = _MODELS_DIR / "metrics.json"
_ROC_PATH    = _MODELS_DIR / "roc_auc_curve.png"
_SHAP_PATH   = _MODELS_DIR / "shap_summary.png"

# Cached loaders
@st.cache_resource(show_spinner="Loading ML model…")
def _load_artifacts():
    model    = joblib.load(_MODEL_PATH)
    encoders = joblib.load(_ENC_PATH)
    cm       = np.load(_CM_PATH)
    with open(_MET_PATH, encoding="utf-8") as f:
        metrics = json.load(f)
    return model, encoders, cm, metrics

# Section 1: KPI Overview
def _render_kpi_overview(metrics: dict, cm: np.ndarray) -> None:
    pal = _get_palette()
    _icon_header("fa-solid fa-gauge-high", "1. Model Performance Overview", color=pal["teal"])

    report = metrics["classification_report"]
    roc_auc  = metrics["roc_auc"]
    accuracy = report["accuracy"]
    f1_bs    = report["1"]["f1-score"]
    prec_bs  = report["1"]["precision"]
    recall_bs= report["1"]["recall"]
    total    = int(report["weighted avg"]["support"])
    pos_n    = int(report["1"]["support"])
    neg_n    = int(report["0"]["support"])
    tn, fp, fn, tp = cm[0,0], cm[0,1], cm[1,0], cm[1,1]

    # Algorithm info banner
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,rgba(13,148,136,.07),rgba(124,58,237,.05));
                    border:1.5px solid rgba(13,148,136,.18);border-radius:12px;
                    padding:1rem 1.4rem;margin-bottom:1.2rem;
                    display:flex;align-items:center;gap:1rem;">
          <i class="fa-solid fa-brain" style="font-size:1.8rem;color:{pal['teal']};"></i>
          <div>
            <div style="font-weight:800;font-size:0.95rem;color:#0f172a;">
              XGBoost Binary Classifier — Tiki Best Seller Prediction
            </div>
            <div style="font-size:0.78rem;color:#64748b;margin-top:0.2rem;">
              Features: price, original_price, discount_rate, rating_average, Price_Gap,
              brand_freq, category_freq &nbsp;·&nbsp;
              Imbalance handling: <code>scale_pos_weight</code> &nbsp;·&nbsp;
              Test set: {total:,} samples ({pos_n:,} Best Seller / {neg_n:,} Non Best Seller)
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("ROC-AUC",  f"{roc_auc:.3f}",  "Excellent ≥ 0.90")
    k2.metric("Accuracy",  f"{accuracy:.1%}", None)
    k3.metric("F1 (Best Seller)", f"{f1_bs:.3f}", None)
    k4.metric("Recall (Best Seller)", f"{recall_bs:.1%}", f"Missed {fn} of {pos_n}")

    with st.expander("Classification Report — Detail"):
        cr = report
        rows = []
        for cls, lbl in [("0","Non Best Seller"), ("1","Best Seller"),
                         ("macro avg","Macro Avg"), ("weighted avg","Weighted Avg")]:
            d = cr[cls]
            rows.append({
                "Class": lbl,
                "Precision": f"{d['precision']:.3f}",
                "Recall":    f"{d['recall']:.3f}",
                "F1-Score":  f"{d['f1-score']:.3f}",
                "Support":   f"{int(d['support']):,}",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.divider()

# Section 2: Confusion Matrix
def _render_confusion_matrix(cm: np.ndarray) -> None:
    pal = _get_palette()
    _icon_header("fa-solid fa-table-cells", "2. Confusion Matrix", color=pal["indigo"])

    tn, fp, fn, tp = cm[0,0], cm[0,1], cm[1,0], cm[1,1]
    total = tn + fp + fn + tp

    z    = [[tn, fp], [fn, tp]]
    text = [
        [f"<b>TN</b><br>{tn:,}<br>({tn/total:.1%})", f"<b>FP</b><br>{fp:,}<br>({fp/total:.1%})"],
        [f"<b>FN</b><br>{fn:,}<br>({fn/total:.1%})", f"<b>TP</b><br>{tp:,}<br>({tp/total:.1%})"],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=["Predicted: Non BS", "Predicted: Best Seller"],
        y=["Actual: Non BS",    "Actual: Best Seller"],
        text=text,
        texttemplate="%{text}",
        colorscale=[[0, "#f0fdf4"], [0.5, "#5eead4"], [1.0, pal["teal"]]],
        showscale=False,
        hovertemplate="Actual: %{y}<br>Predicted: %{x}<br>Count: %{z}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white",
        height=340,
        margin=dict(t=30, b=30, l=120, r=30),
        xaxis=dict(side="bottom", tickfont=dict(size=12)),
        yaxis=dict(tickfont=dict(size=12), autorange="reversed"),
        font=dict(size=13),
    )
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f"""
            <div style="font-size:0.78rem;line-height:1.7;padding:0.3rem 0;">
              <b>True Negatives (TN) = {tn:,}</b> — Correctly predicted Non Best Seller<br>
              <b>False Positives (FP) = {fp:,}</b> — Predicted Best Seller, actually not<br>
              <b>False Negatives (FN) = {fn:,}</b> — Missed actual Best Sellers<br>
              <b>True Positives (TP) = {tp:,}</b> — Correctly predicted Best Seller
            </div>""", unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
            spec      = tn / (tn + fp) if (tn + fp) > 0 else 0
            st.markdown(f"""
            <div style="font-size:0.78rem;line-height:1.7;padding:0.3rem 0;">
              <b>Precision (Best Seller)</b> = {precision:.3f}<br>
              <b>Recall (Best Seller)</b> = {recall:.3f}<br>
              <b>Specificity (Non BS)</b> = {spec:.3f}<br>
              <b>Balanced Accuracy</b> = {(recall + spec)/2:.3f}
            </div>""", unsafe_allow_html=True)

    st.divider()

# Section 3: ROC-AUC & SHAP Images
def _render_model_plots() -> None:
    pal = _get_palette()
    _icon_header("fa-solid fa-chart-line", "3. ROC-AUC Curve & SHAP Feature Importance", color=pal["orange"])

    col_roc, col_shap = st.columns(2)
    with col_roc:
        with st.container(border=True):
            st.markdown("**ROC-AUC Curve**")
            st.caption("Area under curve = 0.915 — model strongly separates Best Seller vs Non Best Seller")
            st.image(str(_ROC_PATH), use_container_width=True)

    with col_shap:
        with st.container(border=True):
            st.markdown("**SHAP Feature Importance**")
            st.caption("Higher |SHAP value| = greater impact on prediction. Dots colored by feature value.")
            st.image(str(_SHAP_PATH), use_container_width=True)

    with st.expander("How to read these charts"):
        st.markdown("""
**ROC-AUC Curve:**
- X-axis = False Positive Rate, Y-axis = True Positive Rate
- AUC = 0.915 means the model correctly ranks a Best Seller above a Non Best Seller **91.5% of the time**
- Dashed diagonal = random classifier (AUC = 0.5)

**SHAP Summary Plot:**
- Each row = one feature; each dot = one training sample
- Dot position on X-axis = SHAP value (impact on log-odds of being Best Seller)
- Red dots = high feature value, Blue dots = low feature value
- `rating_average` and `discount_rate` are the most influential features
""")

    st.divider()

# Section 4: Live Predictor
def _render_live_predictor(model, encoders: dict) -> None:
    pal = _get_palette()
    _icon_header("fa-solid fa-wand-magic-sparkles", "4. Live Best Seller Predictor", color=pal["teal"])

    st.markdown(
        "<div style='font-size:0.84rem;color:#64748b;margin-bottom:1rem;'>"
        "Adjust the product parameters below — the XGBoost model will predict"
        " the probability of a product becoming a <b>Best Seller</b> on Tiki.</div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            price = st.slider(
                "Selling Price (VND)", 50_000, 5_000_000, 500_000, step=50_000,
                format="%d VND",
            )
            original_price = st.slider(
                "Original Price (VND)", 50_000, 5_000_000,
                max(500_000, price), step=50_000,
                format="%d VND",
            )
            discount_rate = st.slider(
                "Discount Rate (%)", 0.0, 80.0,
                round((1 - price / max(original_price, 1)) * 100, 1),
                step=0.5,
            )
        with c2:
            rating = st.slider("Rating Average (0–5)", 0.0, 5.0, 4.2, step=0.1)
            category_freq_pct = st.slider(
                "Category Popularity (%)",
                0.0, 30.0, 5.0, step=0.5,
                help="Frequency of the category in the Tiki dataset (% of listings). "
                     "More popular categories have higher values.",
            )
            brand_freq_pct = st.slider(
                "Brand Popularity (%)",
                0.0, 20.0, 2.0, step=0.5,
                help="Frequency of the brand in the Tiki dataset (% of listings).",
            )

    # Build feature vector
    price_gap = max(float(original_price) - float(price), 0.0)
    X = pd.DataFrame([{
        "price":          float(price),
        "original_price": float(original_price),
        "discount_rate":  float(discount_rate),
        "rating_average": float(rating),
        "Price_Gap":      price_gap,
        "brand_freq":     float(brand_freq_pct) / 100.0,
        "category_freq":  float(category_freq_pct) / 100.0,
    }])

    proba = float(model.predict_proba(X)[0, 1])
    pred  = proba >= 0.5
    pct   = proba * 100

    # Gauge chart
    gauge_color = pal["teal"] if pred else pal["orange"]
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        number={"suffix": "%", "font": {"size": 36}},
        delta={"reference": 50, "valueformat": ".1f"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": gauge_color, "thickness": 0.25},
            "bgcolor": "white",
            "steps": [
                {"range": [0,  50], "color": "rgba(239,68,68,.08)"},
                {"range": [50, 75], "color": "rgba(245,158,11,.08)"},
                {"range": [75,100], "color": "rgba(13,148,136,.08)"},
            ],
            "threshold": {
                "line": {"color": "#334155", "width": 2},
                "thickness": 0.75,
                "value": 50,
            },
        },
        title={"text": "Best Seller Probability", "font": {"size": 15}},
    ))
    fig_gauge.update_layout(
        height=280, margin=dict(t=40, b=10, l=30, r=30),
        template="plotly_white",
    )

    res_col, detail_col = st.columns([1, 1])
    with res_col:
        st.plotly_chart(fig_gauge, width="stretch")

    with detail_col:
        st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
        if pred:
            with st.container(border=True):
                ui.badges(
                    badge_list=[("Best Seller", "default")],
                    class_name="flex justify-center gap-2",
                    key="verdict_badge",
                )
                st.markdown(
                    f"<div style='text-align:center;font-size:0.82rem;color:#64748b;margin-top:.5rem;'>"
                    f"Probability <b>{pct:.1f}%</b> &ge; threshold 50%</div>",
                    unsafe_allow_html=True,
                )
        else:
            with st.container(border=True):
                ui.badges(
                    badge_list=[("Not Best Seller", "secondary")],
                    class_name="flex justify-center gap-2",
                    key="verdict_badge",
                )
                st.markdown(
                    f"<div style='text-align:center;font-size:0.82rem;color:#64748b;margin-top:.5rem;'>"
                    f"Probability <b>{pct:.1f}%</b> &lt; threshold 50%</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("**Input features:**")
        st.dataframe(
            X.T.rename(columns={0: "Value"}).style.format("{:.4f}"),
            use_container_width=True,
        )

    st.divider()
    _render_llm_explanation(X.iloc[0].to_dict(), proba)


def _render_llm_explanation(features: dict, proba: float) -> None:
    pal = _get_palette()
    _icon_header("fa-solid fa-message", "5. AI-Powered Explanation", color=pal["purple"])

    st.markdown(
        "<div style='font-size:0.84rem;color:#64748b;margin-bottom:1rem;'>"
        "Select a provider and language, then click <b>Get Explanation</b>. "
        "Configure API keys in the <code>.env</code> file at the project root.</div>",
        unsafe_allow_html=True,
    )

    if not _LLM_AVAILABLE:
        st.error("llm_explainer module could not be loaded. Check src/llm_explainer.py.")
        return

    available = _llm_detect()

    if not available:
        st.info(
            "No LLM API keys found. Open `.env` at the project root and fill in at least one key:\n\n"
            "```\nOPENAI_API_KEY=sk-...\nGEMINI_API_KEY=AIza...\n"
            "ANTHROPIC_API_KEY=sk-ant-...\nGROQ_API_KEY=gsk-...\n```\n\n"
            "Then restart the dashboard for the changes to take effect."
        )
        return

    cfg_col, lang_col, badge_col = st.columns([2, 1, 1])
    with cfg_col:
        provider = st.selectbox(
            "Provider",
            options=available,
            format_func=lambda p: _LLM_LABELS.get(p, p),
            key="llm_provider",
        )
    with lang_col:
        lang_label = st.radio(
            "Language",
            ["English", "Tiếng Việt"],
            horizontal=True,
            key="llm_lang",
        )
        lang = "vi" if lang_label == "Tiếng Việt" else "en"
    with badge_col:
        st.markdown("<div style='margin-top:1.7rem;'>", unsafe_allow_html=True)
        ui.badges(
            badge_list=[(f"{len(available)} provider(s) configured", "default")],
            class_name="flex gap-2",
            key="llm_available_badge",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Get Explanation", key="llm_explain_btn", type="primary"):
        label = _LLM_LABELS.get(provider, provider)
        try:
            with st.container(border=True):
                ui.badges(
                    badge_list=[(label, "secondary")],
                    class_name="flex gap-2 mb-3",
                    key="llm_provider_badge_stream",
                )
                full_text = st.write_stream(
                    _llm_explain_stream(features=features, proba=proba, provider=provider, lang=lang)
                )
            st.session_state["_llm_result"] = full_text
            st.session_state["_llm_result_provider"] = provider
        except ImportError:
            pkg = _LLM_HINTS.get(provider, provider)
            st.error(f"Package not installed. Run: `pip install {pkg}`")
        except Exception as exc:
            st.error(f"Error: {exc}")
    elif "_llm_result" in st.session_state:
        used = st.session_state.get("_llm_result_provider", "")
        label = _LLM_LABELS.get(used, used)
        with st.container(border=True):
            ui.badges(
                badge_list=[(label, "secondary")],
                class_name="flex gap-2 mb-3",
                key="llm_provider_badge",
            )
            st.markdown(st.session_state["_llm_result"])

# Main render entrypoint
def render(filters: Dict[str, Any]) -> None:
    """Main rendering entrypoint for Tab 4: Machine Learning."""
    _icon_header("fa-solid fa-brain", "Machine Learning &amp; Predictive Insights", level=2)

    # Load all artifacts once (cached)
    try:
        model, encoders, cm, metrics = _load_artifacts()
    except Exception as e:
        _fa_callout(
            "fa-solid fa-circle-exclamation", "#ef4444",
            f"Failed to load model artifacts from `models/`: {e}",
        )
        return

    with st.expander("About this tab"):
        st.markdown("""
This tab presents the results of a **XGBoost Best Seller Classifier** trained on Tiki listings.

**Goal:** Predict whether a product listing will achieve **Best Seller** status based on
pricing features, discount behaviour, rating, and category/brand frequency.

**Sections:**
1. **Model Overview** — Key performance metrics (ROC-AUC, Accuracy, F1)
2. **Confusion Matrix** — Breakdown of TP / TN / FP / FN on the 2,000-sample test set
3. **ROC Curve & SHAP** — Model discrimination power and feature importance explanations
4. **Live Predictor** — Interactive tool: adjust product attributes and get real-time prediction
""")

    _render_kpi_overview(metrics, cm)
    _render_confusion_matrix(cm)
    _render_model_plots()
    _render_live_predictor(model, encoders)
