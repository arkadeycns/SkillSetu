# import sys
# from pathlib import Path

# # Allow importing from AI_Service
# AI_SERVICE_PATH = Path(__file__).resolve().parents[2] / "AI_Service"
# sys.path.append(str(AI_SERVICE_PATH))

# from src.rag.retriever import retrieve_sops


# def rag_query(question: str):
#     """
#     Retrieve SOP context using RAG
#     """

#     try:
#         # retrieve context from vector DB
#         context_chunks = retrieve_sops(question, top_k=4)

#         if not context_chunks:
#             return "No relevant SOP information found."

#         # merge chunks
#         context = "\n\n".join(context_chunks)

#         answer = f"""
# Based on the SOP knowledge base:

# {context}

# User Question:
# {question}
# """

#         return answer.strip()

#     except Exception as e:
#         return f"RAG pipeline failed: {str(e)}"


import sys
import os
from pathlib import Path
from groq import Groq

# Allow importing from AI_Service
AI_SERVICE_PATH = Path(__file__).resolve().parents[2] / "AI_Service"
sys.path.append(str(AI_SERVICE_PATH))

from src.rag.retriever import retrieve_sops

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def rag_query(user_answer: str):
    """
    Retrieves SOP context and uses Groq Llama to grade the worker's response.
    """
    try:
        # retrieve the official textbook answers from Pinecone
        context_chunks = retrieve_sops(user_answer, top_k=4)
        
        if not context_chunks:
            context = "General safety guidelines apply."
        else:
            context = "\n\n".join(context_chunks)

        # Build the Persona and the Rubric
        system_prompt = f"""
        You are an expert AI vocational examiner assessing blue-collar workers (plumbers, electricians, carpenters).
        Your job is to evaluate the user's answer against the Official Standard Operating Procedures (SOPs) provided below.
        
        OFFICIAL SOPs:
        {context}

        RULES FOR YOUR RESPONSE:
        1. Keep it highly conversational, encouraging, and SHORT (maximum 2 to 3 sentences).
        2. Validate what they got right first.
        3. Gently correct them if they missed a critical safety step or technical detail from the SOPs.
        4. NEVER say "Based on the SOPs" or read the SOPs mechanically. Talk like a human mentor.
        """

        # Call the Brain Groq Llama
        completion = client.chat.completions.create(
            model="llama3-8b-8192", # Blazing fast inference for voice apps
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_answer}
            ],
            temperature=0.3, # Low temperature so it doesn't hallucinate fake safety rules
            max_tokens=150
        )

        # Return ONLY the AI's conversational feedback
        ai_feedback = completion.choices[0].message.content.strip()
        return ai_feedback

    except Exception as e:
        print(f"RAG Error: {e}")
        return "Sorry, I am having trouble accessing the assessment guidelines right now."
