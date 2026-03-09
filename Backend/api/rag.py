from fastapi import APIRouter
from services.rag_service import rag_query

router = APIRouter()

@router.post("/rag")
def rag(question: str):

    answer = rag_query(question)

    return {
        "answer": answer
    }