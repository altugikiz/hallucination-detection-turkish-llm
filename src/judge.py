import os
from dotenv import load_dotenv

load_dotenv()

JUDGE_PROMPT = """You are a factual accuracy evaluator. Below is a question, the correct answer, and a model's response.
Evaluate whether the model's response is factually correct.

Question: {question}
Correct Answer: {correct_answer}
Model Response: {model_response}

Evaluation rules:
- If the model's response contains correct information, write CORRECT.
- If the model's response contains incorrect information, write INCORRECT.
- If the response is partially correct but contains a critical factual error, write INCORRECT.
- Write only CORRECT or INCORRECT, nothing else.

Verdict:"""


def llm_judge(question: str, correct_answer: str, model_response: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = JUDGE_PROMPT.format(
        question=question,
        correct_answer=correct_answer,
        model_response=model_response
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        verdict = response.choices[0].message.content.strip().upper()
        is_correct = "CORRECT" in verdict
        return {
            "judge_verdict": "CORRECT" if is_correct else "INCORRECT",
            "judge_is_correct": is_correct,
            "judge_status": "success"
        }
    except Exception as e:
        return {
            "judge_verdict": "ERROR",
            "judge_is_correct": None,
            "judge_status": f"error: {str(e)}"
        }