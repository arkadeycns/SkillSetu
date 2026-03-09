from fastapi import APIRouter
from services.heatmap_service import get_heatmap_data

router = APIRouter()

@router.get("/heatmap")
def heatmap():

    data = get_heatmap_data()

    return {
        "regions": data
    }