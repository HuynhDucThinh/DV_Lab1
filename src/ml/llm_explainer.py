from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PROVIDERS = ("openai", "gemini", "claude", "grok", "groq")

ProviderType = Literal["openai", "gemini", "claude", "grok", "groq"]

PROVIDER_LABELS = {
    "openai": "OpenAI (GPT-4o mini)",
    "gemini": "Google Gemini 1.5 Flash",
    "claude": "Anthropic Claude Haiku",
    "grok":   "xAI Grok",
    "groq":   "Groq (Llama 3.3 70B)",
}

PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "grok":   "GROK_API_KEY",
    "groq":   "GROQ_API_KEY",
}

INSTALL_HINTS = {
    "openai": "openai",
    "gemini": "google-generativeai",
    "claude": "anthropic",
    "grok":   "openai",
    "groq":   "openai",
}


def get_api_key(provider: str) -> str | None:
    """Return the API key for a provider from the environment, or None if not set."""
    env_var = PROVIDER_ENV_KEYS.get(provider)
    return os.getenv(env_var) if env_var else None


def detect_available_providers() -> list[str]:
    """Return the ordered list of providers that have an API key configured."""
    return [p for p in PROVIDERS if get_api_key(p)]


def get_default_provider() -> str | None:
    """Return the first available provider, or None if none is configured."""
    available = detect_available_providers()
    return available[0] if available else None


def build_prompt(features: dict[str, float], proba: float, lang: str = "en") -> str:
    """Build analysis prompt. lang='en' for English, 'vi' for Vietnamese."""
    price          = features.get("price", 0)
    original_price = features.get("original_price", 0)
    discount_rate  = features.get("discount_rate", 0)
    rating         = features.get("rating_average", 0)
    price_gap      = features.get("Price_Gap", 0)
    brand_freq     = features.get("brand_freq", 0) * 100
    category_freq  = features.get("category_freq", 0) * 100
    verdict        = "BEST SELLER" if proba >= 0.5 else "NOT Best Seller"

    if lang == "vi":
        viet_verdict = "BÁN CHẠY NHẤT" if proba >= 0.5 else "KHÔNG phải Best Seller"
        return (
            "Bạn là chuyên gia phân tích thương mại điện tử, chuyên về Tiki — sàn TMĐT hàng đầu Việt Nam.\n\n"
            f"Mô hình XGBoost được huấn luyện trên 10.000 sản phẩm Tiki thực tế dự đoán sản phẩm này "
            f"có xác suất {proba * 100:.1f}% trở thành Best Seller.\n\n"
            "Thông số sản phẩm:\n"
            f"- Giá bán: {price:,.0f} VND\n"
            f"- Giá gốc: {original_price:,.0f} VND\n"
            f"- Tỷ lệ giảm giá: {discount_rate:.1f}%\n"
            f"- Chênh lệch giá: {price_gap:,.0f} VND\n"
            f"- Điểm đánh giá: {rating:.1f} / 5.0\n"
            f"- Mức độ phổ biến danh mục: {category_freq:.1f}% trên Tiki\n"
            f"- Mức độ phổ biến thương hiệu: {brand_freq:.1f}% trên Tiki\n\n"
            f"Kết quả mô hình: {viet_verdict} (ngưỡng phân loại = 50%)\n\n"
            "Trả lời đúng 3 gạch đầu dòng:\n"
            "1. Yếu tố chính tác động đến kết quả dự đoán dựa trên số liệu\n"
            "2. Yếu tố rủi ro lớn nhất hoặc điểm yếu trong các chỉ số\n"
            "3. Một bước hành động cụ thể để tăng xác suất trở thành Best Seller\n\n"
            "Mỗi gạch đầu dòng không quá 60 từ. Phân tích dựa trên số liệu, tránh lời khuyên chung chung."
        )

    return (
        "You are an e-commerce analyst specialized in Tiki, Vietnam's leading marketplace.\n\n"
        f"An XGBoost classifier trained on 10,000 real Tiki listings predicts this product "
        f"has a {proba * 100:.1f}% probability of becoming a Best Seller.\n\n"
        "Product metrics:\n"
        f"- Selling price: {price:,.0f} VND\n"
        f"- Original price: {original_price:,.0f} VND\n"
        f"- Discount rate: {discount_rate:.1f}%\n"
        f"- Price markdown (gap): {price_gap:,.0f} VND\n"
        f"- Rating average: {rating:.1f} / 5.0\n"
        f"- Category popularity: {category_freq:.1f}% of all Tiki listings\n"
        f"- Brand popularity: {brand_freq:.1f}% of all Tiki listings\n\n"
        f"Model verdict: {verdict} (classification threshold = 50%)\n\n"
        "Respond with exactly 3 bullet points:\n"
        "1. The primary driver(s) behind this prediction based on the numbers\n"
        "2. The biggest risk factor or weakness in these metrics\n"
        "3. One concrete, actionable step to increase Best Seller probability\n\n"
        "Keep each bullet under 60 words. Be data-specific, avoid generic advice."
    )


