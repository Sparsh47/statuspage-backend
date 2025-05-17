from fastapi import APIRouter, Depends
from core.auth import verify_clerk_token

router = APIRouter()

@router.get("/services")
async def list_services(user=Depends(verify_clerk_token)):
    return {"message": "List of services", "user": user}
