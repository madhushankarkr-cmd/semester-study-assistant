import sys
import os
import json

sys.path.append(os.path.dirname(__file__))

from rag_pipeline import rag_query


eval_set = [
    {
        "q": "What is CSMA/CD?",
        "reference": "CSMA/CD is a protocol used in Ethernet networks to detect and handle collisions during data transmission."
    },
    {
        "q": "What is a primary key?",
        "reference": "A primary key is a field or combination of fields that uniquely identifies each record in a database table."
    },
    {
        "q": "What is normalization in DBMS?",
        "reference": "Normalization is the process of organizing database tables to reduce redundancy and improve data integrity."
    },
    {
        "q": "What is binary search?",
        "reference": "Binary search is a searching algorithm that repeatedly divides a sorted array into halves to find a target element."
    },
    {
        "q": "What is the pigeonhole principle?",
        "reference": "The pigeonhole principle states that if more objects are placed into fewer containers, at least one container must contain more than one object."
    },
]


def judge_answer(question, reference, generated):
    """
    Uses an LLM to judge the generated answer against
    the reference answer.
    """

    from groq import Groq
    from dotenv import load_dotenv

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    load_dotenv(os.path.join(BASE_DIR, ".env"))

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing.")

    client = Groq(api_key=api_key)

    prompt = f"""
You are evaluating an AI study assistant.

Question:
{question}

Reference answer:
{reference}

Generated answer:
{generated}

Evaluate the generated answer.

Give:
1. Correctness score from 0 to 2
   2 = correct
   1 = partially correct
   0 = incorrect

2. Relevance score from 0 to 2
   2 = directly answers the question
   1 = somewhat relevant
   0 = irrelevant

Return ONLY valid JSON:

{{
    "correctness": 0,
    "relevance": 0
}}
"""

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    text = response.choices[0].message.content.strip()

    # Remove markdown fences if model adds them
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


total_correctness = 0
total_relevance = 0

print("\n===== RAG ANSWER EVALUATION =====\n")

for i, item in enumerate(eval_set, start=1):

    answer, sources, source_type = rag_query(item["q"])

    scores = judge_answer(
        item["q"],
        item["reference"],
        answer
    )

    total_correctness += scores["correctness"]
    total_relevance += scores["relevance"]

    print(f"{i}. {item['q']}")
    print(f"   Source: {source_type}")
    print(f"   Answer: {answer}")
    print(f"   Correctness: {scores['correctness']}/2")
    print(f"   Relevance: {scores['relevance']}/2")
    print()


max_score = len(eval_set) * 2

correctness_score = total_correctness / max_score
relevance_score = total_relevance / max_score

print("===================================")
print(f"Correctness: {total_correctness}/{max_score} = {correctness_score:.2f}")
print(f"Relevance:   {total_relevance}/{max_score} = {relevance_score:.2f}")