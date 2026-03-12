from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from security.key_registry import rotate_key

router = APIRouter(prefix="/admin", tags=["admin"])


class KeyRotationRequest(BaseModel):
   version: str
   secret: str


@router.post("/rotate-key")
def rotate_key_endpoint(request: KeyRotationRequest):
   try:
       rotate_key(request.version, request.secret)
       return {"status": "rotated", "new_version": request.version}
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))