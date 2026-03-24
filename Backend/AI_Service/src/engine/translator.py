from groq import Groq
from AI_Service.src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def _translate(system_prompt: str, user_text: str) -> str:
    """Helper function to cleanly separate instructions from the payload."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0, # Keep at 0 for strict, deterministic translation
    )
    return response.choices[0].message.content.strip()


def translate_to_english(original_text, source_language):
    """Translates vernacular text to English for the Pinecone/RAG pipeline."""
    
    system_prompt = f"""You are a professional, highly accurate translation API.
    Your ONLY job is to translate the user's text from {source_language} to English.
    
    CRITICAL RULES:
    1. Output STRICTLY the English translation.
    2. Do NOT include any explanations, conversational filler, or preambles (e.g., "Here is the translation:").
    3. If the text contains technical system variables or tags (like USE_QA_FEEDBACK, IS_ABUSIVE, etc.), IGNORE THEM entirely. Only translate the human conversation."""

    return _translate(system_prompt, original_text)


def translate_to_user_language(english_feedback, target_language):
    """Translates English feedback back to the user's language."""
    
    system_prompt = f"""You are a professional, highly accurate translation API.
    Your ONLY job is to translate the English text into {target_language}.
    
    CRITICAL RULES:
    1. Output STRICTLY the {target_language} translation.
    2. Do NOT include any explanations or conversational filler.
    3. The input text may contain backend system flags (e.g., 'USE_QA_FEEDBACK: false', 'IS_ABUSIVE: false', 'IS_RETRY: true'). 
    4. You MUST STRIP OUT all of these system flags. DO NOT translate them and DO NOT include them in your final output. Extract and translate ONLY the actual interview question or feedback meant for the human candidate."""

    return _translate(system_prompt, english_feedback)
