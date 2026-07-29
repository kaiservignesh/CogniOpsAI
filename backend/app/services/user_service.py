from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User


def get_all_users(db: Session):
    return db.query(User).all()


# def create_user(db, user):
#     db_user = User(
#         username=user.username,
#         email=user.email,
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

def create_user(db: Session, user):
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    db_user = User(
        username=user.username,
        email=user.email,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

def update_user(db: Session, user_id: int, user):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db_user.username = user.username
    db_user.email = user.email

    db.commit()
    db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}