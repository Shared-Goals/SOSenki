"""MiniApp authentication routes (Telegram Mini App initData verification)."""

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/miniapp", tags=["miniapp"])


@router.post("/auth")
async def miniapp_auth(init_data: str):
    """
    Authenticate a Telegram Mini App user via initData.
    
    ## Implementation TODO
    - Accept POST /miniapp/auth with initData in request body or header
    - Call telegram_auth_service.verify_initdata(init_data)
    - Check if user exists in database (by telegram_id)
      - If linked: return { "linked": True, "user": {...} }
      - If unlinked: return { "linked": False, "request_form": {...} }
    - Return 401 on invalid/expired initData
    
    ## OpenAPI Reference
    See specs/001-seamless-telegram-auth/contracts/openapi.yaml POST /miniapp/auth
    """
    # TODO: implement verify_initdata call
    # TODO: implement user lookup logic
    # TODO: implement response schema matching OpenAPI contract
    raise HTTPException(status_code=501, detail="Not yet implemented")
