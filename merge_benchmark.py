import json
import os

DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "benchmark.json")

FILES = [
    "turkish_history.json",
    "geography.json",
    "science.json",
    "law.json",
    "popular_culture.json",
]

all_questions = []

for filename in FILES:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        questions = json.load(f)
        all_questions.extend(questions)
    print(f"✅ {filename}: {len(questions)} soru yüklendi")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)

print(f"\n✅ Toplam {len(all_questions)} soru → {OUTPUT_FILE} dosyasına yazıldı")

# Özet istatistikler
categories = {}
difficulties = {}

for q in all_questions:
    cat = q["category"]
    diff = q["difficulty"]
    categories[cat] = categories.get(cat, 0) + 1
    difficulties[diff] = difficulties.get(diff, 0) + 1

print("\n📊 Kategori dağılımı:")
for cat, count in categories.items():
    print(f"  {cat}: {count}")

print("\n📊 Zorluk dağılımı:")
for diff, count in sorted(difficulties.items()):
    print(f"  {diff}: {count}")