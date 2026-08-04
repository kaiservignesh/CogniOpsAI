from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import authenticate_user
from app.database.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),  # noqa: B008
):
    token = authenticate_user(
        db,
        login_data.username,
        login_data.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/token", response_model=TokenResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    token = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }