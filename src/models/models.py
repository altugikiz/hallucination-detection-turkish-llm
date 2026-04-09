import os
import time
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiDailyQuotaExceeded(Exception):
    """Günlük kota dolduğunda fırlatılır — retry yapılmaz."""
    pass


def _is_rpm_rate_limit(exc: Exception) -> bool:
    """Sadece dakika başı (RPM) limitlerde True döner — retry edilebilir.
    Günlük kota hatalarında False döner — retry edilmez."""
    msg = str(exc)
    if "PerDay" in msg or "PerDayPer" in msg or "daily" in msg.lower():
        return False
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg or "ResourceExhausted" in msg

# ── OpenAI ────────────────────────────────────────────────────────────────────
def query_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ── Groq / Llama ──────────────────────────────────────────────────────────────
def query_groq(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ── Gemini ────────────────────────────────────────────────────────────────────
@retry(
    retry=retry_if_exception(_is_rpm_rate_limit),
    wait=wait_exponential(multiplier=2, min=10, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _gemini_call(client, prompt: str) -> str:
    """RPM limitlerinde exponential backoff ile tekrar dener.
    Günlük kota dolduğunda GeminiDailyQuotaExceeded fırlatır (retry olmaz)."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text.strip()
    except Exception as exc:
        msg = str(exc)
        if "PerDay" in msg or "PerDayPer" in msg or "daily" in msg.lower():
            raise GeminiDailyQuotaExceeded(
                "Gemini günlük kota doldu — yarın tekrar deneyin."
            ) from exc
        if _is_rpm_rate_limit(exc):
            print(f"\n⏳ Gemini RPM limit — tenacity yeniden deneyecek...")
            raise
        raise


def query_gemini(prompt: str) -> str:
    from google import genai
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _gemini_call(client, prompt)


# ── Mistral ───────────────────────────────────────────────────────────────────
def query_mistral(prompt: str) -> str:
    from mistralai import Mistral
    client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0
    )
    return response.choices[0].message.content.strip()


# ── Model registry ────────────────────────────────────────────────────────────
MODELS = {
    "gpt-4o-mini": query_openai,
    "llama-3.1":   query_groq,
    "gemini-2.5-flash-lite": query_gemini,
    "mistral-small": query_mistral,
}