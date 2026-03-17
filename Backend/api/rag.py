from fastapi import APIRouter
from AI_Service.src.rag.qa import rag_query
from schemas.rag_schemas import RagRequest 

router = APIRouter(prefix="/api/v1")

@router.post("/rag")
def rag(request: RagRequest):

    answer = rag_query(request.question, request.user_answer)

    return {
        "answer": answer
    }