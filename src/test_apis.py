import os
from dotenv import load_dotenv

load_dotenv()

TEST_PROMPT = "Türkiye'nin başkenti neresidir? Tek cümleyle cevapla."

# ── 1. OpenAI ──────────────────────────────────────────────────────────────
def test_openai():
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=50
        )
        print(f"✅ OpenAI      → {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ OpenAI      → HATA: {e}")


# ── 2. Groq (Llama 3.1) ───────────────────────────────────────────────────
def test_groq():
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=50
        )
        print(f"✅ Groq/Llama  → {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ Groq/Llama  → HATA: {e}")


# ── 3. Google Gemini (yeni google-genai SDK) ───────────────────────────────
def test_gemini():
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=TEST_PROMPT
        )
        print(f"✅ Gemini      → {response.text.strip()}")
    except Exception as e:
        print(f"❌ Gemini      → HATA: {e}")


# ── 4. Mistral ─────────────────────────────────────────────────────────────
def test_mistral():
    try:
        from mistralai import Mistral
        client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=50
        )
        print(f"✅ Mistral     → {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ Mistral     → HATA: {e}")


# ── Çalıştır ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  API Bağlantı Testi — Hallucination Detection Project")
    print("=" * 55)
    test_openai()
    test_groq()
    test_gemini()
    test_mistral()
    print("=" * 55)