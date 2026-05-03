# Benchmark Documentation

## Overview

The benchmark consists of **150 factual questions** in Turkish, distributed across five knowledge domains. Each question has a verified correct answer and a source URL. All questions were manually curated from Turkish Wikipedia and official Turkish government publications.

| Domain | Questions | Easy | Medium | Hard |
|--------|-----------|------|--------|------|
| Turkish History | 35 | 12 | 15 | 8 |
| Geography | 30 | 12 | 12 | 6 |
| Science & Technology | 25 | 8 | 12 | 5 |
| Law | 25 | 5 | 8 | 12 |
| Popular Culture | 35 | 10 | 17 | 8 |
| **Total** | **150** | **47** | **64** | **39** |

---

## Entry Format

Each entry is a JSON object:

```json
{
  "id": "tr_hist_001",
  "category": "turkish_history",
  "question": "Türkiye Cumhuriyeti hangi yıl kuruldu?",
  "correct_answer": "Türkiye Cumhuriyeti 29 Ekim 1923 tarihinde kuruldu.",
  "source": "https://tr.wikipedia.org/wiki/Türkiye_Cumhuriyeti",
  "difficulty": "easy"
}
```

| Field | Description |
|-------|-------------|
| `id` | Unique identifier with domain prefix (`tr_hist_`, `tr_geo_`, `tr_sci_`, `tr_law_`, `tr_culture_`) |
| `category` | One of the five domain slugs |
| `question` | Factual question in Turkish |
| `correct_answer` | Ground-truth answer in Turkish (typically 1–2 sentences) |
| `source` | URL of the primary source used to verify the answer |
| `difficulty` | `easy`, `medium`, or `hard` (see rubric below) |

---

## Difficulty Rubric

**Easy** — Facts that are broadly known and covered in general education. A Turkish high-school student would be expected to know these. Examples: the founding year of the Republic, the capital city, the longest river, the most popular film series.

**Medium** — Facts that require more specific domain knowledge. The correct answer involves precise names, dates, or figures that go beyond general knowledge. Examples: the name and exact dates of a specific military campaign, the area of a particular lake, a Turkish scientist's century of activity.

**Hard** — Facts that demand precision in specialized domains (law, technical science, lesser-known history). Wrong-by-one errors (wrong article number, wrong decade, wrong title) are common hallucination patterns at this level. Examples: the exact article number of a constitutional provision, the criminal age of responsibility threshold with its exceptions, elevation data for specific peaks.

---

## Domain 1: Turkish History (`turkish_history`) — 35 questions

This domain covers the full span of recorded Turkish history: the Seljuk period, the founding and expansion of the Ottoman Empire, key battles and sieges, the decline of the Ottoman state, the War of Independence (1919–1922), and the establishment and early decades of the Turkish Republic. Questions frequently involve dates, names of rulers and commanders, and the sequence of historical events.

The domain is deliberately demanding because historical facts require exact recall — a model that confuses the year of the conquest of Istanbul (1453) with another Ottoman campaign, or misattributes the Battle of Sakarya, produces a factually wrong answer even if the surrounding narrative sounds plausible. This makes Turkish history a productive domain for detecting confident hallucinations.

**Example entry:**

```json
{
  "id": "tr_hist_002",
  "category": "turkish_history",
  "question": "Kurtuluş Savaşı'nda Türk kuvvetlerinin Yunan kuvvetlerine karşı kazandığı son büyük meydan muharebesi hangisidir?",
  "correct_answer": "Başkomutanlık Meydan Muharebesi (26-30 Ağustos 1922), Türk kuvvetlerinin Yunan kuvvetlerine karşı kazandığı son büyük meydan muharebesidir.",
  "source": "https://tr.wikipedia.org/wiki/Başkomutanlık_Meydan_Muharebesi",
  "difficulty": "medium"
}
```

---

## Domain 2: Geography (`geography`) — 30 questions

This domain covers the physical and political geography of Turkey: rivers, lakes, mountains, coastlines, provinces, and regional characteristics. Questions range from widely known facts (the longest river, the largest lake) to more specific data points (exact lengths, elevations, surface areas, and the locations of lesser-known geographic features).

