FEW_SHOT_EXAMPLES = [
    {
        "question": "Türkiye Cumhuriyeti hangi yıl kuruldu?",
        "answer": "Türkiye Cumhuriyeti 29 Ekim 1923 tarihinde kuruldu."
    },
    {
        "question": "Türkiye'nin en yüksek dağı hangisidir?",
        "answer": "Türkiye'nin en yüksek dağı 5.137 metre yüksekliğiyle Ağrı Dağı'dır."
    },
    {
        "question": "Aziz Sancar hangi alanda Nobel ödülü kazandı?",
        "answer": "Aziz Sancar, DNA onarım mekanizmaları üzerine yaptığı çalışmalarıyla 2015 yılında Nobel Kimya Ödülü'nü kazandı."
    }
]


def zero_shot_prompt(question: str) -> str:
    return f"""Answer the following question briefly and accurately in Turkish.
If you are unsure, provide your best estimate.

Question: {question}
Answer:"""


def few_shot_prompt(question: str) -> str:
    examples = ""
    for ex in FEW_SHOT_EXAMPLES:
        examples += f"Question: {ex['question']}\nAnswer: {ex['answer']}\n\n"

    return f"""Answer the following question briefly and accurately in Turkish, following the examples below.

{examples}Question: {question}
Answer:"""