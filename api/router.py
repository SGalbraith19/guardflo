from fastapi import APIRouter

router = APIRouter


@router.get("/support/audit")
def get_audit():
   with open("support_ai/logs/support.log") as f:
       return f.readlines()
   