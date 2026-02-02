from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Get availability slots")
async def get_availability():
    """Return available appointment slots (stub)."""
    return {"slots": []}
