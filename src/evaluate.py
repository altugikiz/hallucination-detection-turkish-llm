import time
import argparse
from models import MODELS
from prompts import zero_shot_prompt, few_shot_prompt
from utils import load_benchmark, save_results, print_progress

PROMPT_TYPES = {
    "zero_shot": zero_shot_prompt,
    "few_shot":  few_shot_prompt,
}

# Rate limit için bekleme süreleri (saniye)
RATE_LIMIT_DELAY = {
    "gpt-4o-mini":          0.5,
    "llama-3.1":            0.3,
    "gemini-2.5-flash-lite": 4.0,   # free tier daha kısıtlı
    "mistral-small":        0.5,
}


def run_evaluation(model_name: str, prompt_type: str, limit: int = None):
    questions = load_benchmark()
    if limit:
        questions = questions[:limit]

    query_fn   = MODELS[model_name]
    prompt_fn  = PROMPT_TYPES[prompt_type]
    delay      = RATE_LIMIT_DELAY.get(model_name, 1.0)

    results = []
    total   = len(questions)

    print(f"\n🚀 {model_name} | {prompt_type} | {total} soru\n")

    for i, item in enumerate(questions, 1):
        print_progress(i, total, model_name, prompt_type)

        prompt = prompt_fn(item["question"])

        try:
            response = query_fn(prompt)
            status   = "success"
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
    filename = save_results(results, model_name, prompt_type)
    return filename


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",       choices=list(MODELS.keys()), required=True)
    parser.add_argument("--prompt_type", choices=list(PROMPT_TYPES.keys()), default="zero_shot")
    parser.add_argument("--limit",       type=int, default=None, help="Test için ilk N soruyu çalıştır")
    args = parser.parse_args()

    run_evaluation(args.model, args.prompt_type, args.limit)