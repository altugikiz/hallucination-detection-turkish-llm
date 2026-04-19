# Hallucination Detection in Turkish LLMs

A benchmark study measuring hallucination rates of four large language models on Turkish-language factual questions, using a dual-method detection pipeline (LLM-as-judge + Wikipedia fact-check).

---

## Overview

This project evaluates how often GPT-4o-mini, Llama 3.1, Gemini 2.5 Flash Lite, and Mistral Small hallucinate when answering Turkish factual questions under zero-shot and few-shot prompting conditions.

**Why Turkish?** Turkish is a morphologically rich, low-resource language relative to English. LLMs trained predominantly on English data may struggle with Turkish-specific facts (history, law, geography), making hallucination a more significant concern for real-world Turkish NLP applications.

**Detection method:** Each model response is evaluated by two independent signals:
1. **LLM-as-judge** — GPT-4o-mini compares the response against the ground-truth answer.
2. **Wikipedia fact-check** — Keywords are extracted from the question, Turkish Wikipedia is queried, and GPT-4o-mini assesses factual consistency.

A response is labeled `HALLUCINATION` if either signal flags it as incorrect (with the Wikipedia signal able to override an incorrect judge verdict).

---

## Project Structure

```
hallucination-detection-turkish-llm/
├── data/
│   ├── benchmark.json          # Merged benchmark (150 questions, all categories)
│   ├── pilot_benchmark.json    # 10-question pilot for quick testing
│   ├── turkish_history.json    # 35 questions — Ottoman & Republican history
│   ├── geography.json          # 30 questions — Turkish geography
│   ├── science.json            # 25 questions — Science & technology
│   ├── law.json                # 25 questions — Turkish constitution & law
│   ├── popular_culture.json    # 35 questions — Cinema, music, sports
│   └── BENCHMARK.md            # Benchmark documentation and design rationale
├── src/
│   ├── models/
│   │   ├── models.py           # LLM query functions (OpenAI, Groq, Gemini, Mistral)
│   │   └── prompts.py          # Zero-shot and few-shot prompt templates
│   ├── pipeline/
│   │   ├── evaluate.py         # Stage 1: query LLMs, save responses
│   │   ├── detect.py           # Stage 2: run hallucination detection
│   │   └── analyze_results.py  # Summary tables (pipeline-level)
│   ├── utils/
│   │   ├── judge.py            # LLM-as-judge utility
│   │   ├── wiki_check.py       # Wikipedia fact-check utility
│   │   └── utils.py            # Benchmark loading, result saving, progress bar
│   ├── analyze_results.py      # Full analysis with plots and McNemar tests
│   └── test_apis.py            # Verify all four API keys work
├── merge_benchmark.py          # Merge category JSON files into benchmark.json
├── requirements.txt
└── .env.example
```

---

## Setup

**Prerequisites:** Python 3.10+

```bash
# 1. Clone the repository
git clone https://github.com/your-username/hallucination-detection-turkish-llm.git
cd hallucination-detection-turkish-llm

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env and fill in your four API keys
```

Your `.env` file should look like:

```
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
MISTRAL_API_KEY=...
```

**Verify your keys work:**

```bash
python src/test_apis.py
```

---

## Running the Pipeline

### Step 1 — Evaluate: query a model against the benchmark

```bash
python -m src.pipeline.evaluate --model gpt-4o-mini --prompt_type zero_shot
```

Available options:

| Flag | Values | Default |
|------|--------|---------|
| `--model` | `gpt-4o-mini`, `llama-3.1`, `gemini-2.5-flash-lite`, `mistral-small` | required |
| `--prompt_type` | `zero_shot`, `few_shot` | required |
| `--limit` | integer | all 150 questions |
| `--resume` | flag | off |

Output: `results/{model}_{prompt_type}_{timestamp}.json`

**Quick test with 10 questions:**

```bash
python -m src.pipeline.evaluate --model gpt-4o-mini --prompt_type zero_shot --limit 10
```

**Resume a previously interrupted run:**

```bash
python -m src.pipeline.evaluate --model gpt-4o-mini --prompt_type zero_shot --resume
```

---

### Step 2 — Detect: run hallucination detection on evaluation results

```bash
python -m src.pipeline.detect --file results/gpt-4o-mini_zero_shot_20240101_120000.json
```

Available options:

| Flag | Description |
|------|-------------|
| `--file` | Path to an evaluation JSON file from Step 1 (required) |
| `--limit` | Limit to first N questions |

Output: `results/{model}_{prompt_type}_{timestamp}_detection.json`

Each result gains additional fields:
- `judge_verdict` / `judge_is_correct` — LLM-as-judge output
- `wiki_verdict` / `wiki_is_correct` / `wiki_content_found` — Wikipedia check output
- `final_verdict` / `is_hallucination` — combined verdict

---

### Step 3 — Analyze: generate plots and statistics

```bash
python src/analyze_results.py
```

This loads all `*_detection.json` files in `results/` and produces:

- **Console tables** — hallucination rates by model, prompt type, category, and difficulty
- **Bar chart** — model × prompt type comparison (`results/plots/hallucination_bar_chart.png`)
- **Heatmap** — model × category rates for zero-shot (`results/plots/category_heatmap.png`)
- **Category breakdown** — aggregated category rates (`results/plots/category_breakdown.png`)
- **Difficulty breakdown** — easy / medium / hard rates (`results/plots/difficulty_breakdown.png`)
- **McNemar tests** — statistical significance of zero-shot vs. few-shot and between model pairs

For a quick summary without plots:

```bash
python -m src.pipeline.analyze_results
```

---

## Models Evaluated

| Model | Provider | API Key |
|-------|----------|---------|
| GPT-4o-mini | OpenAI | `OPENAI_API_KEY` |
| Llama 3.1 8B Instant | Groq | `GROQ_API_KEY` |
| Gemini 2.5 Flash Lite | Google | `GOOGLE_API_KEY` |
| Mistral Small | Mistral AI | `MISTRAL_API_KEY` |

**Note on rate limits:** Gemini's free tier allows ~10 requests/minute. The pipeline automatically applies a 6-second delay between Gemini calls and uses exponential backoff (up to 5 retries) for rate-limit errors. If the daily quota is reached, the run stops gracefully and saves results collected so far.

---

## Benchmark

150 factual questions in Turkish across 5 knowledge domains:

| Domain | Questions | Difficulty focus |
|--------|-----------|-----------------|
| Turkish History | 35 | Medium–Hard |
| Geography | 30 | Easy–Medium |
| Science & Technology | 25 | Medium |
| Law | 25 | Hard |
| Popular Culture | 35 | Easy–Medium |

All questions have a `correct_answer` (ground truth) and a `source` URL (Turkish Wikipedia or official government sites). See [data/BENCHMARK.md](data/BENCHMARK.md) for detailed domain descriptions, the difficulty rubric, and example entries.

---

## Output Files

| File pattern | Contents |
|---|---|
| `results/{model}_{prompt}_*.json` | Raw model responses from Stage 1 |
| `results/{model}_{prompt}_*_detection.json` | Responses with judge + wiki + final verdicts |
| `results/plots/*.png` | Analysis plots |
| `results/sample_results.json` | Example detection output (committed for reference) |
