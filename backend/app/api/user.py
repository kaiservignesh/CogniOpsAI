from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])


# @router.get("/")
# def get_users(db: Session = Depends(get_db)):
#     return get_all_users(db)

@router.get("/")
def get_users(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return get_all_users(db)

#@router.post("/")
@router.post("/", response_model=UserResponse)
def add_user(user: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    return create_user(db, user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    return get_user_by_id(db, user_id)

@router.put("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)  # noqa: B008
):
    return update_user(db, user_id, user)

@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    return delete_user(db, user_id)