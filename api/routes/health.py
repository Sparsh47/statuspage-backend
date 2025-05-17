from fastapi import APIRouter

router = APIRouter(
    prefix="/healthz",
    tags=["health"]
)

@router.get("/")
def healthCheck():
    return {"message": "Backend is working just fine"}