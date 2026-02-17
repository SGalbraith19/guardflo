from api import router


@router.get("/support/audit")
def get_audit():
   with open("support_ai/logs/support.log") as f:
       return f.readlines()
   