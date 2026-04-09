"""
Hallucination detection sonuçlarını analiz eder.
API hatalarını (SKIPPED) dışarıda bırakarak doğru oranları hesaplar.
"""

import json
import glob
import os
from collections import defaultdict


def load_detection_files(results_dir: str = "results") -> dict:
    """Her model+prompt_type için en son detection dosyasını yükler."""
    pattern = os.path.join(results_dir, "*_detection.json")
    files = sorted(glob.glob(pattern))

    # Model+prompt_type başına en son dosyayı seç
    latest = {}
    for f in files:
        base = os.path.basename(f)
        # Örnek: gemini-2.5-flash-lite_few_shot_20260406_172400_detection.json
        parts = base.replace("_detection.json", "").rsplit("_", 2)
        if len(parts) < 3:
            continue
        key = "_".join(parts[:-2])  # model_prompttype
        latest[key] = f  # sorted olduğu için son olan kazanır

    return latest


def analyze(results_dir: str = "results"):
    files = load_detection_files(results_dir)

    if not files:
        print("Hiç detection dosyası bulunamadı.")
        return

    # Model → prompt_type → stats
    stats = defaultdict(dict)

    for key, filepath in sorted(files.items()):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            continue

        model       = data[0]["model"]
        prompt_type = data[0]["prompt_type"]

        total      = len(data)
        skipped    = sum(1 for r in data if r.get("final_verdict") == "SKIPPED"
                         or r.get("status") == "error")
        valid      = total - skipped
        halluc     = sum(1 for r in data if r.get("is_hallucination") is True
                         and r.get("status") != "error")
        correct    = sum(1 for r in data if r.get("final_verdict") == "CORRECT")
        rate       = (halluc / valid * 100) if valid > 0 else None

        stats[model][prompt_type] = {
            "total": total,
            "skipped": skipped,
            "valid": valid,
            "hallucinations": halluc,
            "correct": correct,
            "rate": rate,
        }

    # ── Özet Tablo ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  Hallucination Detection — Düzeltilmiş Sonuçlar")
    print("=" * 70)
    print(f"{'Model':<25} {'Prompt':<12} {'Geçerli':>8} {'Hata':>6} {'Hall.':>6} {'Oran':>8}")
    print("-" * 70)

    for model in sorted(stats):
        for prompt_type in ["zero_shot", "few_shot"]:
            if prompt_type not in stats[model]:
                continue
            s = stats[model][prompt_type]
            rate_str = f"{s['rate']:.1f}%" if s["rate"] is not None else "N/A"
            print(
                f"{model:<25} {prompt_type:<12} "
                f"{s['valid']:>8} {s['skipped']:>6} {s['hallucinations']:>6} {rate_str:>8}"
            )

    print("=" * 70)
    print("\nNot: 'Oran' = Hallucination / Geçerli yanıt sayısı (hatalar hariç)\n")

    # ── Kategoriye göre özet (isteğe bağlı) ─────────────────────────────────
    print_category_breakdown(files)


def print_category_breakdown(files: dict):
    # Tüm detection sonuçlarını birleştir (model+prompt bazında)
    category_stats = defaultdict(lambda: defaultdict(lambda: {"valid": 0, "halluc": 0}))

    for key, filepath in files.items():
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for r in data:
            if r.get("final_verdict") == "SKIPPED" or r.get("status") == "error":
                continue
            cat = r.get("category", "unknown")
            model = r.get("model", "unknown")
            category_stats[cat][model]["valid"] += 1
            if r.get("is_hallucination"):
                category_stats[cat][model]["halluc"] += 1

    if not category_stats:
        return

    print("Kategori Bazında Hallucination Oranları (tüm modeller ortalaması):")
    print("-" * 50)
    for cat in sorted(category_stats):
        total_valid = sum(v["valid"] for v in category_stats[cat].values())
        total_halluc = sum(v["halluc"] for v in category_stats[cat].values())
        rate = (total_halluc / total_valid * 100) if total_valid > 0 else 0
        print(f"  {cat:<30} {rate:5.1f}%  ({total_halluc}/{total_valid})")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()
    analyze(args.results_dir)
