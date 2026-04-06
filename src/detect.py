import json
import time
import argparse
import os
from judge import llm_judge
from wiki_check import wiki_fact_check
from utils import print_progress


def detect_hallucinations(results_file: str, limit: int = None):
    with open(results_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    if limit:
        results = results[:limit]

    total = len(results)
    model_name = results[0]["model"] if results else "unknown"
    prompt_type = results[0]["prompt_type"] if results else "unknown"

    print(f"\n🔍 Detection starting: {model_name} | {prompt_type} | {total} questions\n")

    detection_results = []

    for i, item in enumerate(results, 1):
        print_progress(i, total, model_name, "detection")

        # 1. LLM-as-judge
        judge_result = llm_judge(
            question=item["question"],
            correct_answer=item["correct_answer"],
            model_response=item["model_response"]
        )
        time.sleep(0.5)

        # 2. Wikipedia fact-check
        wiki_result = wiki_fact_check(
            question=item["question"],
            model_response=item["model_response"]
        )
        time.sleep(0.5)

        # 3. Agreement-based final verdict
        # Logic:
        # - Judge INCORRECT → HALLUCINATION (unless wiki explicitly says CORRECT)
        # - Judge CORRECT + Wiki INCORRECT → HALLUCINATION
        # - Judge CORRECT + Wiki CORRECT/UNCERTAIN → CORRECT
        judge_wrong = judge_result["judge_verdict"] == "INCORRECT"
        wiki_wrong  = wiki_result["wiki_verdict"] == "INCORRECT"
        wiki_correct = wiki_result["wiki_verdict"] == "CORRECT"

        if judge_wrong and wiki_correct:
            # Wiki overrides judge — trust wiki
            final_verdict = "CORRECT"
        elif judge_wrong:
            final_verdict = "HALLUCINATION"
        elif wiki_wrong:
            final_verdict = "HALLUCINATION"
        else:
            final_verdict = "CORRECT"

        detection_results.append({
            **item,
            **judge_result,
            **wiki_result,
            "final_verdict": final_verdict,
            "is_hallucination": final_verdict == "HALLUCINATION"
        })

    print()

    base_name = os.path.basename(results_file).replace(".json", "")
    output_file = f"results/{base_name}_detection.json"
    os.makedirs("results", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(detection_results, f, ensure_ascii=False, indent=2)

    total_count         = len(detection_results)
    hallucination_count = sum(1 for r in detection_results if r["is_hallucination"])
    hallucination_rate  = hallucination_count / total_count * 100

    print(f"\n📊 {model_name} | {prompt_type}")
    print(f"   Total questions    : {total_count}")
    print(f"   Hallucinations     : {hallucination_count}")
    print(f"   Hallucination rate : {hallucination_rate:.1f}%")
    print(f"   💾 Saved to        : {output_file}")

    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file",  required=True, help="JSON file in results/ folder")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    detect_hallucinations(args.file, args.limit)