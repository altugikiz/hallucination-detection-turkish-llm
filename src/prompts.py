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
    return f"""Aşağıdaki soruyu kısa ve net bir şekilde Türkçe olarak yanıtla.
Eğer cevabı bilmiyorsan, tahmin etmeye çalış.

Soru: {question}
Cevap:"""


def few_shot_prompt(question: str) -> str:
    examples = ""
    for ex in FEW_SHOT_EXAMPLES:
        examples += f"Soru: {ex['question']}\nCevap: {ex['answer']}\n\n"

    return f"""Aşağıdaki örneklere bakarak soruyu kısa ve net bir şekilde Türkçe olarak yanıtla.

{examples}Soru: {question}
Cevap:"""