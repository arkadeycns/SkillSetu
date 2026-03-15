from pydantic import BaseModel

class RagRequest(BaseModel):
    question: str
    user_answer: str = ""