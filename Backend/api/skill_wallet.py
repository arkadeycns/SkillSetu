from fastapi import APIRouter
from services.skill_wallet_service import get_skill_wallet

router = APIRouter(prefix="/api/v1")

@router.get("/skill-wallet/{user_id}")
# change int to str as clerk stores id as str not int 
def skill_wallet(user_id: str):

    wallet = get_skill_wallet(user_id)

    return wallet