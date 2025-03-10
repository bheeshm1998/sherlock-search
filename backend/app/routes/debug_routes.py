from fastapi import APIRouter

router = APIRouter()

@router.get("/debug")
async def debug_endpoint():
    """
    Simple debug endpoint to check if the service is running
    """
    return {"status": "Service is running"}

