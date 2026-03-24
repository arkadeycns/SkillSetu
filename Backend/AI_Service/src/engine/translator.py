# src/engine/translator.py

from groq import Groq
from AI_Service.src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def _translate(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def translate_to_english(original_text, source_language):
    """Translates vernacular text to English for the Pinecone/RAG pipeline."""

    prompt = f"""
    Translate the following text from {source_language} to English.
    Only return the translated English sentence.

    Text:
    {original_text}
    """

    return _translate(prompt)


def translate_to_user_language(english_feedback, target_language):
    """Translates English feedback back to the user's language."""

    prompt = f"""
    Translate the following English text into {target_language}.
    Only return the translated sentence.

    Text:
    {english_feedback}
    """

    return _translate(prompt)