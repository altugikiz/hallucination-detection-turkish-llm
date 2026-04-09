import json
import time
import argparse
import glob
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.models import MODELS, GeminiDailyQuotaExceeded
from models.prompts import zero_shot_prompt, few_shot_prompt
from utils.utils import load_benchmark, save_results, print_progress

PROMPT_TYPES = {
    "zero_shot": zero_shot_prompt,
    "few_shot":  few_shot_prompt,
}

# Rate limit için bekleme süreleri (saniye)
RATE_LIMIT_DELAY = {
    "gpt-4o-mini":            0.5,
    "llama-3.1":              0.3,
    "gemini-2.5-flash-lite":  6.0,   # free tier: 10 RPM → ~6s güvenli aralık
    "mistral-small":          0.5,
}


def find_resume_file(model_name: str, prompt_type: str) -> str | None:
    """results/ altında aynı model+prompt_type için en son dosyayı döndürür."""
    pattern = f"results/{model_name}_{prompt_type}_*.json"
    # _detection.json dosyalarını hariç tut
    candidates = [f for f in glob.glob(pattern) if "_detection" not in f]
    return max(candidates) if candidates else None


def load_completed_ids(filepath: str) -> dict:
    """Dosyadaki başarılı yanıtların id → result eşlemesini döndürür."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        item["id"]: item
        for item in data
        if item.get("status") == "success"
    }


def run_evaluation(model_name: str, prompt_type: str, limit: int = None, resume: bool = False):
    questions = load_benchmark()
    if limit:
        questions = questions[:limit]

    query_fn  = MODELS[model_name]
    prompt_fn = PROMPT_TYPES[prompt_type]
    delay     = RATE_LIMIT_DELAY.get(model_name, 1.0)

    # ── Resume: daha önce başarıyla tamamlananları yükle ──────────────────────
    completed = {}
    resume_file = None
    if resume:
        resume_file = find_resume_file(model_name, prompt_type)
        if resume_file:
            completed = load_completed_ids(resume_file)
            print(f"▶️  Resume: {resume_file}")
            print(f"   {len(completed)} soru zaten tamamlanmış, atlanacak.\n")
        else:
            print("ℹ️  Resume dosyası bulunamadı, sıfırdan başlıyor.\n")

    total   = len(questions)
    results = []

    print(f"\n🚀 {model_name} | {prompt_type} | {total} soru\n")

    for i, item in enumerate(questions, 1):
        print_progress(i, total, model_name, prompt_type)

        # Daha önce başarıyla tamamlandıysa atla
        if item["id"] in completed:
            results.append(completed[item["id"]])
            continue

        prompt = prompt_fn(item["question"])

        try:
            response = query_fn(prompt)
            status   = "success"
        except GeminiDailyQuotaExceeded as e:
            print(f"\n🚫 {e}")
            print(f"   {i-1} soru tamamlandı, dosya kaydediliyor...")
            # Kalan soruları boş bırak, şimdiye kadar toplananları kaydet
            break
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "rate" in err_str.lower():
                response = "[API_ERROR: RATE_LIMIT]"
            elif "401" in err_str or "403" in err_str or "authentication" in err_str.lower():
                response = "[API_ERROR: AUTH]"
            else:
                response = "[API_ERROR: UNKNOWN]"
            status = "error"

        results.append({
            "id":             item["id"],
            "category":       item["category"],
            "difficulty":     item["difficulty"],
            "question":       item["question"],
            "correct_answer": item["correct_answer"],
            "model_response": response,
            "prompt_type":    prompt_type,
            "model":          model_name,
            "status":         status,
        })

        time.sleep(delay)

    print()  # yeni satır

    # Resume modunda önceki dosyanın üzerine yaz, aksi hâlde yeni dosya oluştur
    if resume and resume_file:
        with open(resume_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        filename = resume_file
        print(f"💾 Güncellendi: {filename}")
    else:
        filename = save_results(results, model_name, prompt_type)

    success_count = sum(1 for r in results if r["status"] == "success")
    error_count   = sum(1 for r in results if r["status"] == "error")
    print(f"   ✅ Başarılı: {success_count} / {total}  |  ❌ Hata: {error_count}")

    return filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",       choices=list(MODELS.keys()), required=True)
    parser.add_argument("--prompt_type", choices=list(PROMPT_TYPES.keys()), default="zero_shot")
    parser.add_argument("--limit",       type=int, default=None, help="Test için ilk N soruyu çalıştır")
    parser.add_argument("--resume",      action="store_true", help="Kaldığı yerden devam et")
    args = parser.parse_args()

    run_evaluation(args.model, args.prompt_type, args.limit, args.resume)
