# src/engine/counter_generator.py

from groq import Groq
from src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def _generate(prompt: str) -> str:
    """Internal helper to call Groq LLM."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def generate_counter_questions(
    primary_question,
    user_answer_en,
    identified_gaps,
    sop_context,
    count=2,
    previous_questions=None
):
    """
    Generate follow-up counter questions using Groq LLM.
    """

    if previous_questions is None:
        previous_questions = []

    prompt = f"""
You are an expert vocational skills assessor.

Primary question asked:
{primary_question}

Candidate answer:
{user_answer_en}

Identified skill gaps:
{identified_gaps}

Relevant SOP context:
{sop_context}

Previously asked follow-up questions:
{previous_questions}

Generate {count} follow-up interview questions that test the candidate's
understanding and fill the skill gaps.

Return ONLY the questions, each on a new line.
"""

    response = _generate(prompt)

    questions = [q.strip() for q in response.split("\n") if q.strip()]

    return questions[:count]
