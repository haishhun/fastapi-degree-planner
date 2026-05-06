from fastapi import APIRouter
from app.database import get_session

router = APIRouter()


@router.get("/")
def get_stats():
    pass