Geography is well-suited to hallucination testing because LLMs often confuse similar-sounding place names or transpose numeric values — e.g., mixing up the lengths of the Kızılırmak and Fırat rivers, or misidentifying which lake is the largest by surface area vs. volume.

**Example entry:**

```json
{
  "id": "tr_geo_001",
  "category": "geography",
  "question": "Türkiye'nin en uzun nehri hangisidir?",
  "correct_answer": "Türkiye'nin en uzun nehri 1.355 km uzunluğuyla Kızılırmak Nehri'dir.",
  "source": "https://tr.wikipedia.org/wiki/Kızılırmak_Nehri",
  "difficulty": "easy"
}
```

---

## Domain 3: Science & Technology (`science`) — 25 questions

This domain covers historical Turkish contributions to science (mathematicians, astronomers, physicians from the Ottoman and pre-Ottoman periods) and modern Turkish technological achievements (TOGG electric vehicle, space agency TUA, domestic defense projects). Questions test whether models can accurately place people and inventions in time and attribute them correctly.

Modern tech questions (e.g., the full name of TOGG, the year Turkey's space agency was established) are particularly useful for detecting recency-related hallucinations, since training data for recent events is often sparse or contradictory.

**Example entry:**

```json
{
  "id": "tr_sci_002",
  "category": "science",
  "question": "Türkiye'nin ilk yerli ve milli otomobili olan TOGG'un tam açılımı nedir?",
  "correct_answer": "TOGG'un tam açılımı Türkiye'nin Otomobili Girişim Grubu'dur.",
  "source": "https://tr.wikipedia.org/wiki/Togg",
  "difficulty": "easy"
}
```

---

## Domain 4: Law (`law`) — 25 questions

This domain covers the Turkish Constitution, the Turkish Penal Code (TCK), civil law, and procedural rules. Questions ask for specific article numbers, legal thresholds (age of criminal responsibility, statute of limitations periods), and the exact wording of constitutional provisions.

Law is the hardest domain by design. A model that answers "Article 5" instead of "Article 3" for the provision on the official language is producing a hallucination — the answer sounds reasonable and is in the right format, but is factually wrong. This domain generates the most challenging test cases for both LLM-as-judge and Wikipedia fact-check, since legal sources are not always well-indexed on Wikipedia.

**Example entry:**

```json
{
  "id": "tr_law_001",
  "category": "law",
  "question": "Türkiye Cumhuriyeti Anayasası kaçıncı maddesiyle devletin resmi dilini Türkçe olarak belirlemektedir?",
  "correct_answer": "Türkiye Cumhuriyeti Anayasası'nın 3. maddesi devletin resmi dilinin Türkçe olduğunu belirtmektedir.",
  "source": "https://www.anayasa.gov.tr/tr/mevzuat/anayasa/",
  "difficulty": "hard"
}
```

---

## Domain 5: Popular Culture (`popular_culture`) — 35 questions

This domain covers Turkish cinema, music, television, sports, and international cultural events such as Eurovision. Questions test whether models know widely recognized figures, franchise titles, competition results, and milestone dates in Turkish popular culture.

Popular culture questions tend to be easier than the other domains, but they can expose hallucinations in a different way: models sometimes confidently attribute a film, song, or achievement to the wrong person, or fabricate a plausible-sounding Turkish celebrity who does not exist.

**Example entry:**

```json
{
  "id": "tr_culture_002",
  "category": "popular_culture",
  "question": "Türkiye'yi Eurovision'da ilk kez temsil eden sanatçı kimdir?",
  "correct_answer": "Türkiye'yi Eurovision'da ilk kez 1975 yılında Semiha Yankı temsil etmiştir.",
  "source": "https://tr.wikipedia.org/wiki/Türkiye'nin_Eurovision_şarkı_yarışması_tarihi",
  "difficulty": "easy"
}
```

---

## Sources

All answers were verified against primary sources before inclusion:

- **Turkish Wikipedia** (`tr.wikipedia.org`) — primary source for history, geography, science, and culture questions
- **Turkish Constitutional Court** (`anayasa.gov.tr`) — for constitutional law questions
- **Official legislative texts** (`mevzuat.gov.tr`) — for penal and civil code questions

Questions were excluded if the correct answer was disputed across sources, if the Wikipedia article was flagged as unreliable, or if the question could not be answered unambiguously in 1–2 sentences.
