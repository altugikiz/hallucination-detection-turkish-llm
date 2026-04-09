import json
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy.stats import chi2_contingency
from statsmodels.stats.contingency_tables import mcnemar

# ── Config ────────────────────────────────────────────────────────────────────
RESULTS_DIR = "results"
PLOTS_DIR   = "results/plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

MODELS = ["gpt-4o-mini", "llama-3.1", "gemini-2.5-flash-lite", "mistral-small"]
PROMPT_TYPES = ["zero_shot", "few_shot"]
CATEGORIES = ["turkish_history", "geography", "science", "law", "popular_culture"]

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["figure.dpi"]  = 150


# ── Data loading ──────────────────────────────────────────────────────────────
def load_detection_results():
    all_data = {}
    for model in MODELS:
        for prompt in PROMPT_TYPES:
            pattern = os.path.join(RESULTS_DIR, f"{model}_{prompt}_*_detection.json")
            files   = sorted(glob.glob(pattern))
            if not files:
                print(f"⚠️  Not found: {model} | {prompt}")
                continue
            with open(files[-1], "r", encoding="utf-8") as f:
                data = json.load(f)
            all_data[(model, prompt)] = data
            print(f"✅ Loaded: {model} | {prompt} | {len(data)} questions")
    return all_data


# ── 1. Overall hallucination rates ───────────────────────────────────────────
def compute_overall_rates(all_data):
    rows = []
    for (model, prompt), data in all_data.items():
        total = len(data)
        hall  = sum(1 for r in data if r["is_hallucination"])
        rows.append({
            "model":       model,
            "prompt_type": prompt,
            "total":       total,
            "hallucinations": hall,
            "rate":        round(hall / total * 100, 1)
        })
    df = pd.DataFrame(rows).sort_values(["model", "prompt_type"])
    print("\n📊 Overall Hallucination Rates:")
    print(df.to_string(index=False))
    return df


# ── 2. Bar chart — model × prompt type ───────────────────────────────────────
def plot_bar_chart(df):
    fig, ax = plt.subplots(figsize=(10, 6))

    x       = np.arange(len(MODELS))
    width   = 0.35
    colors  = {"zero_shot": "#4C72B0", "few_shot": "#DD8452"}

    for i, prompt in enumerate(PROMPT_TYPES):
        subset = df[df["prompt_type"] == prompt].set_index("model")
        rates  = [subset.loc[m, "rate"] if m in subset.index else 0 for m in MODELS]
        bars   = ax.bar(x + (i - 0.5) * width, rates, width,
                        label=prompt.replace("_", "-"), color=colors[prompt],
                        edgecolor="white", linewidth=0.8)
        for bar, rate in zip(bars, rates):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                    f"{rate}%", ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Model", fontsize=12)
    ax.set_ylabel("Hallucination Rate (%)", fontsize=12)
    ax.set_title("Hallucination Rate by Model and Prompt Type\n(Turkish LLM Benchmark)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(MODELS, rotation=15, ha="right", fontsize=10)
    ax.set_ylim(0, 75)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, "hallucination_bar_chart.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"\n✅ Saved: {path}")


# ── 3. Category heatmap ───────────────────────────────────────────────────────
def plot_category_heatmap(all_data):
    # Use zero_shot only for heatmap
    matrix = {}
    for model in MODELS:
        key  = (model, "zero_shot")
        data = all_data.get(key, [])
        matrix[model] = {}
        for cat in CATEGORIES:
            subset = [r for r in data if r["category"] == cat]
            if subset:
                rate = sum(1 for r in subset if r["is_hallucination"]) / len(subset) * 100
            else:
                rate = 0.0
            matrix[model][cat] = round(rate, 1)

    df_heat = pd.DataFrame(matrix).T
    df_heat.columns = [c.replace("_", "\n") for c in df_heat.columns]

    fig, ax = plt.subplots(figsize=(11, 5))
    sns.heatmap(df_heat, annot=True, fmt=".1f", cmap="RdYlGn_r",
                linewidths=0.5, linecolor="white",
                cbar_kws={"label": "Hallucination Rate (%)", "shrink": 0.8},
                vmin=0, vmax=80, ax=ax)

    ax.set_title("Hallucination Rate by Model × Category (Zero-shot)\n(Turkish LLM Benchmark)",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Category", fontsize=11)
    ax.set_ylabel("Model", fontsize=11)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9, rotation=0)

    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, "category_heatmap.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {path}")