def _call_openai(prompt: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str, api_key: str) -> str:
    import google.generativeai as genai  # type: ignore[import-untyped]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0.4, "max_output_tokens": 512},
    )
    return response.text.strip()


def _call_claude(prompt: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _call_grok(prompt: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    response = client.chat.completions.create(
        model="grok-3-mini-fast",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def _call_groq(prompt: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def _stream_openai_compat(
    prompt: str, api_key: str, model: str, base_url: str | None = None
):
    from openai import OpenAI
    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    with client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=512,
        stream=True,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


def _stream_gemini(prompt: str, api_key: str):
    import google.generativeai as genai  # type: ignore[import-untyped]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    for chunk in model.generate_content(
        prompt,
        generation_config={"temperature": 0.4, "max_output_tokens": 512},
        stream=True,
    ):
        if chunk.text:
            yield chunk.text


def _stream_claude(prompt: str, api_key: str):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    with client.messages.stream(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        yield from stream.text_stream


def explain(
    features: dict[str, float],
    proba: float,
    provider: ProviderType,
    lang: str = "en",
    api_key: str | None = None,
) -> str:
    """Generate a natural language explanation (non-streaming)."""
    key = api_key or get_api_key(provider)
    if not key:
        env_var = PROVIDER_ENV_KEYS.get(provider, "")
        raise ValueError(f"No API key for '{provider}'. Set {env_var} in .env.")

    prompt = build_prompt(features, proba, lang)

    if provider == "openai":
        return _call_openai(prompt, key)
    if provider == "gemini":
        return _call_gemini(prompt, key)
    if provider == "claude":
        return _call_claude(prompt, key)
    if provider == "grok":
        return _call_grok(prompt, key)
    if provider == "groq":
        return _call_groq(prompt, key)

    raise ValueError(f"Unknown provider {provider!r}. Choose from {PROVIDERS}.")


def explain_stream(
    features: dict[str, float],
    proba: float,
    provider: ProviderType,
    lang: str = "en",
    api_key: str | None = None,
):
    """Generator that yields text chunks for streaming display in Streamlit."""
    key = api_key or get_api_key(provider)
    if not key:
        env_var = PROVIDER_ENV_KEYS.get(provider, "")
        raise ValueError(f"No API key for '{provider}'. Set {env_var} in .env.")

    prompt = build_prompt(features, proba, lang)

    if provider == "openai":
        yield from _stream_openai_compat(prompt, key, "gpt-4o-mini")
    elif provider == "gemini":
        yield from _stream_gemini(prompt, key)
    elif provider == "claude":
        yield from _stream_claude(prompt, key)
    elif provider == "grok":
        yield from _stream_openai_compat(prompt, key, "grok-3-mini-fast", "https://api.x.ai/v1")
    elif provider == "groq":
        yield from _stream_openai_compat(prompt, key, "llama-3.3-70b-versatile", "https://api.groq.com/openai/v1")
    else:
        raise ValueError(f"Unknown provider {provider!r}. Choose from {PROVIDERS}.")

