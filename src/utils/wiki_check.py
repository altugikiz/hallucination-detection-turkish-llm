import re
import os
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    language="tr",
    user_agent="hallucination-detection-turkish-llm/1.0"
)

WIKI_JUDGE_PROMPT = """You are a factual accuracy evaluator. Below is a question, a model's response, and relevant content retrieved from Wikipedia.
Based on the Wikipedia content, evaluate whether the model's response is factually correct.

Question: {question}
Model Response: {model_response}
Wikipedia Content: {wiki_content}

Evaluation rules:
- If the Wikipedia content supports the model's response, write CORRECT.
- If the Wikipedia content contradicts the model's response, write INCORRECT.
- If the Wikipedia content does not contain relevant information, write UNCERTAIN.
- Write only CORRECT, INCORRECT, or UNCERTAIN, nothing else.

Verdict:"""


def extract_keywords(text: str) -> list:
    words = re.findall(r'\b[A-ZÇĞİÖŞÜ][a-zçğışöüA-ZÇĞİÖŞÜ]+\b|\b\d{4}\b', text)
    seen = []
    for w in words:
        if w not in seen:
            seen.append(w)
    return seen[:3]


def search_wikipedia(query: str) -> str:
    page = wiki.page(query)
    if page.exists():
        return page.summary[:500]
    return ""


def wiki_fact_check(question: str, model_response: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    keywords = extract_keywords(question)
    wiki_content = ""

    for keyword in keywords:
        content = search_wikipedia(keyword)
        if content:
            wiki_content = content
            break

    if not wiki_content:
        return {
            "wiki_verdict": "UNCERTAIN",
            "wiki_is_correct": None,
            "wiki_content_found": False,
            "wiki_status": "no_content"
        }

    prompt = WIKI_JUDGE_PROMPT.format(
        question=question,
        model_response=model_response,
        wiki_content=wiki_content
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        verdict = response.choices[0].message.content.strip().upper()

        if "CORRECT" in verdict and "INCORRECT" not in verdict:
            is_correct = True
            final_verdict = "CORRECT"
        elif "INCORRECT" in verdict:
            is_correct = False
            final_verdict = "INCORRECT"
        else:
            is_correct = None
            final_verdict = "UNCERTAIN"

        return {
            "wiki_verdict": final_verdict,
            "wiki_is_correct": is_correct,
            "wiki_content_found": True,
            "wiki_status": "success"
        }
    except Exception as e:
        return {
            "wiki_verdict": "ERROR",
            "wiki_is_correct": None,
            "wiki_content_found": True,
            "wiki_status": f"error: {str(e)}"
        }