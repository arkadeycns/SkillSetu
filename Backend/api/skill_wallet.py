from fastapi import APIRouter
from services.skill_wallet_service import get_skill_wallet

router = APIRouter()

@router.get("/skill-wallet/{user_id}")
def skill_wallet(user_id: int):

    wallet = get_skill_wallet(user_id)

    return wallet