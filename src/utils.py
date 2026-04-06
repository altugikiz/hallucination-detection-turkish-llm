import json
import os
from datetime import datetime


def load_benchmark(path: str = "data/benchmark.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_results(results: list, model_name: str, prompt_type: str):
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/{model_name}_{prompt_type}_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Sonuçlar kaydedildi: {filename}")
    return filename


def print_progress(current: int, total: int, model: str, prompt_type: str):
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\r[{bar}] {current}/{total} — {model} ({prompt_type})", end="", flush=True)