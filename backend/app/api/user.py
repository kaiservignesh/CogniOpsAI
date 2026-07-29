from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.user_service import get_all_users
from app.schemas.user import UserResponse
from app.services.user_service import get_user_by_id
from app.schemas.user import UserUpdate
from app.services.user_service import update_user
from app.services.user_service import delete_user


from app.schemas.user import UserCreate
from app.services.user_service import create_user
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def get_users(db: Session = Depends(get_db)):
    return get_all_users(db)

#@router.post("/")
@router.post("/", response_model=UserResponse)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_user_by_id(db, user_id)

@router.put("/{user_id}", response_model=UserResponse)
def edit_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    return update_user(db, user_id, user)

@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return delete_user(db, user_id)