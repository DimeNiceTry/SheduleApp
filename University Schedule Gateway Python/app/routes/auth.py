from fastapi import APIRouter, HTTPException, Response, status

from ..auth.security import create_access_token, hash_password, verify_password
from ..db.repository import UserRepository
from ..models.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="", tags=["auth"])
_users = UserRepository()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest) -> dict[str, str]:
    existing = _users.get_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    _users.create(payload.name, hash_password(payload.password))
    return {"status": "ok"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response) -> TokenResponse:
    user = _users.get_by_name(payload.name)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user["id"]))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return TokenResponse(access_token=token)