# ── 4. Category breakdown bar chart ──────────────────────────────────────────
def plot_category_breakdown(all_data):
    cat_rates = {cat: [] for cat in CATEGORIES}

    for cat in CATEGORIES:
        total = hall = 0
        for model in MODELS:
            data = all_data.get((model, "zero_shot"), [])
            for r in data:
                if r["category"] == cat:
                    total += 1
                    if r["is_hallucination"]:
                        hall += 1
        cat_rates[cat] = round(hall / total * 100, 1) if total else 0

    fig, ax = plt.subplots(figsize=(9, 5))
    cats   = [c.replace("_", "\n") for c in CATEGORIES]
    rates  = list(cat_rates.values())
    colors = ["#e74c3c" if r >= 40 else "#f39c12" if r >= 25 else "#2ecc71" for r in rates]

    bars = ax.bar(cats, rates, color=colors, edgecolor="white", linewidth=0.8)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{rate}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xlabel("Category", fontsize=12)
    ax.set_ylabel("Hallucination Rate (%)", fontsize=12)
    ax.set_title("Hallucination Rate by Category (All Models, Zero-shot)",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 75)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    legend = [
        mpatches.Patch(color="#e74c3c", label="High (≥40%)"),
        mpatches.Patch(color="#f39c12", label="Medium (25-40%)"),
        mpatches.Patch(color="#2ecc71", label="Low (<25%)"),
    ]
    ax.legend(handles=legend, fontsize=10)

    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, "category_breakdown.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {path}")


# ── 5. McNemar test ───────────────────────────────────────────────────────────
def run_mcnemar_tests(all_data):
    print("\n📊 McNemar Tests (Zero-shot vs Few-shot per model):")
    print("-" * 55)

    for model in MODELS:
        zs = all_data.get((model, "zero_shot"), [])
        fs = all_data.get((model, "few_shot"),  [])
        if not zs or not fs:
            continue

        zs_map = {r["id"]: r["is_hallucination"] for r in zs}
        fs_map = {r["id"]: r["is_hallucination"] for r in fs}
        ids    = [r["id"] for r in zs if r["id"] in fs_map]

        b = sum(1 for i in ids if zs_map[i] and not fs_map[i])   # ZS wrong, FS right
        c = sum(1 for i in ids if not zs_map[i] and fs_map[i])   # ZS right, FS wrong

        if b + c == 0:
            print(f"{model:30s}: No discordant pairs")
            continue

        table  = np.array([[0, b], [c, 0]])
        result = mcnemar(table, exact=True)
        sig    = "✅ Significant" if result.pvalue < 0.05 else "❌ Not significant"
        print(f"{model:30s}: b={b}, c={c}, p={result.pvalue:.4f}  {sig}")

    print("\n📊 McNemar Tests (Model pairs, Zero-shot):")
    print("-" * 55)

    model_pairs = [
        ("gpt-4o-mini",          "mistral-small"),
        ("gpt-4o-mini",          "llama-3.1"),
        ("mistral-small",        "llama-3.1"),
        ("gemini-2.5-flash-lite","mistral-small"),
    ]

    for m1, m2 in model_pairs:
        d1 = all_data.get((m1, "zero_shot"), [])
        d2 = all_data.get((m2, "zero_shot"), [])
        if not d1 or not d2:
            continue

        d1_map = {r["id"]: r["is_hallucination"] for r in d1}
        d2_map = {r["id"]: r["is_hallucination"] for r in d2}
        ids    = [r["id"] for r in d1 if r["id"] in d2_map]

        b = sum(1 for i in ids if d1_map[i] and not d2_map[i])
        c = sum(1 for i in ids if not d1_map[i] and d2_map[i])

        if b + c == 0:
            print(f"{m1} vs {m2}: No discordant pairs")
            continue

        table  = np.array([[0, b], [c, 0]])
        result = mcnemar(table, exact=True)
        sig    = "✅ Significant" if result.pvalue < 0.05 else "❌ Not significant"
        print(f"{m1:25s} vs {m2:25s}: p={result.pvalue:.4f}  {sig}")


# ── 6. Difficulty breakdown ───────────────────────────────────────────────────
def plot_difficulty_breakdown(all_data):
    difficulties = ["easy", "medium", "hard"]
    diff_rates   = {}

    for diff in difficulties:
        total = hall = 0
        for model in MODELS:
            data = all_data.get((model, "zero_shot"), [])
            for r in data:
                if r["difficulty"] == diff:
                    total += 1
                    if r["is_hallucination"]:
                        hall += 1
        diff_rates[diff] = round(hall / total * 100, 1) if total else 0

    fig, ax = plt.subplots(figsize=(7, 5))
    colors  = ["#2ecc71", "#f39c12", "#e74c3c"]
    bars    = ax.bar(difficulties, list(diff_rates.values()),
                     color=colors, edgecolor="white", linewidth=0.8)

    for bar, rate in zip(bars, diff_rates.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{rate}%", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_xlabel("Difficulty", fontsize=12)
    ax.set_ylabel("Hallucination Rate (%)", fontsize=12)
    ax.set_title("Hallucination Rate by Difficulty Level\n(All Models, Zero-shot)",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 75)
    ax.grid(axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, "difficulty_breakdown.png")
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"✅ Saved: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Hallucination Detection — Analysis")
    print("=" * 55)

    all_data = load_detection_results()
    df_rates = compute_overall_rates(all_data)

    print("\n📈 Generating plots...")
    plot_bar_chart(df_rates)
    plot_category_heatmap(all_data)
    plot_category_breakdown(all_data)
    plot_difficulty_breakdown(all_data)
    run_mcnemar_tests(all_data)

    print(f"\n✅ All plots saved to: {PLOTS_DIR}/")