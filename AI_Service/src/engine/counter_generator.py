# src/engine/counter_generator.py

from groq import Groq
from src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def _generate(prompt: str) -> str:
    """
    Internal helper to call Groq LLM.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an empathetic vocational interviewer assessing an Indian blue-collar worker (e.g., plumber, electrician, factory worker). Speak in simple language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
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

    Parameters:
    - primary_question: Original question asked
    - user_answer_en: Candidate answer in English
    - identified_gaps: Feedback / gaps identified by RAG
    - sop_context: SOP knowledge context
    - count: number of follow-up questions
    - previous_questions: already asked follow-ups
    """

    if previous_questions is None:
        previous_questions = []

    # Convert gaps into readable text
    if isinstance(identified_gaps, list):
        gaps_text = "\n".join(identified_gaps)
    else:
        gaps_text = str(identified_gaps)

    previous_q_text = "\n".join(previous_questions) if previous_questions else "None"

    prompt = f"""
You are an empathetic vocational interviewer assessing an Indian blue-collar worker (e.g., plumber, electrician, factory worker). You ask simple, practical questions.

Primary question asked:
{primary_question}

Candidate answer:
{user_answer_en}

Identified knowledge or skill gaps:
{gaps_text}

Relevant SOP / domain context:
{sop_context}

Previously asked follow-up questions:
{previous_q_text}

Your task:
Generate {count} intelligent follow-up interview questions.

Rules:
1. Focus on the candidate's weak areas.
2. Ask clarification if the answer was vague.
3. Probe deeper understanding if the answer was partially correct.
4. Avoid repeating previous questions.
5. Keep questions short and natural like a real interviewer.

Return ONLY the questions.
Each question must be on a new line.
"""

    response = _generate(prompt)

    # Clean response
    questions = []

    for line in response.split("\n"):
        q = line.strip()

        if not q:
            continue

        # Remove numbering if LLM adds it
        if q[0].isdigit():
            q = q.split(".", 1)[-1].strip()

        questions.append(q)

    return questions[:count]
